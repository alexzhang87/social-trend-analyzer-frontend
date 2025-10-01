# IdeaEden 2.0 启动指南

## 📋 系统概述

**IdeaEden** 是一个基于 FastAPI + React 的社交趋势分析平台，提供实时数据分析、用户管理和智能洞察功能。

### 技术栈
- **后端**：FastAPI + Python 3.8+
- **前端**：React 18 + TypeScript + Vite
- **数据库**：SQLite (开发) / PostgreSQL (生产)
- **缓存**：Redis
- **认证**：JWT Token

## 🚀 快速启动

### 前置要求

确保系统已安装以下软件：
- **Python 3.8+**
- **Node.js 16+**
- **npm 或 yarn**
- **Redis** (可选，用于缓存)

### 1. 环境配置

#### 创建环境变量文件

在项目根目录创建 `.env` 文件：

```bash
# 复制示例配置文件
cp backend/.env.example .env
```

#### 基础配置示例

```env
# 数据库配置
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379

# JWT认证
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 管理员账号（重要！）
ADMIN_EMAIL=admin@ideaeden.com
ADMIN_PASSWORD=admin123456

# LLM服务（智谱AI GLM-4.5）
ZHIPU_API_KEY=your_zhipu_api_key_here

# 社交媒体API
TWITTERAPI_IO_KEY=your_twitter_io_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

### 2. 后端启动

#### 方式一：标准启动（推荐）

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境（首次运行）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖（首次运行）
pip install -r requirements.txt

# 5. 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 方式二：开发模式启动

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 启动开发服务器（自动重载）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 方式三：生产模式启动

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 启动生产服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 后端启动验证

启动成功后，访问以下地址验证：

- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/api/v1/health
- **API根路径**：http://localhost:8000/

### 3. 前端启动

#### 方式一：开发模式启动（推荐）

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（首次运行）
npm install
# 或使用 yarn
yarn install

# 3. 启动开发服务器
npm run dev
# 或使用 yarn
yarn dev
```

#### 方式二：预览模式启动

```bash
# 进入前端目录
cd frontend

# 构建项目
npm run build

# 预览构建结果
npm run preview
```

#### 前端启动验证

启动成功后，访问：

- **前端应用**：http://localhost:5173
- **构建预览**：http://localhost:4173 (preview模式)

### 4. 完整启动流程

#### 推荐启动顺序

1. **启动Redis**（如果使用缓存）
   ```bash
   redis-server
   ```

2. **启动后端**
   ```bash
   cd backend
   venv\Scripts\activate
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **启动前端**
   ```bash
   cd frontend
   npm run dev
   ```

#### 验证系统运行

- 后端API：http://localhost:8000/docs
- 前端应用：http://localhost:5173
- 系统健康：http://localhost:8000/api/v1/health

## 👤 管理员登录指南

### 默认管理员账号

系统首次启动时会自动创建默认管理员账号：

```
邮箱：admin@ideaeden.com
密码：admin123456
用户名：admin
角色：系统管理员
权限：完全访问权限
```

> ⚠️ **安全提醒**：生产环境中请立即修改默认密码！

### 管理员登录步骤

1. **访问登录页面**
   - 前端登录：http://localhost:5173/login
   - 或点击首页的"登录"按钮

2. **输入管理员凭据**
   ```
   邮箱：admin@ideaeden.com
   密码：admin123456
   ```

3. **验证登录成功**
   - 登录成功后会跳转到仪表板
   - 管理员用户会看到额外的管理功能菜单
   - 顶部导航栏显示管理员标识

### 管理员功能访问

登录后，管理员可以访问：

- **用户管理**：http://localhost:5173/admin/users
- **系统监控**：http://localhost:5173/admin/monitoring
- **数据分析**：http://localhost:5173/analyze
- **系统设置**：http://localhost:5173/settings
- **API管理**：http://localhost:8000/docs

### 修改管理员信息

#### 方法一：通过前端界面

1. 登录管理员账号
2. 访问个人资料页面：http://localhost:5173/profile
3. 修改个人信息和密码

#### 方法二：通过环境变量

修改 `.env` 文件中的管理员配置：

```env
# 自定义管理员账号
ADMIN_EMAIL=your-admin@company.com
ADMIN_PASSWORD=your-secure-password
```

重启后端服务使配置生效。

#### 方法三：通过API直接修改

使用API文档页面：http://localhost:8000/docs

1. 先通过 `/api/v1/auth/login` 获取管理员Token
2. 使用Token调用 `/api/v1/admin/users/{user_id}` 修改用户信息

## 🔧 开发环境配置

### IDE推荐配置

#### VS Code 推荐插件

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

#### Python环境配置

```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

### 调试配置

#### 后端调试

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/venv/Scripts/uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

#### 前端调试

在浏览器开发者工具中调试，或使用VS Code的调试功能。

## 🐛 常见问题解决

### 后端启动问题

#### 问题1：端口被占用
```bash
# 错误信息：Address already in use
# 解决方案：
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 问题2：依赖安装失败
```bash
# 解决方案：
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 问题3：数据库连接失败
```bash
# 检查数据库文件权限
# 确保 .env 文件中 DATABASE_URL 配置正确
```

### 前端启动问题

#### 问题1：依赖安装失败
```bash
# 清理缓存重新安装
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 问题2：端口冲突
```bash
# 修改端口启动
npm run dev -- --port 3000
```

### 管理员登录问题

#### 问题1：管理员账号不存在
```bash
# 检查后端日志，确认管理员用户创建成功
# 重启后端服务触发用户创建
```

#### 问题2：密码错误
```bash
# 检查 .env 文件中的 ADMIN_PASSWORD 配置
# 确保与登录时输入的密码一致
```

#### 问题3：Token过期
```bash
# 重新登录获取新Token
# 检查 ACCESS_TOKEN_EXPIRE_MINUTES 配置
```

## 📝 启动检查清单

### 启动前检查

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] Redis 已安装并运行（可选）
- [ ] `.env` 文件已配置
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装

### 启动后验证

- [ ] 后端API文档可访问：http://localhost:8000/docs
- [ ] 前端应用可访问：http://localhost:5173
- [ ] 健康检查通过：http://localhost:8000/api/v1/health
- [ ] 管理员可正常登录
- [ ] 数据库连接正常
- [ ] 缓存服务正常（如果启用）

### 功能验证

- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 数据分析功能正常
- [ ] 管理员功能可访问
- [ ] API接口响应正常

## 🚀 生产部署建议

### 安全配置

1. **修改默认密码**
   ```env
   ADMIN_PASSWORD=your-very-secure-password
   ```

2. **使用强密钥**
   ```env
   SECRET_KEY=your-very-long-and-random-secret-key
   ```

3. **配置HTTPS**
   ```env
   FRONTEND_URL=https://your-domain.com
   ```

### 性能优化

1. **使用PostgreSQL**
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. **配置Redis缓存**
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

3. **启用多进程**
   ```bash
   uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

---

**技术支持**：如遇问题，请查看日志文件或联系开发团队。
**文档版本**：IdeaEden 2.0
**更新日期**：2024年1月