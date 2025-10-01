# Railway 快速部署指南

## 🚀 一键部署

### 方法1: 使用自动化脚本 (推荐)

```bash
# PowerShell版本 (推荐)
.\deploy-railway.ps1

# 或者批处理版本
.\deploy-railway.bat
```

### 方法2: 手动部署

1. **安装依赖**
   ```bash
   # 安装Node.js (如果未安装)
   winget install OpenJS.NodeJS
   
   # 安装Railway CLI
   npm install -g @railway/cli
   ```

2. **登录和初始化**
   ```bash
   railway login
   railway init
   ```

3. **添加服务 (可选)**
   ```bash
   # 添加PostgreSQL数据库
   railway add postgresql
   
   # 添加Redis缓存
   railway add redis
   ```

4. **设置环境变量**
   ```bash
   # 必需的环境变量
   railway variables set ZHIPU_API_KEY=your_zhipu_api_key
   railway variables set SECRET_KEY=your_secret_key_here
   
   # 可选的环境变量
   railway variables set TWITTERAPI_IO_KEY=your_twitter_api_key
   railway variables set OPENAI_API_KEY=your_openai_api_key
   ```

5. **部署**
   ```bash
   railway up
   ```

## 📋 必需的环境变量

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `ZHIPU_API_KEY` | 智谱AI API密钥 | ✅ |
| `SECRET_KEY` | JWT密钥 | ✅ |
| `TWITTERAPI_IO_KEY` | Twitter API密钥 | ❌ |
| `OPENAI_API_KEY` | OpenAI API密钥 | ❌ |

## 🔧 部署后操作

1. **获取应用URL**
   ```bash
   railway domain
   ```

2. **查看部署状态**
   ```bash
   railway status
   ```

3. **查看日志**
   ```bash
   railway logs
   railway logs --follow  # 实时日志
   ```

4. **初始化数据库 (如果需要)**
   ```bash
   railway run python railway_init.py
   ```

5. **健康检查**
   ```bash
   railway run python railway_health_check.py
   ```

## 🛠️ 常用命令

```bash
# 打开Railway控制台
railway open

# 重新部署
railway up

# 查看环境变量
railway variables

# 连接到数据库
railway connect postgresql

# 连接到Redis
railway connect redis
```

## ⚠️ 注意事项

1. 确保已安装Node.js (v16+)
2. 确保网络连接正常
3. 首次部署可能需要几分钟时间
4. 数据库和Redis服务会自动配置连接URL

## 🆘 故障排除

- **部署失败**: 检查 `railway logs` 查看详细错误
- **环境变量问题**: 使用 `railway variables` 检查设置
- **数据库连接问题**: 确保已添加PostgreSQL服务
- **健康检查失败**: 检查应用是否正确启动

## 📞 获取帮助

- Railway文档: https://docs.railway.app/
- 查看项目状态: `railway status`
- 查看服务日志: `railway logs`