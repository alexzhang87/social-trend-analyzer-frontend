# Railway 部署指南

## 快速部署步骤

### 1. 准备工作
- 确保您有 GitHub 账号
- 将项目代码推送到 GitHub 仓库

### 2. 注册 Railway
1. 访问 https://railway.app/
2. 点击 "Start a New Project"
3. 使用 GitHub 账号登录

### 3. 部署项目
1. 在 Railway 控制台点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择您的项目仓库
4. Railway 会自动检测到 `backend/` 目录中的 `Dockerfile`

### 4. 配置环境变量
在 Railway 项目设置中添加以下环境变量：

```
ZHIPU_API_KEY=20d51328521b417b9026bc3e6e04d3cf.DL58xDyQFs8H0cAD
TWITTERAPI_IO_KEY=f2a68513bbac4f56a24afe7f655b4e6e
DATABASE_URL=sqlite:///./app.db
PROJECT_NAME=Social Trend Analyzer
API_V1_STR=/api/v1
USE_MOCK_DATA=false
USE_PROXY=false
```

### 5. 部署完成
- Railway 会自动构建和部署
- 部署完成后，您会获得一个类似 `https://your-app-name.railway.app` 的 URL
- API 端点将是：`https://your-app-name.railway.app/api/v1/analyze-trends/`

### 6. 更新前端配置
将前端中的 API 地址更新为 Railway 提供的 URL：

```typescript
// 在 trend-analyzer.tsx 中
const response = await fetch(`https://your-app-name.railway.app/api/v1/analyze-trends/?query=${encodeURIComponent(query)}`, {
  method: 'GET',
});
```

## 验证部署

### 检查健康状态
访问：`https://your-app-name.railway.app/health`
应该返回：`{"status": "healthy"}`

### 测试 API
访问：`https://your-app-name.railway.app/docs`
可以看到 FastAPI 自动生成的 API 文档

### 测试趋势分析
在 API 文档中测试 `/api/v1/analyze-trends/` 端点

## 常见问题

### Q: 部署失败怎么办？
A: 检查 Railway 的构建日志，通常是依赖安装或环境变量配置问题

### Q: API 调用超时？
A: Railway 免费层有 500MB RAM 限制，LLM 分析可能需要时间，可以考虑升级到付费层

### Q: 如何查看日志？
A: 在 Railway 控制台的 "Deployments" 标签页可以查看实时日志

### Q: 如何更新代码？
A: 推送代码到 GitHub，Railway 会自动重新部署

## 成本估算
- **免费层**: $0/月，但有使用限制
- **Hobby 层**: $5/月，适合开发和小规模使用
- **Pro 层**: $20/月，适合生产环境

## 下一步
部署成功后，您可以：
1. 测试 Twitter API 的稳定性
2. 验证 LLM 分析功能
3. 考虑将前端也部署到 Railway 或其他平台
4. 根据使用情况决定是否迁移到 AWS/GCP