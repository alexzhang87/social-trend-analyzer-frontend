# 社交媒体趋势分析器 - 环境配置指南

## 🚀 快速开始

### 1. 环境要求

- **Docker** 和 **Docker Compose**
- **Node.js** 18+ (本地开发)
- **Python** 3.11+ (本地开发)
- **Redis** (已配置在Docker中)
- **PostgreSQL** (已配置在Docker中)

### 2. 一键启动

```bash
# Windows
scripts\setup-env.bat dev
scripts\docker-quick.bat dev

# Linux/macOS
chmod +x scripts/setup-env.sh
chmod +x scripts/docker-quick.sh
./scripts/setup-env.sh dev
./scripts/docker-quick.sh dev
```

### 3. 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Redis管理**: http://localhost:8081
- **数据库管理**: http://localhost:8080

## 📋 环境配置

### 开发环境

```bash
# 设置开发环境
scripts\setup-env.bat dev

# 启动开发服务
scripts\docker-quick.bat dev
```

**特性:**
- 热重载
- 开发工具
- SQLite数据库
- Redis缓存
- 详细日志

### 生产环境

```bash
# 设置生产环境
scripts\setup-env.bat prod

# 启动生产服务
scripts\docker-quick.bat prod
```

**特性:**
- 优化构建
- PostgreSQL数据库
- Redis集群
- Nginx反向代理
- 监控和日志收集

### 测试环境

```bash
# 设置测试环境
scripts\setup-env.bat test

# 启动测试服务
scripts\docker-quick.bat test
```

**特性:**
- 模拟外部API
- 测试数据库
- 快速测试模式

## 🔧 手动配置

### 1. 环境变量配置

复制对应的环境配置文件：

```bash
# 开发环境
cp .env.development .env
cp backend/.env.development backend/.env

# 生产环境
cp .env.production .env
cp backend/.env.production backend/.env

# 测试环境
cp .env.testing .env
cp backend/.env.testing backend/.env
```

### 2. 必需的API密钥

在 `.env` 文件中配置以下API密钥：

```env
# 智谱AI (必需)
ZHIPU_API_KEY=your_zhipu_api_key

# 社交媒体API (可选)
TWITTER_BEARER_TOKEN=your_twitter_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# 支付系统 (生产环境必需)
STRIPE_PUBLISHABLE_KEY=your_stripe_key
STRIPE_SECRET_KEY=your_stripe_secret
```

### 3. 数据库初始化

```bash
# 启动数据库服务
docker-compose up -d postgres redis

# 运行数据库迁移
docker-compose exec backend python -m alembic upgrade head

# 创建初始数据
docker-compose exec backend python scripts/init_data.py
```

## 🛠️ 开发工具

### 常用命令

```bash
# 查看服务状态
scripts\docker-quick.bat status

# 查看日志
scripts\docker-quick.bat logs
scripts\docker-quick.bat logs backend
scripts\docker-quick.bat logs frontend

# 重启服务
scripts\docker-quick.bat restart

# 停止所有服务
scripts\docker-quick.bat stop

# 清理Docker资源
scripts\docker-quick.bat clean
```

### 环境管理

```bash
# 检查当前环境
scripts\setup-env.bat --check

# 列出可用环境
scripts\setup-env.bat --list

# 重置环境配置
scripts\setup-env.bat --reset
```

### 本地开发

如果需要在本地运行而不使用Docker：

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm start
```

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```

2. **Docker权限问题**
   ```bash
   # 确保Docker服务正在运行
   docker --version
   docker-compose --version
   ```

3. **Redis连接失败**
   ```bash
   # 检查Redis服务
   docker-compose exec redis redis-cli ping
   ```

4. **数据库连接失败**
   ```bash
   # 检查PostgreSQL服务
   docker-compose exec postgres pg_isready
   ```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 重置数据

```bash
# 重置数据库
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python -m alembic upgrade head

# 重置Redis缓存
docker-compose exec redis redis-cli FLUSHALL
```

## 📊 监控和性能

### 生产环境监控

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **应用指标**: http://localhost:8000/metrics

### 性能优化

1. **Redis缓存配置**
   - 开发环境: 单实例，端口6379
   - 生产环境: 集群模式，持久化存储

2. **数据库优化**
   - 开发环境: SQLite，快速启动
   - 生产环境: PostgreSQL，连接池

3. **前端优化**
   - 开发环境: 热重载，源映射
   - 生产环境: 代码分割，压缩

## 🔐 安全配置

### 生产环境安全

1. **更改默认密码**
   ```env
   POSTGRES_PASSWORD=your_secure_password
   JWT_SECRET_KEY=your_jwt_secret
   ```

2. **配置HTTPS**
   ```env
   SSL_CERT_PATH=/path/to/cert.pem
   SSL_KEY_PATH=/path/to/key.pem
   ```

3. **限制CORS**
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```

## 📚 更多资源

- [API文档](http://localhost:8000/docs)
- [前端组件文档](./frontend/README.md)
- [后端API文档](./backend/README.md)
- [部署指南](./DEPLOYMENT.md)
- [贡献指南](./CONTRIBUTING.md)

## 🆘 获取帮助

如果遇到问题，请：

1. 查看日志文件
2. 检查环境配置
3. 参考故障排除部分
4. 提交Issue到项目仓库

---

**快速启动命令总结:**

```bash
# 一键启动开发环境
scripts\setup-env.bat dev && scripts\docker-quick.bat dev

# 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```