import asyncio
import json
from typing import List, Dict, Any, Set
from pathlib import Path
from pyrogram import Client
from pyrogram.types import Message
from .media_processor import MediaProcessor
from .utils import save_json, load_json


class MessageProcessor:
    def __init__(self, client: Client, media_processor: MediaProcessor):
        """
        初始化消息处理器
        
        :param client: Pyrogram 客户端
        :param media_processor: 媒体处理器
        """
        self.client = client
        self.media_processor = media_processor
        self.processed_ids_file = "processed_ids.json"
    
    async def process_messages(
        self, 
        channel_id: int,
        start_id: int,
        end_id: int,
        batch_size: int = 50,
        output_path: str = "./output"
    ) -> List[Dict[str, Any]]:
        """
        处理消息并生成包含永久链接的数据结构
        
        :param channel_id: 频道ID
        :param start_id: 起始消息ID
        :param end_id: 结束消息ID
        :param batch_size: 批处理大小
        :param output_path: 输出路径
        :return: 处理后的消息列表
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        processed_ids = self._load_processed_ids(output_dir)
        messages_data = []
        current_id = start_id
        
        print(f"开始处理消息，范围: {start_id} - {end_id}")
        
        while current_id <= end_id:
            # 生成批次ID列表
            batch_ids = [
                i for i in range(current_id, min(current_id + batch_size, end_id + 1))
                if i not in processed_ids
            ]
            
            if not batch_ids:
                print(f"批次 {current_id}-{min(current_id + batch_size - 1, end_id)} 已全部处理，跳过")
                current_id += batch_size
                continue
            
            try:
                # 获取消息
                print(f"获取消息批次: {batch_ids[0]}-{batch_ids[-1]}")
                messages = await self.client.get_messages(channel_id, ids=batch_ids)
                
                # 处理消息
                for msg in messages:
                    if msg is not None:
                        processed_msg = await self._process_single_message(msg)
                        if processed_msg:
                            messages_data.append(processed_msg)
                            processed_ids.add(msg.id)
                
                # 保存处理记录
                valid_ids = [msg.id for msg in messages if msg is not None]
                self._save_processed_ids(valid_ids, output_dir)
                
                print(f"已处理消息批次: {batch_ids[0]}-{batch_ids[-1]}, 有效消息: {len(valid_ids)}")
                
            except Exception as e:
                print(f"处理批次 {batch_ids} 时出错: {e}")
            
            current_id += batch_size
            await asyncio.sleep(1)  # 避免频率限制
        
        # 按ID排序
        messages_data.sort(key=lambda x: x['id'])
        
        # 处理消息分组和回复关系
        messages_data = self._group_messages(messages_data)
        
        print(f"处理完成，共 {len(messages_data)} 条消息")
        return messages_data
    
    async def _process_single_message(self, msg: Message) -> Dict[str, Any]:
        """处理单条消息"""
        # 基础消息信息
        message_data = {
            "id": msg.id,
            "date": msg.date.isoformat() if msg.date else None,
            "text": msg.text or msg.caption or "",
            "views": getattr(msg, 'views', None),
            "forwards": getattr(msg, 'forwards', None),
            "media_group_id": getattr(msg, 'media_group_id', None),
            "reply_to_message_id": getattr(msg, 'reply_to_message_id', None),
            "author": getattr(msg, 'author_signature', None),
        }
        
        # 处理转发信息
        if msg.forward_from:
            message_data["forwarded_from"] = {
                "name": f"{msg.forward_from.first_name or ''} {msg.forward_from.last_name or ''}".strip(),
                "username": msg.forward_from.username,
                "url": f"https://t.me/{msg.forward_from.username}" if msg.forward_from.username else None,
            }
        elif msg.forward_from_chat:
            message_data["forwarded_from"] = {
                "name": msg.forward_from_chat.title,
                "username": msg.forward_from_chat.username,
                "url": f"https://t.me/{msg.forward_from_chat.username}" if msg.forward_from_chat.username else None,
            }
        elif msg.forward_sender_name:
            message_data["forwarded_from"] = {
                "name": msg.forward_sender_name,
                "username": None,
                "url": None,
            }
        
        # 处理媒体文件
        media_info = self.media_processor.process_media(msg, self.client)
        if media_info:
            message_data["media"] = media_info
        
        return message_data
    
    def _group_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理消息分组和回复关系"""
        # 创建ID映射
        id_map = {msg['id']: msg for msg in messages}
        
        # 处理媒体组
        grouped_messages = {}
        result = []
        
        for msg in messages:
            media_group_id = msg.get('media_group_id')
            
            if media_group_id:
                if media_group_id not in grouped_messages:
                    grouped_messages[media_group_id] = []
                grouped_messages[media_group_id].append(msg)
            else:
                result.append(msg)
        
        # 合并媒体组
        for group_id, group_msgs in grouped_messages.items():
            # 选择主消息（有文本的第一条，或第一条）
            main_msg = None
            for msg in group_msgs:
                if msg.get('text'):
                    main_msg = msg
                    break
            if not main_msg:
                main_msg = group_msgs[0]
            
            # 收集所有媒体
            all_media = []
            for msg in group_msgs:
                if msg.get('media'):
                    all_media.append(msg['media'])
            
            # 设置媒体列表
            if all_media:
                if all_media[0]['media_type'] == 'photo':
                    main_msg['images'] = all_media
                else:
                    main_msg['files'] = all_media
                
                # 移除单个媒体字段
                main_msg.pop('media', None)
            
            result.append(main_msg)
        
        # 处理回复关系
        for msg in result:
            reply_id = msg.get('reply_to_message_id')
            if reply_id and reply_id in id_map:
                reply_msg = id_map[reply_id]
                msg['reply'] = {
                    'id': reply_msg['id'],
                    'text': reply_msg.get('text', '')[:100] + '...' if len(reply_msg.get('text', '')) > 100 else reply_msg.get('text', ''),
                    'thumb': None  # 可以添加缩略图逻辑
                }
            
            # 清理空字段
            msg.pop('reply_to_message_id', None)
        
        return sorted(result, key=lambda x: x['id'])
    
    def _load_processed_ids(self, output_dir: Path) -> Set[int]:
        """加载已处理的消息ID"""
        processed_file = output_dir / self.processed_ids_file
        try:
            data = load_json(processed_file)
            return set(data) if data else set()
        except (FileNotFoundError, json.JSONDecodeError):
            return set()
    
    def _save_processed_ids(self, new_ids: List[int], output_dir: Path):
        """保存新处理的消息ID"""
        processed_file = output_dir / self.processed_ids_file
        existing_ids = self._load_processed_ids(output_dir)
        existing_ids.update(new_ids)
        save_json(processed_file, list(existing_ids))
