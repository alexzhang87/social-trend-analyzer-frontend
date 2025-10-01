# Railway 自动化部署指南

## 概述

本指南将帮助您将社交趋势分析器自动部署到Railway平台。Railway是一个现代化的云平台，提供简单的部署流程和自动扩展功能。

## 前置要求

1. **Railway账户**: 在 [railway.app](https://railway.app) 注册账户
2. **Node.js**: 安装Node.js以使用Railway CLI
3. **Git**: 确保项目已提交到Git仓库
4. **API密钥**: 准备好所需的API密钥

## 快速部署

### 方法1: 使用自动化脚本

1. 运行部署脚本：
```bash
deploy-railway.bat
```

2. 按照脚本提示完成部署

### 方法2: 手动部署

#### 步骤1: 安装Railway CLI

```bash
npm install -g @railway/cli
```

#### 步骤2: 登录Railway

```bash
railway login
```

#### 步骤3: 初始化项目

```bash
railway init
```

选择 "Create new project" 并为项目命名。

#### 步骤4: 配置环境变量

在Railway控制台中设置以下环境变量：

**必需的环境变量:**
- `ZHIPU_API_KEY`: 智谱AI API密钥
- `SECRET_KEY`: JWT密钥（建议使用强随机字符串）

**可选的环境变量:**
- `TWITTERAPI_IO_KEY`: Twitter API密钥
- `OPENAI_API_KEY`: OpenAI API密钥
- `DATABASE_URL`: 数据库连接URL（Railway可自动提供）
- `REDIS_URL`: Redis连接URL（Railway可自动提供）

#### 步骤5: 部署应用

```bash
railway up
```

## 数据库配置

### 使用Railway PostgreSQL

1. 在Railway控制台中添加PostgreSQL服务：
```bash
railway add postgresql
```

2. Railway会自动设置 `DATABASE_URL` 环境变量

3. 运行数据库初始化：
```bash
railway run python railway_init.py
```

### 使用SQLite（默认）

如果不添加PostgreSQL服务，应用将使用SQLite数据库，数据存储在容器中。

## Redis配置（可选）

1. 添加Redis服务：
```bash
railway add redis
```

2. Railway会自动设置 `REDIS_URL` 环境变量

## 部署后验证

### 自动健康检查

运行健康检查脚本：
```bash
python railway_health_check.py https://your-app.railway.app
```

### 手动验证

1. **检查应用状态:**
```bash
railway status
```

2. **查看日志:**
```bash
railway logs
```

3. **打开应用:**
```bash
railway open
```

4. **测试API端点:**
- 访问 `https://your-app.railway.app/` 查看欢迎消息
- 访问 `https://your-app.railway.app/docs` 查看API文档

## 常见问题

### 1. 部署失败

**检查日志:**
```bash
railway logs
```

**常见原因:**
- 环境变量未设置
- 依赖安装失败
- 端口配置错误

### 2. 应用无法启动

**检查配置:**
- 确保 `railway.toml` 配置正确
- 验证 `Dockerfile` 语法
- 检查环境变量设置

### 3. 数据库连接失败

**解决方案:**
- 确保添加了PostgreSQL服务
- 检查 `DATABASE_URL` 环境变量
- 运行数据库初始化脚本

### 4. API密钥错误

**检查:**
- 在Railway控制台中验证API密钥设置
- 确保密钥格式正确
- 测试密钥有效性

## 监控和维护

### 查看应用指标

1. 在Railway控制台中查看：
   - CPU使用率
   - 内存使用率
   - 网络流量
   - 响应时间

### 日志监控

```bash
# 实时查看日志
railway logs --follow

# 查看特定时间的日志
railway logs --since 1h
```

### 应用更新

```bash
# 重新部署
railway up

# 重启应用
railway restart
```

## 扩展配置

### 自定义域名

1. 在Railway控制台中添加自定义域名
2. 配置DNS记录
3. 更新CORS设置

### 环境分离

1. 创建不同的Railway项目用于开发/生产环境
2. 使用不同的环境变量配置
3. 设置不同的数据库实例

## 成本优化

### 资源配置

- Railway提供免费额度
- 根据实际使用情况调整资源配置
- 监控使用量避免超出限制

### 数据库优化

- 定期清理旧数据
- 优化查询性能
- 考虑使用Redis缓存

## 安全最佳实践

1. **环境变量安全:**
   - 不要在代码中硬编码密钥
   - 使用强随机密钥
   - 定期轮换API密钥

2. **网络安全:**
   - 配置适当的CORS策略
   - 使用HTTPS
   - 实施速率限制

3. **数据安全:**
   - 定期备份数据库
   - 加密敏感数据
   - 实施访问控制

## 支持和帮助

- **Railway文档**: https://docs.railway.app
- **Railway社区**: https://discord.gg/railway
- **项目问题**: 在GitHub仓库中提交issue

## 总结

通过本指南，您应该能够成功将应用部署到Railway平台。Railway提供了简单的部署流程和强大的功能，是部署现代Web应用的理想选择。

记住定期监控应用性能，及时更新依赖，并遵循安全最佳实践。