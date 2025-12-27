#!/usr/bin/env python3
"""
AI 视频脚本生成器 - 演示脚本(无需 API Key)
展示不同 AI 模型的 Prompt 优化策略
"""
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from demo_video_generator.core.ai_generator_v2 import PromptOptimizer


def demo_prompt_comparison():
    """演示不同 AI 模型的 Prompt 优化策略"""

    # 模拟网站分析结果
    website_analysis = {
        "url": "http://essay.wanli.ai/",
        "title": "万里书院 - AI 驱动的智能写作助手",
        "description": "智能AI写作助手，帮助你快速创作高质量内容",
        "headings": [
            {"level": 1, "text": "智能写作，从这里开始"},
            {"level": 2, "text": "核心功能"},
            {"level": 2, "text": "AI 润色"},
            {"level": 2, "text": "多场景支持"},
            {"level": 2, "text": "立即体验"}
        ],
        "sections": [
            "提供 AI 辅助写作、智能润色、多场景模板等功能",
            "一键优化文章结构、语言表达和逻辑流畅度",
            "支持论文、报告、文案等多种写作场景"
        ],
        "cta_buttons": ["免费试用", "立即体验", "了解更多"],
        "page_height": 3200
    }

    requirements = {
        "video_length": 30,
        "language": "zh-CN",
        "style": "professional",
        "focus_areas": ["核心功能", "用户价值"]
    }

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         AI 视频脚本生成器 - Prompt 优化策略演示                      ║
╚══════════════════════════════════════════════════════════════════════╝

本演示展示了针对不同 AI 模型优化的 Prompt 策略
无需 API Key，可直接查看各模型的 Prompt 设计
""")

    providers = [
        ("claude", "Claude 3.5 Sonnet - Anthropic"),
        ("deepseek", "DeepSeek - 高性价比代码模型"),
        ("gpt", "GPT-4 - OpenAI"),
        ("minimax", "MiniMax - 国内访问友好"),
        ("gemini", "Gemini - Google 多模态模型")
    ]

    for provider_key, provider_name in providers:
        print(f"\n{'='*80}")
        print(f"提供商: {provider_name}")
        print(f"{'='*80}\n")

        # 获取针对该提供商优化的 Prompt
        if provider_key == "claude":
            prompt = PromptOptimizer.build_claude_prompt(website_analysis, requirements)
        elif provider_key == "deepseek":
            prompt = PromptOptimizer.build_deepseek_prompt(website_analysis, requirements)
        elif provider_key == "gpt":
            prompt = PromptOptimizer.build_gpt_prompt(website_analysis, requirements)
        elif provider_key == "minimax":
            prompt = PromptOptimizer.build_minimax_prompt(website_analysis, requirements)
        elif provider_key == "gemini":
            prompt = PromptOptimizer.build_gemini_prompt(website_analysis, requirements)

        # 显示 Prompt 的关键特征
        print(f"Prompt 长度: {len(prompt)} 字符")
        print(f"Prompt 预览 (前 500 字符):\n")
        print("-" * 80)
        print(prompt[:500])
        print("...")
        print("-" * 80)

        # 分析 Prompt 特点
        print(f"\nPrompt 设计特点:")
        if provider_key == "claude":
            print("  ✓ 结构化: 使用 XML 标签清晰分隔各个部分")
            print("  ✓ 详细说明: 提供完整的 YAML 格式示例")
            print("  ✓ 专业风格: 强调准确性和完整性")
            print("  ✓ 最佳实践: Claude 擅长理解复杂结构和详细指令")
        elif provider_key == "deepseek":
            print("  ✓ Schema 驱动: 明确定义数据结构和类型")
            print("  ✓ 代码风格: 使用代码块和严格的格式约束")
            print("  ✓ 逻辑严谨: 强调技术准确性")
            print("  ✓ 最佳实践: DeepSeek 在代码和结构化任务上表现优异")
        elif provider_key == "gpt":
            print("  ✓ 指令明确: 清晰的步骤化指导")
            print("  ✓ 格式严格: 强调 YAML 语法规范")
            print("  ✓ 示例丰富: 提供具体的输出示例")
            print("  ✓ 最佳实践: GPT 在遵循明确指令方面表现出色")
        elif provider_key == "minimax":
            print("  ✓ 中文友好: 使用中文术语和表达")
            print("  ✓ 创意导向: 鼓励生动的叙述和场景设计")
            print("  ✓ 对话风格: 更自然的交互方式")
            print("  ✓ 最佳实践: MiniMax 对中文语境理解深入")
        elif provider_key == "gemini":
            print("  ✓ 多模态: 强调视觉和上下文理解")
            print("  ✓ JSON 输入: 使用结构化数据格式")
            print("  ✓ 场景描述: 注重视觉呈现的细节")
            print("  ✓ 最佳实践: Gemini 擅长整合多种信息源")

        input("\n按 Enter 查看下一个提供商的 Prompt...")

    print(f"\n{'='*80}")
    print("Prompt 优化策略总结")
    print(f"{'='*80}\n")

    print("""
不同 AI 模型的 Prompt 优化关键点:

1. Claude (Anthropic)
   - 使用 XML 标签组织内容
   - 提供详细的上下文和示例
   - 强调结构化和专业性
   - 适合复杂任务和长篇内容

2. DeepSeek
   - Schema 和类型定义优先
   - 代码风格的格式要求
   - 强调逻辑严谨性
   - 适合技术文档和结构化数据

3. GPT (OpenAI)
   - 清晰的分步指令
   - 严格的格式规范
   - 丰富的示例
   - 适合需要精确遵循指令的任务

4. MiniMax
   - 中文语境优化
   - 创意和叙述性强
   - 对话式交互
   - 适合需要本地化和创意的内容

5. Gemini (Google)
   - 多模态信息整合
   - JSON 结构化输入
   - 视觉场景描述
   - 适合需要综合理解的任务

实际使用时的建议:
- 根据内容类型选择模型(技术文档→DeepSeek, 创意内容→MiniMax)
- 根据语言选择模型(中文→MiniMax/DeepSeek, 英文→Claude/GPT)
- 根据复杂度选择模型(简单→GPT, 复杂→Claude)
- 根据预算选择模型(高性价比→DeepSeek, 最佳质量→Claude Opus)
""")

    print("\n如需实际测试 AI 生成效果,请配置以下环境变量:")
    print("  export ANTHROPIC_API_KEY='your_key'")
    print("  export DEEPSEEK_API_KEY='your_key'")
    print("  export OPENAI_API_KEY='your_key'")
    print("\n然后运行: python examples/test_ai_models.py")


if __name__ == "__main__":
    demo_prompt_comparison()
