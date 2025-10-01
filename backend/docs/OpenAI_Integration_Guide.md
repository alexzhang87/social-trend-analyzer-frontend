# OpenAI GPT 系列模型接入指南

## 概述

本系统已完成 OpenAI GPT 系列模型的技术集成，支持 GPT-3.5-turbo、GPT-4 和 GPT-4-turbo 模型作为智谱AI的备用选择。

## 配置步骤

### 1. 安装依赖

```bash
pip install openai
```

### 2. 获取 API 密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API 密钥

### 3. 环境配置

在 `.env` 文件中添加以下配置：

```env
# OpenAI API 配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_ORGANIZATION=org-your-organization-id  # 可选
```

### 4. 模型映射策略

系统根据用户订阅等级自动选择模型：

| 用户等级 | OpenAI 模型 | 智谱AI 备用模型 |
|---------|------------|---------------|
| Free | glm-3-turbo | glm-3-turbo |
| Pro | gpt-3.5-turbo | glm-4 |
| Plus | gpt-4-turbo | glm-4 |
| Enterprise | gpt-4 | glm-4 |

## 技术实现

### 1. 客户端初始化

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    organization=settings.OPENAI_ORGANIZATION
)
```

### 2. 智能降级机制

- 优先使用 OpenAI 模型（如果配置且可用）
- 自动降级到智谱AI模型
- 最终降级到本地回退响应

### 3. 流式响应支持

支持 OpenAI 的流式响应，提供实时对话体验：

```python
async for chunk in stream:
    if chunk.choices[0].delta.content:
        yield {
            "type": "content",
            "content": chunk.choices[0].delta.content,
            "model": model
        }
```

## 成本控制

### 1. 模型选择策略

- **免费用户**: 仅使用智谱AI模型
- **付费用户**: 根据等级使用相应的OpenAI模型
- **企业用户**: 使用最高级的GPT-4模型

### 2. Token 限制

| 模型 | 最大Token数 | 建议用途 |
|------|------------|---------|
| gpt-3.5-turbo | 3,000 | 日常对话、简单分析 |
| gpt-4-turbo | 4,000 | 复杂分析、专业咨询 |
| gpt-4 | 4,000 | 高级策略、深度分析 |

### 3. 费用预估

- **GPT-3.5-turbo**: ~$0.002/1K tokens
- **GPT-4-turbo**: ~$0.01/1K tokens  
- **GPT-4**: ~$0.03/1K tokens

## 监控和日志

### 1. 使用统计

系统自动记录：
- 模型使用次数
- Token 消耗量
- 响应时间
- 错误率

### 2. 成本追踪

```python
response_data["metadata"] = {
    "model": model,
    "tokens": {
        "prompt": response.usage.prompt_tokens,
        "completion": response.usage.completion_tokens,
        "total": response.usage.total_tokens
    },
    "estimated_cost": calculate_cost(model, total_tokens)
}
```

## 安全考虑

### 1. API 密钥保护

- 使用环境变量存储密钥
- 定期轮换 API 密钥
- 监控异常使用模式

### 2. 内容过滤

- 实施输入内容检查
- 遵循 OpenAI 使用政策
- 记录敏感内容处理

## 故障处理

### 1. 自动降级

```
OpenAI API 不可用 → 智谱AI → 本地回退响应
```

### 2. 错误处理

- API 限流: 自动重试机制
- 网络错误: 切换到备用模型
- 认证失败: 记录错误并降级

## 部署建议

### 1. 生产环境

- 设置合理的 rate limiting
- 配置监控告警
- 准备成本预算

### 2. 测试环境

- 使用较低成本的模型
- 限制 Token 使用量
- 模拟各种故障场景

## 总结

通过本集成方案，系统具备了：

✅ **多模型支持**: OpenAI + 智谱AI + 本地回退  
✅ **智能选择**: 基于用户等级的模型分配  
✅ **成本控制**: Token限制和使用监控  
✅ **高可用性**: 多层降级机制  
✅ **流式响应**: 实时对话体验  

系统现已具备生产环境部署条件，可根据业务需求灵活配置使用。