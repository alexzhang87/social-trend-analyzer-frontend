# 🔧 环境变量配置指南

## ⚡ 快速配置

### 1. 创建 .env 文件
在 `backend` 目录下创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env
```

### 2. 配置Reddit API（✅ 已完成注册）
在 `.env` 文件中更新：

```bash
# Reddit 官方API - ✅ 已注册成功
REDDIT_CLIENT_ID=hH0BEEYddOeBpKMO-2GH_A
REDDIT_CLIENT_SECRET=2l2t5XyqAxIGSJMLLGAGjlct1DBmmA
REDDIT_USERNAME=你的Reddit用户名
REDDIT_PASSWORD=你的Reddit密码
```

### 3. 测试Reddit API
运行测试脚本：

```bash
cd backend
python test_reddit_api.py
```

## 📋 必需的环境变量

### 核心配置
```bash
# 数据库
DATABASE_URL=sqlite:///./app.db

# JWT认证
SECRET_KEY=your-secret-key-here

# LLM服务（智谱AI）
ZHIPU_API_KEY=your_zhipu_api_key_here
```

### 数据源API
```bash
# Twitter (现有)
TWITTERAPI_IO_KEY=your_twitter_io_api_key_here

# Reddit (✅ 已配置)
REDDIT_CLIENT_ID=hH0BEEYddOeBpKMO-2GH_A
REDDIT_CLIENT_SECRET=2l2t5XyqAxIGSJMLLGAGjlct1DBmmA
REDDIT_USERNAME=你的用户名
REDDIT_PASSWORD=你的密码
```

## 🚀 下一步

1. ✅ Reddit API已注册
2. 🔄 配置.env文件中的用户名密码
3. 🔄 运行测试脚本
4. 🔄 注册Product Hunt API
5. 🔄 集成到分析服务

## ⚠️ 重要提示

- **不要**将 `.env` 文件提交到Git仓库
- 确保 `.gitignore` 包含 `.env`
- Reddit密码建议使用应用专用密码
- 定期轮换API密钥保证安全

---

**下一步**: 请在 `.env` 文件中填入您的Reddit用户名和密码，然后运行测试！