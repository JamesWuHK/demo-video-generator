# 快速开始指南

这个指南将帮助你在 5 分钟内生成第一个演示视频。

## 前置要求

- Python 3.9+
- Docker（可选，用于容器化运行）
- FFmpeg（用于视频处理）

## 方法 1: 使用 Docker（推荐）

### 步骤 1: 构建 Docker 镜像

```bash
git clone https://github.com/JamesWuHK/demo-video-generator.git
cd demo-video-generator
docker-compose up -d
```

### 步骤 2: 通过 API 生成视频

```bash
# 查看 API 服务状态
curl http://localhost:8000/

# 提交视频生成任务
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d @examples/api_request.json

# 查询任务状态（使用返回的 task_id）
curl http://localhost:8000/api/v1/tasks/{task_id}

# 下载生成的视频
curl -O http://localhost:8000/api/v1/tasks/{task_id}/download
```

## 方法 2: 本地安装

### 步骤 1: 安装依赖

```bash
# 克隆项目
git clone https://github.com/JamesWuHK/demo-video-generator.git
cd demo-video-generator

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装项目
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

### 步骤 2: 生成第一个视频

```bash
# 使用示例脚本生成视频
demovideo generate \
  --script examples/demo.yaml \
  --output output/demo.mp4 \
  --headless

# 视频将保存在 output/demo.mp4
# 字幕将保存在 output/demo.srt
```

## 方法 3: 分步执行（了解工作原理）

### 步骤 1: 仅生成音频

```bash
demovideo audio \
  --script examples/demo.yaml \
  --output output/audio/ \
  --voice zh-CN-XiaoxiaoNeural
```

这会生成：
- `output/audio/01_homepage.mp3`
- `output/audio/02_features.mp3`
- ...（每个场景一个音频文件）

### 步骤 2: 仅录制视频

```bash
demovideo record \
  --script examples/demo.yaml \
  --output output/video.webm \
  --headless
```

这会生成：
- `output/video.webm` - 录制的浏览器视频
- `output/timestamps.json` - 时间戳信息

### 步骤 3: 合并音视频

```bash
demovideo merge \
  --video output/video.webm \
  --audio-dir output/audio/ \
  --timestamps output/timestamps.json \
  --output output/final.mp4
```

最终输出：
- `output/final.mp4` - 完整视频
- `output/final.srt` - 字幕文件

## 创建自己的视频脚本

### 基础模板

创建 `my_demo.yaml`:

```yaml
project:
  name: "我的产品演示"
  resolution: [1920, 1080]  # 16:9 高清
  fps: 30
  voice: "zh-CN-XiaoxiaoNeural"  # 中文女声

scenes:
  - id: scene_01
    url: "https://your-website.com"
    narration: "欢迎来到我们的产品。"
    actions:
      - type: scroll
        y: 0
      - type: wait
        duration: 2

  - id: scene_02
    narration: "这是我们的核心功能。"
    actions:
      - type: scroll
        y: 500
        smooth: true
      - type: wait
        duration: 2
```

### 可用的动作类型

```yaml
# 滚动到指定位置
- type: scroll
  y: 500
  smooth: true  # 平滑滚动

# 滚动到包含特定文本的元素
- type: scroll_to_text
  text: "登录"
  offset: 100  # 额外偏移

# 点击元素
- type: click
  selector: "button.login"  # CSS 选择器
  # 或
  text: "登录"  # 按文本查找

# 填写表单
- type: fill
  selector: "input[name='username']"
  value: "demo@example.com"

# 等待
- type: wait
  duration: 2  # 秒

# 导航到新页面
- type: goto
  url: "https://example.com/page2"

# iframe 内滚动
- type: scroll_iframe
  positions: [300, 600, 900]
  interval: 1.5
```

## 查看可用的 TTS 语音

```bash
# 列出所有可用语音
demovideo voices

# 筛选中文语音
demovideo voices --language zh-CN

# 筛选英文语音
demovideo voices --language en-US
```

常用语音：
- `zh-CN-XiaoxiaoNeural` - 中文女声（温柔）
- `zh-CN-YunxiNeural` - 中文男声
- `en-US-JennyNeural` - 英文女声
- `en-US-GuyNeural` - 英文男声

## 故障排查

### 问题 1: Playwright 浏览器未安装

**错误**: `Executable doesn't exist at ...`

**解决**:
```bash
playwright install chromium
playwright install-deps chromium  # Linux 需要额外依赖
```

### 问题 2: FFmpeg 未找到

**错误**: `ffmpeg not found`

**解决**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 下载 https://ffmpeg.org/download.html 并添加到 PATH
```

### 问题 3: 视频和音频不同步

**原因**: 录制过程中网络延迟或页面加载缓慢

**解决**:
- 增加动作间的等待时间
- 使用 `--slow-mo` 参数减慢浏览器操作
- 确保网络连接稳定

### 问题 4: Chrome 扩展无法加载

**解决**: 进入 `chrome://extensions/`，启用"开发者模式"，然后"加载已解压的扩展程序"，选择 `chrome-extension` 目录。

## 高级用法

### 自定义视频质量

```bash
demovideo generate \
  --script demo.yaml \
  --output video.mp4 \
  --resolution 3840x2160 \  # 4K
  --bitrate 16000k          # 高码率
```

### 处理需要登录的网站

1. 使用 Chrome 扩展捕获登录状态
2. 导出 cookies 和 localStorage
3. 在脚本中注入登录信息（需要修改 recorder.py）

### 批量生成多个视频

```bash
# 创建批处理脚本
for script in scripts/*.yaml; do
  demovideo generate \
    --script "$script" \
    --output "output/$(basename $script .yaml).mp4" \
    --headless
done
```

## 下一步

- 查看 [examples/](../examples/) 目录了解更多示例
- 阅读 [API 文档](API.md) 了解如何集成到你的应用
- 加入我们的 [讨论区](https://github.com/JamesWuHK/demo-video-generator/discussions)

## 需要帮助？

- [问题反馈](https://github.com/JamesWuHK/demo-video-generator/issues)
- [讨论区](https://github.com/JamesWuHK/demo-video-generator/discussions)
- 查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何贡献
