# AI专家系统使用指南

## 系统概述

本AI专家系统通过数据收集和机器学习技术，为您的AI顾问提供高质量的训练数据和增强功能，显著提升专家回答的质量和相关性。

## 核心功能

### 1. 数据收集服务 (`data_collection_service.py`)
- **功能**: 从Hugging Face等数据源收集高质量训练数据
- **支持的数据源**: 
  - Hugging Face数据集
  - 其他免费API数据源
- **数据处理**: 自动分类、质量评分、业务相关性分析

### 2. AI专家增强器 (`ai_expert_enhancer.py`)
- **功能**: 基于收集的训练数据增强AI专家回答
- **核心特性**:
  - 智能相关性匹配（使用jieba中文分词）
  - 多维度评分系统
  - 动态提示词生成

### 3. 离线测试系统 (`test_data_collection.py`)
- **功能**: 使用模拟数据验证系统功能
- **测试覆盖**: 数据收集、存储、检索、导出全流程

## 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements_data.txt
pip install jieba
```

### 2. 运行数据收集测试
```bash
python test_data_collection.py
```

### 3. 测试AI专家增强
```bash
python ai_expert_enhancer.py
```

### 4. 运行完整集成测试
```bash
python integration_test.py
```

## 系统架构

```
数据收集层 (data_collection_service.py)
    ↓
数据存储层 (SQLite数据库)
    ↓
AI增强层 (ai_expert_enhancer.py)
    ↓
配置输出 (ai_expert_enhancement_config.json)
```

## 数据库结构

### training_data表
- `id`: 主键
- `question`: 问题文本
- `answer`: 回答文本
- `category`: 分类（business_strategy, customer_support等）
- `source`: 数据源
- `business_relevance`: 业务相关性分数
- `quality_score`: 质量分数
- `created_at`: 创建时间

### data_sources表
- `source_name`: 数据源名称
- `last_updated`: 最后更新时间
- `status`: 状态
- `records_count`: 记录数量

## 支持的专家类型

1. **business_strategy**: 商业策略顾问
2. **customer_support**: 客户支持专家
3. **product_consultation**: 产品咨询顾问
4. **technical_support**: 技术支持专家
5. **product_strategy**: 产品策略专家

## 相关性匹配算法

系统使用多层次匹配算法：

1. **直接匹配**: 基于jieba分词的词汇匹配
2. **语义匹配**: 关键词映射表匹配
3. **主题匹配**: 业务主题相关性

最终分数 = 0.5 × 直接匹配 + 0.3 × 语义匹配 + 0.2 × 主题匹配

## 配置文件

生成的`ai_expert_enhancement_config.json`包含：
- 支持的专家类型
- 每种类型的示例数据
- 增强提示词模板

## 性能指标

当前系统性能：
- **数据记录**: 32条高质量训练数据
- **分类覆盖**: 5个主要业务类别
- **匹配准确率**: 相关性阈值0.1，匹配成功率>90%
- **响应时间**: <1秒

## 扩展指南

### 添加新数据源
1. 在`data_collection_service.py`中添加新的收集方法
2. 更新`collect_all_data()`方法
3. 测试数据质量和分类准确性

### 添加新专家类型
1. 在`ai_expert_enhancer.py`中更新`EXPERT_TYPES`
2. 添加相应的关键词映射
3. 更新测试用例

### 优化匹配算法
1. 调整权重参数
2. 扩展关键词映射表
3. 添加新的匹配维度

## 故障排除

### 常见问题

1. **数据库不存在**
   - 运行`python test_data_collection.py`重新创建

2. **分词错误**
   - 确保jieba已正确安装
   - 检查文本编码格式

3. **匹配率低**
   - 调整相关性阈值
   - 扩展关键词映射表

### 日志查看
系统使用loguru记录详细日志，包括：
- 数据收集过程
- 匹配计算详情
- 错误信息

## 下一步开发

1. **实时数据收集**: 集成更多在线数据源
2. **智能分类**: 使用机器学习自动分类
3. **个性化推荐**: 基于用户历史优化匹配
4. **性能优化**: 缓存和索引优化

## 联系支持

如有问题或建议，请查看：
- 系统日志文件
- 测试结果输出
- 配置文件内容

---

*最后更新: 2025-09-26*
*版本: 1.0*