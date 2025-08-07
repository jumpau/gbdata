import os
import toml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelegramConfig:
    api_id: int
    api_hash: str
    session_string: str


@dataclass
class ExportConfig:
    source_channel: int
    output_path: str
    domain_prefix: str
    batch_size: int = 50
    start_id: int = 1
    end_id: int = 100000


@dataclass
class RSSConfig:
    title: str
    link: str
    description: str
    language: str
    image_url: str


@dataclass
class Config:
    telegram: TelegramConfig
    export: ExportConfig
    rss: Optional[RSSConfig] = None


def load_config(config_path: str = "config.toml") -> Config:
    """
    加载配置文件
    
    :param config_path: 配置文件路径
    :return: 配置对象
    """
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在，请先复制 config.example.toml 并填写配置")
    
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = toml.load(f)
    
    # 解析配置
    telegram_config = TelegramConfig(**config_data['telegram'])
    export_config = ExportConfig(**config_data['export'])
    rss_config = RSSConfig(**config_data['rss']) if 'rss' in config_data else None
    
    return Config(
        telegram=telegram_config,
        export=export_config,
        rss=rss_config
    )


def validate_config(config: Config) -> bool:
    """
    验证配置是否有效
    
    :param config: 配置对象
    :return: 是否有效
    """
    # 验证 Telegram 配置
    if not config.telegram.api_id or not config.telegram.api_hash:
        print("错误: Telegram API ID 和 API Hash 不能为空")
        return False
    
    if not config.telegram.session_string:
        print("错误: Session String 不能为空")
        return False
    
    # 验证导出配置
    if not config.export.source_channel:
        print("错误: 源频道 ID 不能为空")
        return False
    
    if not config.export.domain_prefix:
        print("错误: 域名前缀不能为空")
        return False
    
    # 创建输出目录
    Path(config.export.output_path).mkdir(parents=True, exist_ok=True)
    
    return True
