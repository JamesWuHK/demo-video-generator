"""Multi-provider AI script generator with optimized prompts.

Supports multiple AI providers:
- Anthropic Claude (claude-3-5-sonnet)
- DeepSeek (deepseek-chat)
- MiniMax (abab6.5)
- Google Gemini (gemini-pro)
- OpenAI GPT (gpt-4-turbo)
"""

import asyncio
import os
from typing import Optional, Dict, Any, List, Literal
from playwright.async_api import async_playwright
import anthropic
from openai import AsyncOpenAI
import httpx
import yaml


ModelProvider = Literal["claude", "deepseek", "minimax", "gemini", "gpt"]


class WebsiteAnalyzer:
    """Analyze website content and structure for script generation."""

    async def analyze(self, url: str, max_sections: int = 5) -> Dict[str, Any]:
        """Analyze website and extract key information.

        Args:
            url: Website URL to analyze
            max_sections: Maximum number of sections to extract

        Returns:
            Dictionary containing site structure and content
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)

                # Extract comprehensive page information
                analysis = {
                    "url": url,
                    "title": await page.title(),
                    "description": "",
                    "headings": [],
                    "sections": [],
                    "cta_buttons": [],
                    "features": [],
                    "images": [],
                    "page_structure": {}
                }

                # Meta description
                try:
                    desc = await page.locator('meta[name="description"]').get_attribute("content")
                    analysis["description"] = desc or ""
                except:
                    pass

                # Extract main heading
                try:
                    h1_elements = await page.locator("h1").all()
                    for h1 in h1_elements[:3]:
                        text = await h1.text_content()
                        if text and len(text.strip()) > 0:
                            analysis["headings"].append({
                                "level": 1,
                                "text": text.strip()[:200]
                            })
                except:
                    pass

                # Extract subheadings
                try:
                    h2_elements = await page.locator("h2").all()
                    for h2 in h2_elements[:max_sections]:
                        text = await h2.text_content()
                        if text and len(text.strip()) > 0:
                            analysis["headings"].append({
                                "level": 2,
                                "text": text.strip()[:200]
                            })
                except:
                    pass

                # Extract sections/paragraphs for context
                try:
                    paragraphs = await page.locator("p").all()
                    for p in paragraphs[:10]:
                        text = await p.text_content()
                        if text and len(text.strip()) > 20:
                            analysis["sections"].append(text.strip()[:300])
                except:
                    pass

                # CTA buttons
                button_patterns = [
                    'button, a[href*="trial"], a[href*="demo"], a[href*="start"]',
                    'text=/开始|试用|立即|免费|Demo|Start|Try|Free/i'
                ]

                for pattern in button_patterns:
                    try:
                        elements = await page.locator(pattern).all()
                        for elem in elements[:5]:
                            text = await elem.text_content()
                            if text and len(text.strip()) > 0:
                                btn_text = text.strip()[:50]
                                if btn_text not in analysis["cta_buttons"]:
                                    analysis["cta_buttons"].append(btn_text)
                    except:
                        pass

                # Get viewport info
                analysis["viewport"] = {"width": 1920, "height": 1080}

                # Get page height for scroll planning
                try:
                    page_height = await page.evaluate("document.documentElement.scrollHeight")
                    analysis["page_height"] = page_height
                except:
                    analysis["page_height"] = 3000

            finally:
                await context.close()
                await browser.close()

            return analysis


class PromptOptimizer:
    """Optimized prompts for different AI models."""

    @staticmethod
    def build_claude_prompt(
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Claude-optimized prompt with detailed instructions."""

        video_length = requirements.get("video_length", 60)
        style = requirements.get("style", "professional")
        language = requirements.get("language", "zh-CN")

        voice_map = {
            "zh-CN": "zh-CN-XiaoxiaoNeural",
            "zh-TW": "zh-TW-HsiaoChenNeural",
            "en-US": "en-US-JennyNeural",
            "ja-JP": "ja-JP-NanamiNeural",
        }

        style_guide = {
            "professional": "专业、权威、重点突出产品价值",
            "casual": "轻松、友好、贴近用户日常使用场景",
            "energetic": "活力、激情、强调创新和突破"
        }

        headings_text = "\n".join([f"  - {h['text']}" for h in analysis.get('headings', [])[:8]])
        sections_text = "\n".join([f"  - {s[:150]}" for s in analysis.get('sections', [])[:5]])

        prompt = f"""你是一位顶尖的产品演示视频脚本专家，专注于为 SaaS 产品创作高转化率的演示视频脚本。

## 网站分析结果

**URL**: {analysis['url']}
**标题**: {analysis.get('title', 'N/A')}
**描述**: {analysis.get('description', 'N/A')}

**主要内容结构**:
{headings_text}

**核心信息**:
{sections_text}

**行动号召**: {', '.join(analysis.get('cta_buttons', [])[:5])}

## 脚本要求

- **视频时长**: {video_length}秒
- **叙事风格**: {style_guide.get(style, '专业')}
- **语言**: {language}
- **分辨率**: 1920x1080 (16:9)
- **目标**: 在{video_length}秒内清晰展示产品核心价值，引导用户行动

## 输出格式

请直接输出一个可执行的 YAML 脚本，包含：

1. **project** 配置
2. **scenes** 场景数组（3-5个场景）

### 场景设计原则

**开场场景** (0-15秒):
- 快速建立产品认知
- 一句话价值主张
- 展示首屏核心信息
- Action: scroll y:0, wait 2-3秒

**功能展示** (15-45秒):
- 2-3个核心功能/特色
- 每个功能简明扼要
- 配合平滑滚动展示
- Action: scroll_to_text 或 smooth scroll

**结尾号召** (45-{video_length}秒):
- 总结核心优势
- 明确行动号召
- 滚回顶部或定位 CTA
- Action: click CTA 或 scroll to CTA

### Narration 要求

- **简洁有力**: 每句话10-20字
- **价值导向**: 突出"用户能获得什么"
- **自然流畅**: 像真人讲解，不要太书面化
- **节奏把控**: 总字数控制在 {video_length * 3} 字左右

### Actions 设计要点

可用动作类型:
- `scroll`: {{y: 数值, smooth: true/false}}  # 滚动到指定位置
- `scroll_to_text`: {{text: "文本", offset: 100}}  # 滚动到包含文本的元素
- `click`: {{text: "按钮文字"}} 或 {{selector: "CSS选择器"}}
- `wait`: {{duration: 秒数}}  # 停留时间
- `goto`: {{url: "新URL"}}  # 页面跳转（慎用）

**注意**:
- 每个场景 actions 执行时间应匹配 narration 时长
- 滚动距离基于页面高度 {analysis.get('page_height', 3000)}px
- 使用 smooth:true 创造流畅体验
- wait 时间总和应接近但略小于 narration 时长

## 输出示例

```yaml
project:
  name: "{analysis.get('title', '产品演示')[:30]}"
  resolution: [1920, 1080]
  fps: 30
  voice: "{voice_map.get(language, 'zh-CN-XiaoxiaoNeural')}"
  bitrate: "10000k"

scenes:
  - id: "opening"
    url: "{analysis['url']}"
    narration: "简洁的开场白，点出核心价值。"
    actions:
      - type: scroll
        y: 0
      - type: wait
        duration: 3

  - id: "feature_01"
    narration: "第一个核心功能的介绍。"
    actions:
      - type: scroll
        y: 800
        smooth: true
      - type: wait
        duration: 2.5

  # ... 更多场景

  - id: "closing"
    narration: "总结并号召行动。"
    actions:
      - type: scroll
        y: 0
        smooth: true
      - type: wait
        duration: 2
```

请基于以上信息，生成一个高质量的演示视频脚本。直接输出 YAML，不要有额外说明。"""

        return prompt

    @staticmethod
    def build_deepseek_prompt(
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """DeepSeek-optimized prompt (more structured, code-focused)."""

        video_length = requirements.get("video_length", 60)
        language = requirements.get("language", "zh-CN")

        prompt = f"""# 任务：生成产品演示视频脚本

## 输入数据
- URL: {analysis['url']}
- 标题: {analysis.get('title', '')}
- 核心内容: {', '.join([h['text'] for h in analysis.get('headings', [])[:5]])}
- 视频时长: {video_length}秒
- 语言: {language}

## 输出要求
生成符合以下 schema 的 YAML 脚本:

```yaml
project:
  name: string  # 视频名称
  resolution: [1920, 1080]  # 固定
  fps: 30
  voice: string  # TTS 语音
  bitrate: "10000k"

scenes:  # 3-5个场景
  - id: string  # 唯一标识
    url: string  # 可选，页面URL
    narration: string  # 旁白，10-30字
    actions:  # 浏览器操作
      - type: scroll|click|wait|scroll_to_text
        # 对应参数
```

## 约束条件
1. 总场景数: 3-5个
2. narration 总字数: ≈ {video_length * 3}字
3. 每场景 wait 时间总和应匹配 narration 时长
4. 滚动范围: 0 - {analysis.get('page_height', 3000)}px
5. 必须包含开场、功能展示、结尾

## 输出
直接输出可解析的 YAML，无额外文字。

分析网站 {analysis['url']}，生成脚本:"""

        return prompt

    @staticmethod
    def build_minimax_prompt(
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """MiniMax-optimized prompt (Chinese-friendly, creative)."""

        video_length = requirements.get("video_length", 60)
        style = requirements.get("style", "professional")

        style_keywords = {
            "professional": "专业、精准、高效",
            "casual": "亲切、有趣、生活化",
            "energetic": "激情、创新、未来感"
        }

        prompt = f"""请为网站 {analysis['url']} 生成一个{video_length}秒的产品演示视频脚本。

网站信息：
• 名称：{analysis.get('title', '')}
• 简介：{analysis.get('description', '')[:100]}
• 主要模块：{', '.join([h['text'] for h in analysis.get('headings', [])[:6]])}

脚本风格：{style_keywords.get(style, '专业')}

请以 YAML 格式输出，包含：
1. project 配置（name, resolution [1920,1080], fps 30, voice "zh-CN-XiaoxiaoNeural", bitrate "10000k"）
2. scenes 数组，每个场景包含 id、narration（旁白）、actions（动作序列）

场景设计：
• 第1场景：开场，展示核心价值（0-20秒）
• 第2-3场景：关键功能/亮点（20-45秒）
• 最后场景：总结+行动号召（45-{video_length}秒）

旁白要求：
• 精练有力，每句10-25字
• 口语化表达，避免生硬
• 突出产品优势和用户价值

动作类型：
• scroll: 滚动 (y: 像素值, smooth: true/false)
• wait: 停留 (duration: 秒数)
• scroll_to_text: 定位元素 (text: "文字")
• click: 点击 (text: "按钮")

直接输出 YAML，不要有其他解释："""

        return prompt

    @staticmethod
    def build_gemini_prompt(
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Gemini-optimized prompt (multimodal, context-aware)."""

        video_length = requirements.get("video_length", 60)

        prompt = f"""Generate a professional product demo video script in YAML format.

Website Analysis:
- URL: {analysis['url']}
- Title: {analysis.get('title', '')}
- Key Sections: {', '.join([h['text'] for h in analysis.get('headings', [])[:6]])}
- Description: {analysis.get('description', '')[:150]}
- Page Height: {analysis.get('page_height', 3000)}px

Requirements:
- Video Duration: {video_length} seconds
- Resolution: 1920x1080
- Language: Chinese (zh-CN)
- FPS: 30
- Voice: zh-CN-XiaoxiaoNeural

Script Structure:
1. Opening (0-15s): Hook + Value Proposition
2. Features (15-50s): 2-3 Key Features
3. Closing (50-{video_length}s): Summary + CTA

Narration Guidelines:
- Concise and impactful (10-25 characters per line)
- Total ≈ {video_length * 3} characters
- Natural, conversational tone
- Focus on user benefits

Actions Schema:
- scroll: {{y: number, smooth: boolean}}
- scroll_to_text: {{text: string, offset: number}}
- wait: {{duration: number}}
- click: {{text: string}}

Output valid YAML only, no explanations:

```yaml
project:
  name: "..."
  resolution: [1920, 1080]
  fps: 30
  voice: "zh-CN-XiaoxiaoNeural"
  bitrate: "10000k"

scenes:
  - id: "..."
    url: "{analysis['url']}"
    narration: "..."
    actions:
      - type: ...
```"""

        return prompt

    @staticmethod
    def build_gpt_prompt(
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """GPT-optimized prompt (instruction-following, structured)."""

        video_length = requirements.get("video_length", 60)

        prompt = f"""You are an expert video script writer specializing in SaaS product demos.

Task: Create a {video_length}-second demo video script for the website.

Input Data:
```json
{{
  "url": "{analysis['url']}",
  "title": "{analysis.get('title', '')}",
  "headings": {[h['text'] for h in analysis.get('headings', [])[:5]]},
  "page_height": {analysis.get('page_height', 3000)},
  "cta_buttons": {analysis.get('cta_buttons', [])}
}}
```

Output Requirements:
1. Valid YAML format
2. 3-5 scenes total
3. Chinese narration (≈ {video_length * 3} chars total)
4. Precise browser actions (scroll/wait/click)

Schema:
```yaml
project:
  name: str
  resolution: [1920, 1080]
  fps: 30
  voice: "zh-CN-XiaoxiaoNeural"
  bitrate: "10000k"

scenes:
  - id: str (unique)
    url: str (optional)
    narration: str (10-30 chars)
    actions:
      - type: scroll|wait|click|scroll_to_text
        # relevant params
```

Scene Flow:
1. Opening: Value prop + hero section
2. Middle: Key features (2-3)
3. Closing: Summary + CTA

Generate the YAML script now:"""

        return prompt


class MultiProviderScriptGenerator:
    """Generate scripts using multiple AI providers."""

    def __init__(
        self,
        provider: ModelProvider = "claude",
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.api_key = api_key or self._get_api_key(provider)

        # Initialize clients
        self.clients = {}
        self._init_clients()

    def _get_api_key(self, provider: ModelProvider) -> str:
        """Get API key from environment."""
        env_keys = {
            "claude": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "minimax": "MINIMAX_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "gpt": "OPENAI_API_KEY"
        }

        key = os.getenv(env_keys[provider])
        if not key:
            raise ValueError(f"{env_keys[provider]} environment variable not set")
        return key

    def _init_clients(self):
        """Initialize API clients."""
        try:
            if self.provider == "claude":
                self.clients["claude"] = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider in ["gpt", "deepseek"]:
                base_url = None
                if self.provider == "deepseek":
                    base_url = "https://api.deepseek.com"
                self.clients[self.provider] = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=base_url
                )
        except Exception as e:
            raise ValueError(f"Failed to initialize {self.provider} client: {e}")

    async def generate_script(
        self,
        website_analysis: Dict[str, Any],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate script using selected AI provider."""

        requirements = requirements or {}

        # Build optimized prompt
        prompt = self._build_prompt(website_analysis, requirements)

        # Call appropriate API
        if self.provider == "claude":
            response_text = await self._call_claude(prompt)
        elif self.provider == "deepseek":
            response_text = await self._call_deepseek(prompt)
        elif self.provider == "minimax":
            response_text = await self._call_minimax(prompt, requirements)
        elif self.provider == "gemini":
            response_text = await self._call_gemini(prompt)
        elif self.provider == "gpt":
            response_text = await self._call_gpt(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Parse YAML
        script_data = self._parse_script(response_text)

        return script_data

    def _build_prompt(
        self,
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Build optimized prompt for the provider."""

        if self.provider == "claude":
            return PromptOptimizer.build_claude_prompt(analysis, requirements)
        elif self.provider == "deepseek":
            return PromptOptimizer.build_deepseek_prompt(analysis, requirements)
        elif self.provider == "minimax":
            return PromptOptimizer.build_minimax_prompt(analysis, requirements)
        elif self.provider == "gemini":
            return PromptOptimizer.build_gemini_prompt(analysis, requirements)
        elif self.provider == "gpt":
            return PromptOptimizer.build_gpt_prompt(analysis, requirements)

    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API."""
        client = self.clients["claude"]

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API."""
        client = self.clients["deepseek"]

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.7
        )

        return response.choices[0].message.content

    async def _call_minimax(self, prompt: str, requirements: Dict) -> str:
        """Call MiniMax API."""
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "abab6.5-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4096
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4096
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_gpt(self, prompt: str) -> str:
        """Call OpenAI GPT API."""
        client = self.clients["gpt"]

        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _parse_script(self, response_text: str) -> Dict[str, Any]:
        """Parse YAML from AI response."""

        # Extract YAML from markdown code blocks if present
        if "```yaml" in response_text:
            start = response_text.find("```yaml") + 7
            end = response_text.find("```", start)
            yaml_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            yaml_text = response_text[start:end].strip()
        else:
            yaml_text = response_text.strip()

        try:
            script_data = yaml.safe_load(yaml_text)

            # Validate basic structure
            if not isinstance(script_data, dict):
                raise ValueError("Script must be a dictionary")
            if "project" not in script_data or "scenes" not in script_data:
                raise ValueError("Script must contain 'project' and 'scenes'")

            return script_data

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML: {e}\n\nResponse:\n{yaml_text}")


async def generate_demo_script(
    url: str,
    provider: ModelProvider = "claude",
    api_key: Optional[str] = None,
    **requirements
) -> Dict[str, Any]:
    """Main entry point for script generation.

    Args:
        url: Website URL to analyze
        provider: AI provider to use
        api_key: API key (or use environment variable)
        **requirements: Additional requirements (video_length, style, etc)

    Returns:
        Generated script as dictionary
    """

    # Analyze website
    analyzer = WebsiteAnalyzer()
    analysis = await analyzer.analyze(url)

    # Generate script
    generator = MultiProviderScriptGenerator(provider, api_key)
    script = await generator.generate_script(analysis, requirements)

    return script


async def compare_providers(
    url: str,
    providers: List[ModelProvider] = ["claude", "deepseek", "gpt"],
    **requirements
) -> Dict[str, Dict[str, Any]]:
    """Compare script generation across multiple providers.

    Returns:
        Dictionary mapping provider name to generated script
    """

    # Analyze website once
    analyzer = WebsiteAnalyzer()
    analysis = await analyzer.analyze(url)

    # Generate scripts in parallel
    tasks = []
    for provider in providers:
        try:
            generator = MultiProviderScriptGenerator(provider)
            task = generator.generate_script(analysis, requirements)
            tasks.append((provider, task))
        except Exception as e:
            print(f"Warning: Skipping {provider}: {e}")

    # Wait for all
    results = {}
    for provider, task in tasks:
        try:
            script = await task
            results[provider] = {
                "script": script,
                "provider": provider,
                "success": True
            }
        except Exception as e:
            results[provider] = {
                "error": str(e),
                "provider": provider,
                "success": False
            }

    return results


# CLI for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ai_generator_v2.py <url> [provider]")
        print("Providers: claude, deepseek, minimax, gemini, gpt")
        sys.exit(1)

    url = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else "claude"

    async def main():
        print(f"Generating script using {provider}...")
        script = await generate_demo_script(url, provider=provider)
        print(yaml.dump(script, allow_unicode=True, sort_keys=False))

    asyncio.run(main())
