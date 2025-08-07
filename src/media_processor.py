import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.file_id import FileId, FileType


class MediaProcessor:
    def __init__(self, domain_prefix: str):
        """
        初始化媒体处理器
        
        :param domain_prefix: 永久域名前缀
        """
        self.domain_prefix = domain_prefix.rstrip('/')
    
    def process_media(self, msg: Message, client: Client) -> Optional[Dict[str, Any]]:
        """
        处理消息中的媒体，生成永久链接信息
        
        :param msg: Telegram 消息对象
        :param client: Pyrogram 客户端
        :return: 媒体信息字典
        """
        media = self._get_media(msg)
        if not media:
            return None
        
        # 获取文件信息
        file_id = media.file_id
        file_ext = self._guess_extension(client, msg)
        
        # 生成永久ID
        permanent_id = self._generate_permanent_id(file_id)
        
        # 构建永久链接
        permanent_url = f"{self.domain_prefix}/{permanent_id}{file_ext}"
        
        # 构建媒体信息
        media_info = {
            "permanent_url": permanent_url,
            "permanent_id": permanent_id,
            "file_id": file_id,
            "file_ext": file_ext,
            "original_name": getattr(media, 'file_name', None),
            "mime_type": getattr(media, 'mime_type', None),
            "file_size": getattr(media, 'file_size', 0),
            "media_type": self._get_media_type(msg),
            "width": getattr(media, 'width', None),
            "height": getattr(media, 'height', None),
            "duration": getattr(media, 'duration', None),
        }
        
        # 处理缩略图
        thumb_info = self._process_thumbnail(msg, client)
        if thumb_info:
            media_info["thumb"] = thumb_info
        
        return media_info
    
    def _get_media(self, msg: Message):
        """获取消息中的媒体对象"""
        media_types = ['photo', 'video', 'audio', 'voice', 'document', 
                      'sticker', 'animation', 'video_note']
        
        for media_type in media_types:
            media = getattr(msg, media_type, None)
            if media:
                return media
        return None
    
    def _generate_permanent_id(self, file_id: str) -> str:
        """
        基于 file_id 生成永久ID
        使用 SHA256 确保唯一性和一致性
        """
        hash_obj = hashlib.sha256(file_id.encode())
        return hash_obj.hexdigest()[:16]  # 取前16位作为永久ID
    
    def _guess_extension(self, client: Client, msg: Message) -> str:
        """推测文件扩展名"""
        media = self._get_media(msg)
        if not media:
            return ""
        
        # 如果有原始文件名，提取扩展名
        if hasattr(media, 'file_name') and media.file_name:
            return Path(media.file_name).suffix
        
        # 根据媒体类型推测扩展名
        try:
            file_id_obj = FileId.decode(media.file_id)
            mime_type = getattr(media, 'mime_type', None)
            return self._guess_ext_by_type(client, file_id_obj.file_type, mime_type)
        except Exception:
            return self._guess_ext_by_media_type(msg)
    
    def _guess_ext_by_type(self, client: Client, file_type: int, mime_type: str) -> str:
        """根据文件类型推测扩展名"""
        guessed = client.guess_extension(mime_type) if mime_type else None
        
        if file_type == FileType.PHOTO:
            return ".jpg"
        elif file_type == FileType.VOICE:
            return guessed or ".ogg"
        elif file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
            return guessed or ".mp4"
        elif file_type == FileType.DOCUMENT:
            return guessed or ".bin"
        elif file_type == FileType.STICKER:
            return guessed or ".webp"
        elif file_type == FileType.AUDIO:
            return guessed or ".mp3"
        else:
            return ".unknown"
    
    def _guess_ext_by_media_type(self, msg: Message) -> str:
        """根据消息媒体类型推测扩展名"""
        if msg.photo:
            return ".jpg"
        elif msg.video:
            return ".mp4"
        elif msg.audio:
            return ".mp3"
        elif msg.voice:
            return ".ogg"
        elif msg.sticker:
            return ".webp"
        elif msg.animation:
            return ".mp4"
        elif msg.video_note:
            return ".mp4"
        else:
            return ".bin"
    
    def _get_media_type(self, msg: Message) -> str:
        """获取媒体类型"""
        if msg.photo:
            return "photo"
        elif msg.video:
            return "video_file"
        elif msg.audio:
            return "audio_file"
        elif msg.voice:
            return "voice_message"
        elif msg.document:
            return "document"
        elif msg.sticker:
            return "sticker"
        elif msg.animation:
            return "animation"
        elif msg.video_note:
            return "video_message"
        return "unknown"
    
    def _process_thumbnail(self, msg: Message, client: Client) -> Optional[Dict[str, Any]]:
        """处理缩略图"""
        media = self._get_media(msg)
        if not media or not hasattr(media, 'thumbs') or not media.thumbs:
            return None
        
        # 选择最大的缩略图
        largest_thumb = max(media.thumbs, key=lambda x: getattr(x, 'file_size', 0))
        
        # 生成缩略图永久链接
        thumb_id = self._generate_permanent_id(largest_thumb.file_id)
        thumb_ext = ".jpg"  # 缩略图通常是 JPEG 格式
        thumb_url = f"{self.domain_prefix}/{thumb_id}_thumb{thumb_ext}"
        
        return {
            "permanent_url": thumb_url,
            "permanent_id": thumb_id,
            "file_id": largest_thumb.file_id,
            "width": getattr(largest_thumb, 'width', None),
            "height": getattr(largest_thumb, 'height', None),
        }
