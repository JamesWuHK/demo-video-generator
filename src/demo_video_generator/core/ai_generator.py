"""AI-powered script generator for demo videos.

This module uses LLM to automatically generate demo video scripts
by analyzing website content and structure.
"""

import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright
import anthropic
import os


class WebsiteAnalyzer:
    """Analyze website content and structure for script generation."""

    async def analyze(self, url: str) -> Dict[str, Any]:
        """Analyze website and extract key information.

        Args:
            url: Website URL to analyze

        Returns:
            Dictionary containing:
            - title: Page title
            - description: Meta description
            - headings: List of main headings
            - sections: Key sections and their content
            - cta_buttons: Call-to-action buttons
            - features: Detected features/benefits
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Extract page information
                analysis = {
                    "url": url,
                    "title": await page.title(),
                    "description": await page.locator('meta[name="description"]').get_attribute("content") or "",
                    "headings": [],
                    "sections": [],
                    "cta_buttons": [],
                    "features": []
                }

                # Extract headings (h1, h2)
                h1_elements = await page.locator("h1").all()
                for h1 in h1_elements:
                    text = await h1.text_content()
                    if text:
                        analysis["headings"].append({"level": 1, "text": text.strip()})

                h2_elements = await page.locator("h2").all()
                for h2 in h2_elements[:5]:  # Limit to first 5
                    text = await h2.text_content()
                    if text:
                        analysis["headings"].append({"level": 2, "text": text.strip()})

                # Extract CTA buttons
                button_selectors = [
                    'button:has-text("试用")',
                    'button:has-text("开始")',
                    'a:has-text("了解更多")',
                    'a:has-text("Get Started")',
                    'button:has-text("Demo")'
                ]

                for selector in button_selectors:
                    try:
                        buttons = await page.locator(selector).all()
                        for btn in buttons[:3]:
                            text = await btn.text_content()
                            if text:
                                analysis["cta_buttons"].append(text.strip())
                    except:
                        pass

                # Get page screenshot for context
                screenshot = await page.screenshot(full_page=False)

                # Get viewport dimensions for script generation
                viewport = page.viewport_size
                analysis["viewport"] = viewport

            finally:
                await browser.close()

            return analysis


class ScriptGenerator:
    """Generate demo video scripts using AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_script(
        self,
        website_analysis: Dict[str, Any],
        user_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate demo video script using AI.

        Args:
            website_analysis: Analysis result from WebsiteAnalyzer
            user_requirements: Optional user preferences:
                - video_length: Target length in seconds (default: 60)
                - style: 'professional', 'casual', 'energetic' (default: 'professional')
                - focus_areas: List of areas to emphasize
                - language: 'zh-CN', 'en-US', etc (default: 'zh-CN')

        Returns:
            Complete script in YAML format
        """
        requirements = user_requirements or {}
        video_length = requirements.get("video_length", 60)
        style = requirements.get("style", "professional")
        language = requirements.get("language", "zh-CN")
        focus_areas = requirements.get("focus_areas", [])

        # Build prompt for Claude
        prompt = self._build_prompt(website_analysis, requirements)

        # Call Claude API
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract YAML script from response
        script_yaml = message.content[0].text

        # Parse and validate
        import yaml
        try:
            script_data = yaml.safe_load(script_yaml)
            return script_data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse generated script: {e}")

    def _build_prompt(self, analysis: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Build prompt for Claude to generate script."""

        video_length = requirements.get("video_length", 60)
        style = requirements.get("style", "professional")
        language = requirements.get("language", "zh-CN")

        voice_map = {
            "zh-CN": "zh-CN-XiaoxiaoNeural",
            "en-US": "en-US-JennyNeural",
            "ja-JP": "ja-JP-NanamiNeural"
        }

        prompt = f"""你是一个专业的产品演示视频脚本编写专家。请根据以下网站分析结果，生成一个完整的演示视频分镜脚本。

网站信息：
- URL: {analysis['url']}
- 标题: {analysis['title']}
- 描述: {analysis.get('description', '无')}
- 主要标题: {', '.join([h['text'] for h in analysis.get('headings', [])[:5]])}
- CTA按钮: {', '.join(analysis.get('cta_buttons', []))}

要求：
- 视频总长度: 约{video_length}秒
- 风格: {style}
- 语言: {language}
- 分辨率: 1920x1080

请生成一个YAML格式的分镜脚本，包含：
1. project配置（name, resolution, fps, voice, bitrate）
2. 3-5个精心设计的场景（scenes），每个场景包含：
   - id: 场景唯一标识
   - url: 要访问的URL（可选，如果切换页面）
   - narration: 旁白文字（自然、流畅、吸引人）
   - actions: 具体的浏览器操作（滚动、点击、等待等）

场景设计原则：
- 第一个场景：展示首页核心价值主张
- 中间场景：展示关键功能/特色
- 最后场景：总结和号召行动
- 每个场景的narration要简洁有力，突出重点
- actions要合理，模拟真实用户浏览行为

可用的action类型：
- scroll: 滚动页面 (参数: y, smooth)
- scroll_to_text: 滚动到包含特定文本的元素 (参数: text, offset)
- click: 点击元素 (参数: selector 或 text)
- wait: 等待 (参数: duration)
- goto: 访问新URL (参数: url)

请直接输出YAML格式的脚本，不要有其他说明文字：

```yaml
project:
  name: "产品演示视频"
  resolution: [1920, 1080]
  fps: 30
  voice: "{voice_map.get(language, 'zh-CN-XiaoxiaoNeural')}"
  bitrate: "8000k"

scenes:
  - id: "scene_01"
    url: "{analysis['url']}"
    narration: "..."
    actions:
      - type: scroll
        y: 0
      - type: wait
        duration: 2
```

请确保生成完整、可执行的脚本。"""

        return prompt


async def generate_demo_script(
    url: str,
    api_key: Optional[str] = None,
    **requirements
) -> Dict[str, Any]:
    """Convenience function to analyze website and generate script.

    Args:
        url: Website URL
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        **requirements: Additional requirements (video_length, style, etc)

    Returns:
        Generated script as dictionary
    """
    # Analyze website
    analyzer = WebsiteAnalyzer()
    analysis = await analyzer.analyze(url)

    # Generate script
    generator = ScriptGenerator(api_key)
    script = generator.generate_script(analysis, requirements)

    return script


# CLI for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ai_generator.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    async def main():
        script = await generate_demo_script(url)

        import yaml
        print(yaml.dump(script, allow_unicode=True, sort_keys=False))

    asyncio.run(main())
