# Product Hunt 官方API注册与配置指南

## 🎯 **注册步骤**

### 第一步：访问Product Hunt API开发者页面
```
https://api.producthunt.com/v2/oauth/applications
```

### 第二步：登录Product Hunt账号
- 如果还没有Product Hunt账号，需要先注册：https://www.producthunt.com/
- 使用现有账号登录

### 第三步：创建OAuth应用
点击 **"New Application"** 按钮，填写应用信息：

```
应用名称: Social Trend Analyzer
应用描述: AI-powered social media trend analysis platform for entrepreneurs and startups
应用网站: https://localhost:8000 (开发期间)
回调URL: https://localhost:8000/auth/callback
```

⚠️ **重要**: Product Hunt要求HTTPS重定向URI，请使用以下解决方案之一：

#### 方案A: 使用ngrok创建HTTPS隧道（推荐）
```bash
# 1. 安装ngrok: https://ngrok.com/download
# 2. 启动本地服务器 (8000端口)
# 3. 在另一个终端运行:
ngrok http 8000

# 4. 复制显示的HTTPS URL，例如:
# https://abc123.ngrok.io
```

然后在Product Hunt中使用：
```
回调URL: https://abc123.ngrok.io/auth/callback
```

#### 方案B: 使用在线测试地址
如果您已有在线部署，直接使用：
```
回调URL: https://your-domain.com/auth/callback
```

#### 方案C: 使用可选的假地址（仅测试）
```
回调URL: https://example.com/auth/callback
```
注：这个方案只能用于获取API凭证，实际测试需要修改为真实地址

### 第四步：获取API凭证
创建成功后，您会获得：

```
Client ID: (类似 abc123def456...)
Client Secret: (类似 xyz789uvw012...)
```

## 🔧 **配置环境变量**

在您的 `.env` 文件中添加以下配置：

```bash
# Product Hunt 官方API配置
PRODUCT_HUNT_CLIENT_ID=your_client_id_here
PRODUCT_HUNT_CLIENT_SECRET=your_client_secret_here
PRODUCT_HUNT_REDIRECT_URI=http://localhost:8000/auth/callback
```

## 📊 **API配额和限制**

### 免费配额
- **1000次请求/月** (足够初期使用)
- **GraphQL API** (灵活查询)
- **实时数据** (产品发布信息)

### 速率限制
- **每秒1次请求** (避免触发限制)
- **每分钟60次请求**
- **每小时1000次请求**

## ✅ **验证配置**

### 测试脚本
运行以下命令验证API连接：

```bash
cd backend
python test_product_hunt_api.py
```

### 手动验证
访问以下URL确认应用创建成功：
```
https://api.producthunt.com/v2/oauth/applications
```

## 📋 **API功能概述**

### 核心功能
1. **每日产品列表** - 获取Product Hunt每日发布的产品
2. **产品搜索** - 根据关键词搜索相关产品
3. **产品详情** - 获取产品的完整信息
4. **热门话题** - 获取当前热门的产品类别
5. **创作者信息** - 获取产品制作者信息

### 数据字段
```json
{
  "id": "产品ID",
  "name": "产品名称",
  "tagline": "产品口号",
  "description": "产品描述",
  "website": "产品网站",
  "votesCount": "投票数",
  "commentsCount": "评论数",
  "makers": ["制作者列表"],
  "topics": ["产品类别"],
  "thumbnail": "产品截图"
}
```

## 🚨 **常见问题排查**

### 问题1: 无法创建应用
**原因**: 需要先有Product Hunt账号
**解决**: 访问 https://www.producthunt.com/ 注册账号

### 问题2: API调用失败 (401错误)
**原因**: Client ID或Secret错误
**解决**: 重新检查 `.env` 文件中的凭证

### 问题3: 超过API配额 (429错误)
**原因**: 超过月度1000次限制
**解决**: 等待下月重置或联系Product Hunt升级

### 问题4: GraphQL查询错误
**原因**: 查询语法错误
**解决**: 参考官方文档：https://api.producthunt.com/v2/docs

## 🎯 **对您项目的价值**

### 创业者用户群体刚需
- ✅ **竞品监控**: 实时发现新产品和竞争对手
- ✅ **市场趋势**: 了解当前最热门的产品方向  
- ✅ **灵感来源**: 发现创新产品和功能
- ✅ **投资机会**: 识别获得高关注的初创产品

### 分析维度
- **产品热度**: 投票数、评论数、关注度
- **领域分布**: AI、SaaS、移动应用等类别统计
- **创作者画像**: 成功创作者的特征分析
- **发布时机**: 最佳产品发布时间分析

## 💡 **最佳实践**

1. **缓存策略**: Product Hunt数据相对稳定，可以缓存1小时
2. **批量获取**: 一次获取多天数据，减少API调用
3. **关键词匹配**: 结合用户输入的关键词过滤相关产品
4. **趋势分析**: 对比不同时期的产品热度和类别分布

## 📋 **后续集成步骤**

1. ✅ 注册API账号 (当前任务)
2. 🔄 测试API连接
3. 🔄 集成到分析服务  
4. 🔄 添加产品趋势分析功能
5. 🔄 与Reddit/Twitter数据融合分析

---

**下一步**: 完成注册后，请将获得的Client ID和Secret配置到 `.env` 文件中！