# Railway 部署检查清单

## ✅ 部署前检查

### 1. 文件准备
- [x] `railway.toml` - Railway配置文件
- [x] `backend/Dockerfile` - Docker构建文件
- [x] `backend/requirements.txt` - Python依赖
- [x] `.env.railway` - Railway环境变量模板
- [x] `deploy-railway.ps1` - PowerShell部署脚本
- [x] `deploy-railway.bat` - 批处理部署脚本
- [x] `railway_init.py` - 数据库初始化脚本
- [x] `railway_health_check.py` - 健康检查脚本

### 2. 环境依赖
- [ ] Node.js (v16+) 已安装
- [ ] Railway CLI 已安装
- [ ] 网络连接正常

### 3. API密钥准备
- [ ] ZHIPU_API_KEY (智谱AI) - **必需**
- [ ] SECRET_KEY (JWT密钥) - **必需**
- [ ] TWITTERAPI_IO_KEY (Twitter API) - 可选
- [ ] OPENAI_API_KEY (OpenAI) - 可选

## 🚀 部署步骤

### 快速部署 (推荐)
```powershell
# 运行自动化脚本
.\deploy-railway.ps1
```

### 手动部署
1. **安装CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **登录Railway**
   ```bash
   railway login
   ```

3. **初始化项目**
   ```bash
   railway init
   ```

4. **添加服务 (可选)**
   ```bash
   railway add postgresql  # 数据库
   railway add redis       # 缓存
   ```

5. **设置环境变量**
   ```bash
   railway variables set ZHIPU_API_KEY=your_key
   railway variables set SECRET_KEY=your_secret
   ```

6. **部署**
   ```bash
   railway up
   ```

## 🔍 部署后验证

### 1. 检查部署状态
```bash
railway status
```

### 2. 查看应用URL
```bash
railway domain
```

### 3. 检查日志
```bash
railway logs
```

### 4. 健康检查
```bash
# 访问根路径
curl https://your-app.railway.app/

# 检查API文档
curl https://your-app.railway.app/docs

# 运行健康检查脚本
railway run python railway_health_check.py
```

### 5. 初始化数据库 (如果需要)
```bash
railway run python railway_init.py
```

## ⚠️ 常见问题

### 部署失败
- 检查 `railway logs` 查看错误详情
- 确认环境变量设置正确
- 验证Dockerfile语法

### 健康检查失败
- 确认应用正确启动
- 检查端口配置
- 查看应用日志

### 数据库连接问题
- 确认已添加PostgreSQL服务
- 检查DATABASE_URL环境变量
- 验证数据库初始化

### API密钥问题
- 确认所有必需的API密钥已设置
- 检查密钥格式和有效性
- 验证权限和配额

## 📊 监控和维护

### 查看实时日志
```bash
railway logs --follow
```

### 重新部署
```bash
railway up
```

### 查看环境变量
```bash
railway variables
```

### 连接数据库
```bash
railway connect postgresql
```

### 打开控制台
```bash
railway open
```

## 🎯 成功标准

部署成功的标志：
- [ ] `railway status` 显示服务运行中
- [ ] 应用URL可访问并返回欢迎消息
- [ ] `/docs` 端点显示API文档
- [ ] 日志中无严重错误
- [ ] 健康检查通过

## 📞 获取帮助

- Railway文档: https://docs.railway.app/
- 项目仓库: 查看README和文档
- 技术支持: 检查日志和错误信息