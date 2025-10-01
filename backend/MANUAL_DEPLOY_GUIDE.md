# Railway 手动部署指南 - 5分钟快速部署

## 方法1：网页控制台部署（最简单）

### 步骤1：准备代码
1. 打开 https://railway.com 并登录
2. 点击 "New Project" → "Empty Project"
3. 给项目命名：`ai-data-collector`

### 步骤2：添加服务
1. 在项目中点击 "Add Service" → "Empty Service"
2. 命名服务：`backend`

### 步骤3：连接代码
1. 在服务设置中，点击 "Connect Repo"
2. 如果没有GitHub，可以使用Railway CLI：
   ```bash
   cd C:\Users\zhang\Desktop\2\backend
   railway login
   railway link [项目ID]
   railway up
   ```

### 步骤4：配置环境变量
在Railway控制台的Variables标签页添加：
```
PORT=8000
PYTHONPATH=/app
ENVIRONMENT=production
DATA_COLLECTION_ENABLED=true
COLLECTION_INTERVAL_HOURS=6
MAX_DAILY_COLLECTIONS=4
QUALITY_THRESHOLD=0.7
```

### 步骤5：配置部署设置
在Settings标签页设置：
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python model_training/master_data_scheduler.py`
- **Healthcheck Path**: `/health`

## 方法2：使用Railway CLI（最快）

### 快速命令序列：
```bash
# 1. 进入项目目录
cd C:\Users\zhang\Desktop\2\backend

# 2. 登录Railway（如果还没登录）
railway login

# 3. 创建新项目
railway init

# 4. 设置环境变量
railway variables --set PORT=8000
railway variables --set PYTHONPATH=/app
railway variables --set ENVIRONMENT=production
railway variables --set DATA_COLLECTION_ENABLED=true
railway variables --set COLLECTION_INTERVAL_HOURS=6
railway variables --set MAX_DAILY_COLLECTIONS=4
railway variables --set QUALITY_THRESHOLD=0.7

# 5. 部署
railway up
```

## 方法3：GitHub集成（最稳定）

### 步骤1：推送到GitHub
```bash
cd C:\Users\zhang\Desktop\2\backend
git init
git add .
git commit -m "Initial commit"
git remote add origin [你的GitHub仓库URL]
git push -u origin main
```

### 步骤2：在Railway连接GitHub
1. 在Railway控制台选择 "Deploy from GitHub repo"
2. 选择你的仓库
3. 设置环境变量（同上）
4. 自动部署完成

## 常见问题解决

### 问题1：文件太大
确保 `.gitignore` 文件包含：
```
collected_data/
model_outputs/
*.json
*.csv
*.pth
```

### 问题2：Dockerfile路径错误
检查 `railway.toml` 文件：
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"
```

### 问题3：端口配置
确保在代码中使用环境变量：
```python
port = int(os.environ.get("PORT", 8000))
```

## 预计部署时间
- 网页控制台：3-5分钟
- Railway CLI：2-3分钟  
- GitHub集成：5-8分钟

## 部署成功标志
- Railway控制台显示绿色"Active"状态
- 可以访问健康检查端点：`https://[你的域名]/health`
- 日志显示"数据收集系统启动成功"

## 紧急联系
如果遇到问题，可以：
1. 查看Railway控制台的Build Logs
2. 检查Runtime Logs
3. 使用 `railway logs` 命令查看实时日志