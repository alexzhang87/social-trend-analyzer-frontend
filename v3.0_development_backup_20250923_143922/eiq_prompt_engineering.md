# EIQ Platform AI分析Prompt工程方案

## 核心分析Prompt模板

### 主分析Prompt (版本1.0)
```
你是一位资深的商业趋势分析师和创业导师，拥有10年以上的市场研究经验。现在需要你基于社交媒体数据，为创业者提供具有执行价值的商业洞察。

**分析目标关键词**: ${keyword}
**时间范围**: ${timeRange}
**数据来源**: ${platforms}

**原始数据**:
${rawData}

**分析要求**:
请严格按照以下JSON格式输出，每个字段都必须包含实质性内容：

{
  "trends": {
    "direction": "上升|下降|平稳|波动",
    "strength": "强烈|中等|微弱",
    "timeline_analysis": "详细描述时间趋势变化，包含具体数据支撑",
    "key_drivers": ["驱动因素1", "驱动因素2", "驱动因素3"],
    "confidence_level": "高|中|低"
  },
  "pain_points": [
    {
      "title": "简洁有力的痛点标题",
      "description": "详细描述用户面临的具体问题",
      "evidence": "来自数据的具体证据，包含用户原话摘要",
      "frequency_score": "1-10分的频繁程度评分",
      "severity_score": "1-10分的严重程度评分",
      "target_user": "受此痛点影响的主要用户群体"
    }
  ],
  "opportunities": [
    {
      "title": "清晰的商机标题",
      "description": "详细的商机描述和实现路径",
      "market_validation": "市场验证的证据和理由",
      "estimated_market_size": "市场规模的合理估算",
      "competition_level": "竞争激烈程度评估",
      "difficulty_score": "1-10分的实现难度评分",
      "revenue_potential": "收入潜力评估(低|中|高)",
      "time_to_market": "预估上市时间"
    }
  ],
  "mvp_plan": {
    "core_concept": "MVP的核心概念和价值主张",
    "target_audience": "明确的目标用户画像",
    "key_features": ["核心功能1", "核心功能2", "核心功能3"],
    "week_plan": [
      {"days": "1-2", "phase": "阶段名称", "tasks": ["具体任务1", "具体任务2"], "deliverables": "交付物"},
      {"days": "3-4", "phase": "阶段名称", "tasks": ["具体任务1", "具体任务2"], "deliverables": "交付物"},
      {"days": "5-7", "phase": "阶段名称", "tasks": ["具体任务1", "具体任务2"], "deliverables": "交付物"}
    ],
    "validation_metrics": ["可量化的验证指标1", "可量化的验证指标2"],
    "budget_estimate": "预估开发成本范围",
    "risk_factors": ["主要风险因素1", "主要风险因素2"]
  },
  "actionable_insights": [
    "立即可执行的建议1",
    "立即可执行的建议2", 
    "立即可执行的建议3"
  ]
}

**重要提醒**:
1. 所有分析必须基于提供的真实数据，不能凭空推测
2. 痛点必须是从数据中真实提取的用户问题
3. 商机必须具备可行性和商业价值
4. MVP计划必须具体可执行，避免空泛描述
5. 如果数据不足，请在相应字段中注明"数据不足，需要更多信息"
```

### 数据预处理Prompt
```
请对以下社交媒体原始数据进行清理和预处理，为后续商业分析做准备：

**原始数据**: ${rawData}

**处理要求**:
1. 去除明显的垃圾信息和广告
2. 识别并标记情感倾向（积极/消极/中性）
3. 提取关键主题和讨论点
4. 统计高频词汇和短语
5. 识别有价值的用户反馈和需求表达

**输出格式**:
{
  "cleaned_data": [
    {
      "content": "清理后的内容",
      "sentiment": "积极|消极|中性",
      "themes": ["主题1", "主题2"],
      "engagement": {"likes": 数字, "shares": 数字, "comments": 数字},
      "user_type": "普通用户|意见领袖|专家|品牌",
      "relevance_score": "1-10分的相关性评分"
    }
  ],
  "summary_stats": {
    "total_posts": "总数",
    "sentiment_distribution": {"positive": %, "negative": %, "neutral": %},
    "top_themes": ["主题1", "主题2", "主题3"],
    "high_frequency_terms": {"词汇": 频次}
  }
}
```

