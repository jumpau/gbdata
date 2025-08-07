# Telegram 备份工具 - 永久链接版本

基于 `one-among-us/TelegramBackup` 项目的改进版本，主要特点是使用永久外链代替下载文件，节省本地存储空间。

## ✨ 主要特点

- 🚀 **不下载文件**: 只获取文件信息，生成永久外链
- 🔗 **永久链接**: 格式为 `域名前缀/永久ID.文件扩展名`
- 📈 **增量更新**: 支持断点续传，记录已处理的消息ID
- 📋 **完整输出**: 生成 `posts.json`、`index.html`、`rss.xml`、`atom.xml`
- 🎯 **批量处理**: 支持批量获取和处理消息
- 🛡️ **错误处理**: 完整的异常处理和日志记录

## 📁 项目结构

```
telegram-backup-permanent/
├── requirements.txt          # 依赖包
├── config.example.toml      # 配置文件示例
├── README.md               # 说明文档
├── main.py                # 主程序入口
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── telegram_client.py # Telegram客户端
│   ├── media_processor.py # 媒体处理器
│   ├── message_processor.py # 消息处理器
│   ├── blog_generator.py  # 博客生成器
│   └── utils.py           # 工具函数
└── templates/             # 模板目录
    └── tg-blog.html      # 博客模板
```

## 🚀 快速开始

### 1. 环境准备

确保你已安装 Python 3.8 或更高版本。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置设置

复制配置文件模板并填写：

```bash
cp config.example.toml config.toml
```

编辑 `config.toml` 文件：

```toml
[telegram]
api_id = 123456                    # 你的 API ID
api_hash = "your_api_hash_here"    # 你的 API Hash
session_string = "your_session"    # 你的 Session String

[export]
source_channel = -1001234567890    # 源频道ID（负数）
output_path = "./output"           # 输出路径
domain_prefix = "https://cdn.yourdomain.com/tg"  # 永久链接域名前缀
batch_size = 50                    # 批处理大小
start_id = 1                       # 起始消息ID
end_id = 10000                     # 结束消息ID

[rss]                              # RSS配置（可选）
title = "My Telegram Channel"
link = "https://yourdomain.com/blog"
description = "My channel backup"
language = "zh-cn"
image_url = "https://yourdomain.com/avatar.png"
```

### 4. 获取必要凭据

#### 获取 API ID 和 API Hash

1. 访问 https://my.telegram.org/apps
2. 登录你的 Telegram 账号
3. 创建新的应用程序
4. 记录 API ID 和 API Hash

#### 获取 Session String

使用以下脚本生成 Session String：

```python
from pyrogram import Client

api_id = 123456
api_hash = "your_api_hash"

with Client("my_account", api_id, api_hash) as app:
    print(app.export_session_string())
```

#### 获取频道ID

1. 将频道消息转发给 [@RawDataBot](https://t.me/RawDataBot)
2. 在返回的JSON中找到 `forward_from_chat.id` 字段
3. 这个数字就是频道ID（通常是负数）

### 5. 运行程序

```bash
python main.py
```

## 📋 输出文件说明

运行完成后，将在输出目录生成以下文件：

- **`posts.json`** - 包含所有消息数据的JSON文件
- **`index.html`** - 可直接访问的博客页面
- **`rss.xml`** - RSS 订阅源
- **`atom.xml`** - Atom 订阅源
- **`processed_ids.json`** - 已处理的消息ID记录（用于增量更新）

## 🔗 永久链接格式

所有媒体文件使用以下格式的永久链接：

```
https://你的域名前缀/永久ID.文件扩展名
```

其中：
- **永久ID**: 基于文件ID的SHA256哈希（前16位）
- **文件扩展名**: 根据文件类型自动推测

示例：
- 图片: `https://cdn.example.com/tg/a1b2c3d4e5f6g7h8.jpg`
- 视频: `https://cdn.example.com/tg/x9y8z7w6v5u4t3s2.mp4`
- 音频: `https://cdn.example.com/tg/m5n6o7p8q9r0s1t2.mp3`

## ⚙️ 配置说明

### Telegram 配置

| 字段 | 说明 | 必填 |
|-----|------|-----|
| `api_id` | Telegram API ID | ✅ |
| `api_hash` | Telegram API Hash | ✅ |
| `session_string` | 会话字符串 | ✅ |

### 导出配置

| 字段 | 说明 | 默认值 |
|-----|------|-------|
| `source_channel` | 源频道ID | 必填 |
| `output_path` | 输出路径 | `./output` |
| `domain_prefix` | 域名前缀 | 必填 |
| `batch_size` | 批处理大小 | `50` |
| `start_id` | 起始消息ID | `1` |
| `end_id` | 结束消息ID | `100000` |

### RSS 配置（可选）

| 字段 | 说明 |
|-----|------|
| `title` | RSS标题 |
| `link` | RSS链接 |
| `description` | RSS描述 |
| `language` | 语言代码 |
| `image_url` | RSS图标URL |

## 🔄 增量更新

程序支持增量更新：

1. 首次运行会处理指定范围内的所有消息
2. 再次运行时会跳过已处理的消息ID
3. 只处理新增的消息，大大提高效率
4. 处理记录保存在 `processed_ids.json` 文件中

## 🎨 自定义模板

你可以修改 `templates/tg-blog.html` 来自定义博客页面的外观：

- 修改CSS样式
- 调整页面布局
- 添加自定义功能
- 更改颜色主题

## 📱 支持的媒体类型

- 📷 **照片** (.jpg, .png, .webp)
- 🎥 **视频** (.mp4, .mov, .avi)
- 🎵 **音频** (.mp3, .ogg, .m4a)
- 🎤 **语音消息** (.ogg)
- 📄 **文档** (各种格式)
- 🏷️ **贴纸** (.webp, .tgs)
- 🎬 **动画** (.gif, .mp4)
- 💬 **视频消息** (.mp4)

## 🛠️ 故障排除

### 常见问题

**Q: 提示无法访问频道？**
A: 检查频道ID是否正确，确保机器人
