# Demo Video Generator

🎬 **AI驱动的产品演示视频自动生成工具**

将分镜脚本自动转换为专业的产品演示视频，支持自动配音、精准同步、字幕生成。

## ✨ 特性

- **分镜脚本驱动** - 使用 YAML/JSON 定义视频分镜
- **自动浏览器录制** - 基于 Playwright 的高清屏幕录制
- **AI 语音合成** - 支持多语言、多音色的 TTS 配音
- **精准声画同步** - 基于时间戳的音视频精确对齐
- **自动字幕生成** - 生成 SRT 格式字幕文件
- **高清输出** - 支持 1080p、4K 分辨率

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/demo-video-generator.git
cd demo-video-generator

# 安装依赖
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

### CLI 使用

```bash
# 从分镜脚本生成视频
demovideo generate --script examples/demo.yaml --output output/demo.mp4

# 仅生成音频
demovideo audio --script examples/demo.yaml --output output/audio/

# 仅录制视频（无配音）
demovideo record --script examples/demo.yaml --output output/video.webm

# 合并已有的视频和音频
demovideo merge --video video.webm --timestamps timestamps.json --audio-dir audio/ --output final.mp4
```

### API 服务

```bash
# 启动 API 服务
demovideo serve --port 8000

# 或使用 Docker
docker-compose up -d
```

## 📝 分镜脚本格式

```yaml
# demo.yaml
project:
  name: "产品演示视频"
  resolution: [1440, 900]
  fps: 30
  voice: "zh-CN-XiaoxiaoNeural"

scenes:
  - id: homepage
    url: "https://example.com/"
    narration: "欢迎来到我们的产品，这是一个创新的解决方案。"
    actions:
      - type: scroll
        y: 0
      - type: wait
        duration: auto  # 自动根据配音时长

  - id: features
    narration: "我们提供六大核心功能，满足您的各种需求。"
    actions:
      - type: scroll
        y: 500
        smooth: true

  - id: demo
    url: "https://example.com/demo"
    narration: "让我们看一个实际的演示。"
    actions:
      - type: click
        selector: "button.start-demo"
      - type: wait
        duration: 2
```

## 🏗️ 项目结构

```
demo-video-generator/
├── src/
│   ├── core/           # 核心引擎
│   │   ├── recorder.py     # 浏览器录制引擎
│   │   ├── tts.py          # 语音合成引擎
│   │   ├── merger.py       # 音视频合并
│   │   └── script.py       # 分镜脚本解析
│   ├── cli/            # 命令行工具
│   │   └── main.py
│   ├── api/            # API 服务
│   │   ├── app.py
│   │   └── routes.py
│   └── utils/          # 工具函数
├── examples/           # 示例脚本
├── docs/               # 文档
└── tests/              # 测试
```

## 🔧 配置

### 环境变量

```bash
# TTS 配置
TTS_VOICE=zh-CN-XiaoxiaoNeural
TTS_RATE=+0%

# 视频配置
VIDEO_RESOLUTION=1440x900
VIDEO_FPS=30
VIDEO_BITRATE=8000k

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
```

## 📖 API 文档

### POST /api/v1/generate

生成演示视频

```json
{
  "script": {
    "project": { "name": "Demo", "resolution": [1440, 900] },
    "scenes": [...]
  },
  "options": {
    "format": "mp4",
    "quality": "high"
  }
}
```

### GET /api/v1/tasks/{task_id}

查询生成任务状态

### GET /api/v1/tasks/{task_id}/download

下载生成的视频

## 🛠️ 技术栈

- **Playwright** - 浏览器自动化和录制
- **Edge TTS** - 微软语音合成
- **MoviePy** - 视频处理和合并
- **FastAPI** - API 服务框架
- **Celery** - 异步任务队列

## 🎯 使用场景

- **产品演示** - 快速制作产品功能演示视频
- **功能发布** - 自动生成新功能介绍视频
- **教程制作** - 批量生成教程视频
- **营销内容** - 规模化生成营销视频
- **变更日志** - 为每个版本生成演示视频

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [文档](docs/)
- [示例脚本](examples/)
- [问题反馈](https://github.com/your-org/demo-video-generator/issues)

---

Made with ❤️ by the Demo Video Generator team
