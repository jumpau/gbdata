#!/usr/bin/env python3
"""
Telegram 备份工具 - 使用永久链接
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config, validate_config
from telegram_client import TelegramClientManager
from media_processor import MediaProcessor
from message_processor import MessageProcessor
from blog_generator import BlogGenerator


async def main():
    """主函数"""
    print("=== Telegram 备份工具 - 永久链接版本 ===\n")
    
    try:
        # 加载配置
        print("加载配置文件...")
        config = load_config()
        
        # 验证配置
        if not validate_config(config):
            print("配置验证失败，请检查配置文件")
            return
        
        print("配置加载成功")
        
        # 初始化组件
        print("\n初始化 Telegram 客户端...")
        client_manager = TelegramClientManager(config.telegram)
        client = await client_manager.initialize()
        
        # 测试频道访问
        print(f"\n测试频道访问...")
        if not await client_manager.test_channel_access(config.export.source_channel):
            print("无法访问目标频道，请检查频道ID和权限")
            await client_manager.disconnect()
            return
        
        # 获取频道信息
        channel_info = await client_manager.get_channel_info(config.export.source_channel)
        if channel_info:
            print(f"频道信息: {channel_info['title']} (@{channel_info.get('username', 'N/A')})")
        
        # 初始化处理器
        media_processor = MediaProcessor(config.export.domain_prefix)
        message_processor = MessageProcessor(client, media_processor)
        blog_generator = BlogGenerator(config.export.output_path, config.rss)
        
        print(f"\n开始处理消息...")
        print(f"消息范围: {config.export.start_id} - {config.export.end_id}")
        print(f"批处理大小: {config.export.batch_size}")
        print(f"输出路径: {config.export.output_path}")
        print(f"域名前缀: {config.export.domain_prefix}")
        
        # 处理消息
        messages = await message_processor.process_messages(
            channel_id=config.export.source_channel,
            start_id=config.export.start_id,
            end_id=config.export.end_id,
            batch_size=config.export.batch_size,
            output_path=config.export.output_path
        )
        
        # 生成输出文件
        print(f"\n生成输出文件...")
        blog_generator.generate_all(messages)
        
        print(f"\n✅ 任务完成!")
        print(f"📁 输出目录: {config.export.output_path}")
        print(f"📊 处理消息数: {len(messages)}")
        
        # 列出生成的文件
        output_path = Path(config.export.output_path)
        generated_files = []
        for file_name in ["posts.json", "index.html", "rss.xml", "atom.xml"]:
            file_path = output_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                generated_files.append(f"  📄 {file_name} ({size} bytes)")
        
        if generated_files:
            print("\n生成的文件:")
            print("\n".join(generated_files))
        
        # 断开连接
        await client_manager.disconnect()
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n程序结束")


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
