# AI 多模型脚本生成优化指南

## 概述

本文档记录了 Demo Video Generator 项目中 AI 自动生成分镜脚本功能的多模型 Prompt 优化策略。

## 支持的 AI 模型

| 模型 | 提供商 | 特点 | 适用场景 |
|------|--------|------|---------|
| Claude 3.5 Sonnet | Anthropic | 理解能力强,输出质量高 | 复杂任务,长篇内容 |
| DeepSeek | DeepSeek | 性价比高,代码能力强 | 技术文档,结构化数据 |
| GPT-4 | OpenAI | 指令遵循好,通用性强 | 标准化任务,精确要求 |
| MiniMax | MiniMax | 中文优化,国内访问 | 中文内容,本地化需求 |
| Gemini | Google | 多模态,上下文理解 | 综合信息,视觉场景 |

## Prompt 优化策略

### 1. Claude 3.5 Sonnet

**设计理念**: 结构化、详细化、专业化

**关键特点**:
- 使用清晰的 Markdown 结构组织内容
- 提供完整的上下文和背景信息
- 包含详细的输出格式示例
- 强调准确性和完整性

**Prompt 模板结构**:
```
角色定位
  └─ 网站分析结果
      ├─ URL/标题/描述
      ├─ 内容结构
      ├─ 核心信息
      └─ 行动号召
  └─ 脚本要求
      ├─ 时长/风格/语言
      └─ 目标定位
  └─ 输出格式
      ├─ YAML 结构说明
      ├─ 场景设计要点
      └─ 完整示例
```

**适用场景**:
- 需要高质量输出的商业项目
- 复杂的多场景视频脚本
- 需要精确控制的专业内容

### 2. DeepSeek

**设计理念**: Schema 驱动、代码风格、逻辑严谨

**关键特点**:
- 使用 Schema 定义明确数据结构
- 代码块展示格式要求
- 强调类型和约束
- 技术化的表达方式

**Prompt 模板结构**:
```
任务定义
  └─ 输入数据 (结构化列表)
  └─ 输出要求
      ├─ Schema 定义 (YAML)
      ├─ 类型约束
      └─ 格式规范
  └─ 约束条件 (代码注释风格)
```

**适用场景**:
- 技术产品演示
- 需要精确数据结构的场景
- 预算有限但要求质量的项目

### 3. GPT-4

**设计理念**: 指令明确、步骤清晰、示例丰富

**关键特点**:
- 清晰的分步指导
- JSON 格式的输入数据
- 严格的输出规范
- 具体的示例参考

**Prompt 模板结构**:
```
角色 + 任务
  └─ Input Data (JSON)
  └─ Output Requirements
      ├─ 格式要求 (编号列表)
      ├─ 数量约束
      └─ 质量标准
  └─ YAML Template (完整示例)
```

**适用场景**:
- 标准化的视频脚本生成
- 需要严格遵循格式的任务
- 英文内容为主的项目

### 4. MiniMax

**设计理念**: 中文友好、创意导向、对话自然

**关键特点**:
- 全中文表达,符合中文语境
- 鼓励创意和生动描述
- 对话式的交互风格
- 强调用户体验和价值

**Prompt 模板结构**:
```
任务描述 (口语化)
  └─ 网站信息 (bullet points)
  └─ 脚本风格
  └─ 输出格式 (中文说明)
  └─ 场景设计 (创意引导)
  └─ 旁白要求 (表达技巧)
```

**适用场景**:
- 中文市场的产品推广
- 需要创意和情感表达的内容
- 国内服务器部署的项目

### 5. Gemini

**设计理念**: 多模态整合、上下文丰富、视觉导向

**关键特点**:
- 结构化的 JSON 输入
- 强调视觉和场景描述
- 多维度信息整合
- 注重用户体验设计

**Prompt 模板结构**:
```
任务 + 目标
  └─ Website Analysis (JSON)
  └─ Requirements (JSON)
  └─ Scene Design Guidelines
      ├─ 视觉元素
      ├─ 用户体验
      └─ 叙事流程
  └─ YAML Output Format
```

**适用场景**:
- 视觉效果要求高的演示
- 需要综合多种信息源
- 强调用户体验的产品

## 实际使用建议

### 选型决策树

```
开始
  ├─ 预算充足?
  │   ├─ 是 → Claude Opus 4.5 (最佳质量)
  │   └─ 否 → 继续
  ├─ 主要语言?
  │   ├─ 中文 → MiniMax / DeepSeek
  │   └─ 英文 → GPT-4 / Claude
  ├─ 内容类型?
  │   ├─ 技术产品 → DeepSeek
  │   ├─ 创意内容 → MiniMax / Claude
  │   └─ 标准演示 → GPT-4
  └─ 复杂度?
      ├─ 高 → Claude
      └─ 低 → GPT-4 / DeepSeek
```

### 成本对比 (每 1M tokens)

