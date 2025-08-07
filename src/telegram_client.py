import asyncio
from pyrogram import Client
from pyrogram.session import StringSession
from .config import TelegramConfig


class TelegramClientManager:
    def __init__(self, config: TelegramConfig):
        """
        初始化 Telegram 客户端管理器
        
        :param config: Telegram 配置
        """
        self.config = config
        self.client = None
    
    async def initialize(self) -> Client:
        """
        初始化并启动客户端
        
        :return: Pyrogram 客户端
        """
        self.client = Client(
            "telegram_backup",
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            session_string=self.config.session_string
        )
        
        await self.client.start()
        
        # 获取当前用户信息
        me = await self.client.get_me()
        print(f"已登录: {me.first_name} (@{me.username})")
        
        return self.client
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.stop()
            print("已断开连接")
    
    async def test_channel_access(self, channel_id: int) -> bool:
        """
        测试是否可以访问指定频道
        
        :param channel_id: 频道ID
        :return: 是否可以访问
        """
        if not self.client:
            return False
        
        try:
            chat = await self.client.get_chat(channel_id)
            print(f"成功访问频道: {chat.title} (ID: {channel_id})")
            return True
        except Exception as e:
            print(f"无法访问频道 {channel_id}: {e}")
            return False
    
    async def get_channel_info(self, channel_id: int) -> dict:
        """
        获取频道信息
        
        :param channel_id: 频道ID
        :return: 频道信息
        """
        if not self.client:
            return {}
        
        try:
            chat = await self.client.get_chat(channel_id)
            return {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description,
                "members_count": chat.members_count,
                "type": str(chat.type)
            }
        except Exception as e:
            print(f"获取频道信息失败: {e}")
            return {}