## 分阶段测试Prompt

### A/B测试方案

#### 版本A: 详细分析型
- 优点: 分析深入，信息全面
- 缺点: 可能过于复杂，处理时间长
- 适用: 专业用户，深度分析需求

#### 版本B: 精简实用型  
- 优点: 结果简洁，易于理解
- 缺点: 可能缺少深度洞察
- 适用: 快速决策，初级用户

#### 版本C: 行动导向型
- 优点: 强调可执行性
- 缺点: 可能忽略复杂市场因素
- 适用: 急需启动项目的创业者

### 测试指标
```
评估维度:
1. 准确性 (1-10分) - AI分析与实际市场情况的匹配度
2. 实用性 (1-10分) - 建议的可执行程度  
3. 创新性 (1-10分) - 洞察的独特性和启发性
4. 完整性 (1-10分) - 分析覆盖的全面程度
5. 处理速度 - 从输入到输出的时间

目标基准:
- 准确性 > 7分
- 实用性 > 8分
- 处理时间 < 60秒
- 用户满意度 > 80%
```

## 优化迭代策略

### 第一轮优化: 基础功能验证
```
测试关键词: ["AI玩具", "智能家居", "在线教育", "SaaS工具", "电商平台"]
数据量: 每个关键词500-1000条
优化重点: 
- Prompt准确性调优
- 输出格式统一
- 错误处理完善
```

### 第二轮优化: 行业特化
```
不同行业使用不同的分析框架:
- B2B SaaS: 强调企业需求和付费意愿
- 消费品: 重视用户体验和市场规模  
- 服务业: 关注服务痛点和操作效率
- 内容创作: 突出创意和变现方式
```

### 第三轮优化: 个性化调整
```
根据用户画像调整输出:
- 技术背景: 详细技术实现建议
- 商业背景: 强调商业模式和盈利
- 设计背景: 重视用户体验和界面
- 运营背景: 突出推广和增长策略
```

## 质量控制机制

### 自动质量检查
```python
# 伪代码示例
def quality_check(ai_output):
    checks = {
        "json_format_valid": validate_json_structure(ai_output),
        "required_fields_present": check_required_fields(ai_output),
        "content_length_adequate": check_content_length(ai_output),
        "pain_points_count": len(ai_output.pain_points) >= 3,
        "opportunities_count": len(ai_output.opportunities) >= 2,
        "mvp_plan_detailed": check_mvp_completeness(ai_output)
    }
    
    quality_score = sum(checks.values()) / len(checks)
    return quality_score > 0.8
```

### 人工审核标准
```
审核checklist:
□ 痛点是否基于真实数据
□ 商机是否具备可行性  
□ MVP计划是否具体可执行
□ 分析逻辑是否合理
□ 语言表达是否清晰
□ 数据引用是否准确
```

## 成本优化方案

### Token使用优化
```
策略:
1. 数据预处理: 只传递高价值内容给AI
2. 分阶段分析: 先概览后深入
3. 模板复用: 减少重复prompt内容  
4. 缓存结果: 相似查询复用分析结果

预估Token使用:
- 数据预处理: 2,000 tokens
- 主分析过程: 5,000 tokens  
- 输出生成: 3,000 tokens
- 单次分析总计: ~10,000 tokens
```

### 备用LLM方案
```
主力: GPT-4o-mini ($0.15/1M input, $0.6/1M output)
备选1: Claude 3.5 Haiku ($0.25/1M input, $1.25/1M output)  
备选2: Llama 3.1 70B via Groq (免费但限速)
```

## 持续改进计划

### 用户反馈收集
```
反馈机制:
1. 每次分析后的5星评分
2. 具体改进建议收集
3. 用户使用行为分析
4. 定期用户访谈

改进周期: 每2周一次prompt优化迭代
```