| 模型 | 输入成本 | 输出成本 | 性价比 |
|------|----------|----------|--------|
| Claude 3.5 Sonnet | $3 | $15 | ⭐⭐⭐⭐ |
| DeepSeek | $0.14 | $0.28 | ⭐⭐⭐⭐⭐ |
| GPT-4 Turbo | $10 | $30 | ⭐⭐⭐ |
| MiniMax | ¥15 | ¥30 | ⭐⭐⭐⭐ |
| Gemini Pro | $1.25 | $5 | ⭐⭐⭐⭐⭐ |

### 质量对比 (基于测试)

| 维度 | Claude | DeepSeek | GPT-4 | MiniMax | Gemini |
|------|--------|----------|-------|---------|--------|
| 理解能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 创意性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 格式准确 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 中文质量 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 使用示例

### 配置环境变量

```bash
# 至少配置一个 AI 提供商
export ANTHROPIC_API_KEY="sk-ant-..."
export DEEPSEEK_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."
export MINIMAX_API_KEY="..."
export GOOGLE_API_KEY="..."
```

### 查看 Prompt 策略 (无需 API Key)

```bash
python examples/demo_prompts.py
```

### 运行模型对比测试

```bash
python examples/test_ai_models.py
```

### API 调用示例

```python
from demo_video_generator.core.ai_generator_v2 import (
    WebsiteAnalyzer,
    MultiProviderScriptGenerator
)

# 1. 分析网站
analyzer = WebsiteAnalyzer()
analysis = await analyzer.analyze("https://example.com")

# 2. 生成脚本 (选择提供商)
generator = MultiProviderScriptGenerator(
    provider="claude",  # 或 "deepseek", "gpt", "minimax", "gemini"
    api_key="your_api_key"
)

script = await generator.generate_script(
    analysis,
    requirements={
        "video_length": 30,
        "language": "zh-CN",
        "style": "professional"
    }
)

# 3. 对比多个提供商
from demo_video_generator.core.ai_generator_v2 import compare_providers

results = await compare_providers(
    url="https://example.com",
    providers=["claude", "deepseek", "gpt"]
)
```

## Prompt 优化技巧

### 通用原则

1. **明确角色定位**: 告诉 AI 它是什么专家
2. **提供充分上下文**: 网站信息、用户需求、目标受众
3. **明确输出格式**: 使用示例、Schema、模板
4. **设定约束条件**: 时长、场景数、语言风格
5. **包含质量标准**: 什么是好的输出

### 针对性优化

**Claude**:
- ✅ 使用详细的结构化说明
- ✅ 提供完整的示例
- ✅ 强调专业性和准确性
- ❌ 避免过于简短的指令

**DeepSeek**:
- ✅ 使用 Schema 定义数据结构
- ✅ 代码风格的格式要求
- ✅ 强调技术准确性
- ❌ 避免过于口语化的表达

**GPT-4**:
- ✅ 清晰的分步指令
- ✅ JSON 格式的输入
- ✅ 严格的格式规范
- ❌ 避免模糊的要求

**MiniMax**:
- ✅ 全中文表达
- ✅ 创意和情感引导
- ✅ 对话式交互
- ❌ 避免生硬的技术术语

**Gemini**:
- ✅ 结构化 JSON 输入
- ✅ 视觉场景描述
- ✅ 多维度信息整合
- ❌ 避免单一维度的要求

## 性能监控

建议监控以下指标:

1. **生成质量**
   - 场景数量是否合理 (3-5个)
   - 总时长是否符合要求 (±5秒)
   - 旁白是否自然流畅
   - 操作序列是否可执行

2. **性能指标**
   - API 响应时间
   - Token 消耗量
   - 成功率
   - 错误类型

3. **成本控制**
   - 每次生成的成本
   - 日/月总成本
   - ROI 分析

## 故障排查

### 常见问题

**1. 输出格式不正确**
- 检查 Prompt 中的示例是否完整
- 增加格式约束说明
- 使用更严格的 Schema 定义

**2. 生成内容质量差**
- 检查网站分析是否完整
- 增加上下文信息
- 调整 temperature 参数 (降低随机性)

**3. API 调用失败**
- 检查 API Key 是否正确
- 检查网络连接
- 检查配额限制

**4. 成本过高**
- 考虑使用 DeepSeek 等性价比高的模型
- 优化 Prompt 长度
- 实施缓存策略

## 未来优化方向

1. **Fine-tuning**: 基于真实数据微调模型
2. **Few-shot Learning**: 提供更多高质量示例
3. **动态 Prompt**: 根据网站类型自动调整
4. **混合策略**: 不同场景使用不同模型
5. **质量评估**: 自动评分和优化系统

## 参考资源

- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [DeepSeek Platform](https://platform.deepseek.com/)
- [MiniMax API](https://api.minimax.chat/)
- [Google Gemini](https://ai.google.dev/)

## 更新日志

- 2025-12-27: 初始版本,支持 5 个 AI 提供商
- 后续根据实际测试结果持续优化

---

**维护者**: Demo Video Generator Team
**最后更新**: 2025-12-27
