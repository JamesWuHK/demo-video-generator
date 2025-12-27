#!/usr/bin/env python3
"""
测试和对比不同 AI 模型生成视频脚本的效果
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from demo_video_generator.core.ai_generator_v2 import (
    WebsiteAnalyzer,
    MultiProviderScriptGenerator,
    ModelProvider,
)


async def test_single_provider(
    provider: ModelProvider,
    url: str,
    api_key: str = None
) -> Dict[str, Any]:
    """测试单个 AI 提供商"""
    print(f"\n{'='*80}")
    print(f"测试提供商: {provider.upper()}")
    print(f"{'='*80}")

    try:
        # 1. 分析网站
        print(f"\n[1/3] 分析网站: {url}")
        analyzer = WebsiteAnalyzer()
        analysis = await analyzer.analyze(url)

        print(f"  ✓ 标题: {analysis.get('title', 'N/A')}")
        print(f"  ✓ 主要标题数: {len(analysis.get('headings', []))}")
        print(f"  ✓ CTA 按钮数: {len(analysis.get('ctas', []))}")
        print(f"  ✓ 页面高度: {analysis.get('page_height', 0)}px")

        # 2. 生成脚本
        print(f"\n[2/3] 使用 {provider} 生成脚本...")
        generator = MultiProviderScriptGenerator(provider=provider, api_key=api_key)

        requirements = {
            "video_length": 30,
            "language": "zh-CN",
            "style": "professional",
            "focus_areas": ["核心功能", "用户价值"]
        }

        script = await generator.generate_script(analysis, requirements)

        # 3. 分析结果
        print(f"\n[3/3] 生成结果分析:")
        scenes = script.get("scenes", [])
        print(f"  ✓ 场景数量: {len(scenes)}")

        total_duration = 0
        for i, scene in enumerate(scenes, 1):
            duration = scene.get("duration", 0)
            total_duration += duration
            print(f"  ✓ 场景 {i}: {scene.get('id', 'N/A')} ({duration}秒)")
            print(f"    - 解说: {scene.get('narration', '')[:50]}...")
            print(f"    - 操作数: {len(scene.get('actions', []))}")

        print(f"\n  总时长: {total_duration}秒 (要求: {requirements['video_length']}秒)")

        return {
            "provider": provider,
            "success": True,
            "script": script,
            "metrics": {
                "scene_count": len(scenes),
                "total_duration": total_duration,
                "avg_scene_duration": total_duration / len(scenes) if scenes else 0,
                "total_actions": sum(len(s.get("actions", [])) for s in scenes),
            }
        }

    except Exception as e:
        print(f"\n  ✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "provider": provider,
            "success": False,
            "error": str(e)
        }


async def compare_providers(
    url: str,
    providers: List[ModelProvider] = None
) -> Dict[str, Any]:
    """对比多个 AI 提供商的输出"""
    if providers is None:
        # 默认测试有 API key 的提供商
        providers = []
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append("claude")
        if os.getenv("DEEPSEEK_API_KEY"):
            providers.append("deepseek")
        if os.getenv("OPENAI_API_KEY"):
            providers.append("gpt")
        if os.getenv("MINIMAX_API_KEY"):
            providers.append("minimax")
        if os.getenv("GOOGLE_API_KEY"):
            providers.append("gemini")

    if not providers:
        print("错误: 没有配置任何 AI API Key")
        print("请设置以下环境变量之一:")
        print("  - ANTHROPIC_API_KEY (Claude)")
        print("  - DEEPSEEK_API_KEY (DeepSeek)")
        print("  - OPENAI_API_KEY (GPT)")
        print("  - MINIMAX_API_KEY (MiniMax)")
        print("  - GOOGLE_API_KEY (Gemini)")
        return {}

    print(f"\n准备测试 {len(providers)} 个 AI 提供商: {', '.join(providers)}")

    # 并行测试所有提供商
    tasks = [test_single_provider(p, url) for p in providers]
    results = await asyncio.gather(*tasks)

    # 汇总结果
    print(f"\n{'='*80}")
    print("对比分析结果")
    print(f"{'='*80}\n")

    comparison = {
        "url": url,
        "providers_tested": len(providers),
        "results": results,
        "summary": {}
    }

    successful_results = [r for r in results if r.get("success")]

    if successful_results:
        print(f"成功生成: {len(successful_results)}/{len(results)}\n")

        # 对比指标
        print(f"{'提供商':<12} {'场景数':<8} {'总时长':<10} {'平均时长':<12} {'总操作数':<10}")
        print("-" * 70)

        for result in successful_results:
            provider = result["provider"]
            metrics = result["metrics"]
            print(f"{provider:<12} {metrics['scene_count']:<8} "
                  f"{metrics['total_duration']:<10.1f} "
                  f"{metrics['avg_scene_duration']:<12.1f} "
                  f"{metrics['total_actions']:<10}")

        # 找出最佳结果
        best_duration = min(successful_results,
                           key=lambda x: abs(x["metrics"]["total_duration"] - 30))
        best_scenes = max(successful_results,
                         key=lambda x: x["metrics"]["scene_count"])

        print(f"\n推荐:")
        print(f"  最接近目标时长: {best_duration['provider']} "
              f"({best_duration['metrics']['total_duration']}秒)")
        print(f"  场景最丰富: {best_scenes['provider']} "
              f"({best_scenes['metrics']['scene_count']}个场景)")

        comparison["summary"] = {
            "best_duration": best_duration["provider"],
            "best_scenes": best_scenes["provider"]
        }

    # 保存详细结果
    output_file = Path("output/ai_comparison_results.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存到: {output_file}")

    return comparison


async def main():
    """主函数"""
    # 测试网站
    test_url = "http://essay.wanli.ai/"

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║         AI 视频脚本生成器 - 多模型对比测试                           ║
╚══════════════════════════════════════════════════════════════════════╝

测试网站: {test_url}

检查 API Keys:
  - ANTHROPIC_API_KEY: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}
  - DEEPSEEK_API_KEY:  {'✓' if os.getenv('DEEPSEEK_API_KEY') else '✗'}
  - OPENAI_API_KEY:    {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}
  - MINIMAX_API_KEY:   {'✓' if os.getenv('MINIMAX_API_KEY') else '✗'}
  - GOOGLE_API_KEY:    {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}
""")

    # 运行对比测试
    await compare_providers(test_url)

    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(main())
