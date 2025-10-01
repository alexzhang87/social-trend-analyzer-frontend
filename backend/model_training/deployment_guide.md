# 🚀 AI产品训练数据自动收集系统 - 部署指南

## 📋 系统概述

本系统是一个企业级的自动化数据收集平台，专为AI产品训练设计，能够：

- **大规模数据收集**: 每日自动收集数万条高质量数据
- **多源数据整合**: 整合Reddit、GitHub、Twitter、Product Hunt等平台数据
- **智能质量控制**: 自动评估和过滤数据质量
- **24/7自动运行**: 支持云端部署，假期期间持续收集
- **数据标注清洗**: 自动专家类型分类和质量评分

## 🎯 数据收集目标

- **每日API数据**: 5,000+ 条真实数据
- **每周HF数据**: 20,000+ 条补充数据  
- **质量阈值**: ≥ 0.7 分
- **专家类型**: 商业策略、用户体验、市场研究、技术分析等

## 📁 系统架构

```
backend/model_training/
├── enterprise_data_collector.py    # 企业级数据收集器
├── reddit_collector.py            # Reddit数据收集器
├── github_collector.py            # GitHub数据收集器  
├── twitter_collector.py           # Twitter数据收集器
├── huggingface_data_integrator.py # Hugging Face数据集成器
├── master_data_scheduler.py       # 主调度器
├── cloud_deployment.py           # 云端部署配置
├── test_collectors.py            # 收集器测试
├── .env.template                 # 环境变量模板
└── deployment_guide.md           # 本部署指南
```

## 🔧 快速部署步骤

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 创建环境变量文件
cp .env.template .env
```

### 2. API密钥配置

编辑 `.env` 文件，填入以下API密钥：

```env
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name

# GitHub API  
GITHUB_TOKEN=your_github_token

# Twitter API
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Product Hunt API
PRODUCTHUNT_ACCESS_TOKEN=your_producthunt_token
```

### 3. 本地测试

```bash
# 测试所有收集器
python test_collectors.py

# 测试Hugging Face集成
python huggingface_data_integrator.py

# 运行完整收集流程
python master_data_scheduler.py
```

### 4. 云端部署

#### 选项A: AWS部署

```bash
# 生成AWS配置
python cloud_deployment.py --platform aws

# 部署到AWS
aws cloudformation create-stack \
  --stack-name ai-data-collector \
  --template-body file://aws-cloudformation.yaml \
  --capabilities CAPABILITY_IAM
```

#### 选项B: Docker部署

```bash
# 构建Docker镜像
docker build -t ai-data-collector .

# 运行容器
docker run -d \
  --name data-collector \
  --env-file .env \
  -v $(pwd)/collected_data:/app/collected_data \
  ai-data-collector
```

#### 选项C: Heroku部署

```bash
# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name

# 设置环境变量
heroku config:set REDDIT_CLIENT_ID=your_value
# ... 设置所有其他环境变量

# 部署
git push heroku main
```

## 🔑 API密钥获取指南

### Reddit API
1. 访问 https://www.reddit.com/prefs/apps
2. 创建新应用，选择"script"类型
3. 获取client_id和client_secret

### GitHub API
1. 访问 https://github.com/settings/tokens
2. 生成新的Personal Access Token
3. 选择适当的权限范围

### Twitter API
1. 访问 https://developer.twitter.com/
2. 申请开发者账户
3. 创建应用获取Bearer Token

### Product Hunt API
1. 访问 https://api.producthunt.com/v2/docs
2. 注册开发者账户
3. 获取访问令牌

## 📊 数据收集配置

### 收集频率设置

```python
# 在master_data_scheduler.py中配置
collection_targets = {
    "daily_api_target": 5000,     # 每日API数据目标
    "weekly_hf_target": 20000,    # 每周HF数据目标  
    "quality_threshold": 0.7,     # 质量阈值
    "max_storage_days": 30        # 数据保存天数
}
```

### 调度计划

- **每小时**: API数据收集
- **每日02:00**: 完整数据收集和合并
- **每周一**: Hugging Face数据集成
- **每日**: 数据清理和质量检查

## 🎛️ 监控和管理

### 数据库监控

系统使用SQLite数据库跟踪收集状态：

```sql
-- 查看收集记录
SELECT * FROM collection_records ORDER BY created_at DESC;

-- 查看质量统计
SELECT * FROM quality_stats ORDER BY date DESC;
```

### 日志监控

```bash
# 查看实时日志
tail -f data_collection.log

# 查看错误日志
grep ERROR data_collection.log
```

### 数据质量检查

```python
# 检查最新收集的数据
python -c "
import json
with open('collected_data/master_training_data_latest.json') as f:
    data = json.load(f)
    print(f'总记录数: {len(data)}')
    print(f'平均质量分数: {sum(item[\"quality_score\"] for item in data) / len(data):.2f}')
"
```

## 🔧 故障排除

### 常见问题

1. **API限制错误**
   - 检查API密钥是否正确
   - 确认API配额未超限
   - 调整收集频率

2. **网络连接问题**
   - 检查网络连接
   - 配置代理设置
   - 增加重试次数

3. **数据质量低**
   - 调整质量阈值
   - 优化关键词过滤
   - 检查数据源配置

### 性能优化

1. **提高收集效率**
   ```python
   # 增加并发数
   max_concurrent_requests = 10
   
   # 优化批处理大小
   batch_size = 100
   ```

2. **减少存储占用**
   ```python
   # 启用数据压缩
   compress_data = True
   
   # 定期清理旧数据
   cleanup_interval_days = 7
   ```

## 📈 扩展功能

### 添加新数据源

1. 创建新的收集器类
2. 实现标准接口方法
3. 添加到主调度器中
4. 配置相应的API密钥

### 自定义数据处理

1. 修改质量评分算法
2. 添加新的专家类型
3. 实现自定义过滤规则
4. 集成外部标注服务

## 🚀 生产环境建议

### 安全配置

- 使用环境变量存储敏感信息
- 启用HTTPS和SSL证书
- 配置防火墙和访问控制
- 定期更新依赖包

### 高可用性

- 部署多个实例
- 配置负载均衡
- 设置自动故障转移
- 实现数据备份策略

### 监控告警

- 配置Prometheus监控
- 设置Grafana仪表板
- 配置邮件/短信告警
- 监控关键指标

## 📞 技术支持

如遇到问题，请检查：

1. 📋 日志文件: `data_collection.log`
2. 📊 数据库状态: `collection_tracking.db`
3. 🔧 配置文件: `.env`
4. 📁 输出目录: `collected_data/`

---

## 🎯 预期结果

部署完成后，系统将：

- ✅ 每日自动收集5000+条API数据
- ✅ 每周整合20000+条Hugging Face数据
- ✅ 自动质量评估和专家类型分类
- ✅ 生成可直接用于AI训练的数据集
- ✅ 24/7无人值守运行

**假期回来后，您将拥有数万条高质量、已标注的训练数据，可立即开始AI模型训练！** 🚀