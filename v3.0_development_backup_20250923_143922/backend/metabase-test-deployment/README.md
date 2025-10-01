# Metabase BI 部署指南

## 概述
这是一个预配置的Metabase开源BI工具部署方案，专门为社交媒体趋势分析系统设计。

## 功能特性
- ✅ 完全开源免费
- ✅ Docker一键部署
- ✅ PostgreSQL生产级数据库
- ✅ 中文界面支持
- ✅ 专业仪表盘模板
- ✅ 丰富的图表类型

## 快速开始

### 1. 启动服务
```bash
# 启动Metabase
./start.sh

# 或直接使用docker-compose
docker-compose up -d
```

### 2. 访问系统
- Metabase访问地址: http://localhost:3001
- PostgreSQL端口: 5433

### 3. 初始设置
1. 打开浏览器访问Metabase
2. 创建管理员账号
3. 跳过数据源设置（稍后配置）
4. 完成初始化

### 4. 连接数据源
在Metabase中添加数据库连接：
- 数据库类型: PostgreSQL
- 主机: localhost
- 端口: 5432 (内部端口)
- 数据库名: your_trend_analysis_db
- 用户名: your_db_user
- 密码: your_db_password

## 停止服务
```bash
./stop.sh
```

## 目录结构
```
metabase-deployment/
├── docker-compose.yml    # Docker编排文件
├── .env                 # 环境变量配置
├── start.sh            # 启动脚本
├── stop.sh             # 停止脚本
├── README.md           # 说明文档
└── metabase-plugins/   # 插件目录
```

## 数据持久化
所有数据存储在Docker volumes中：
- `metabase-data`: Metabase应用数据
- `postgres-data`: PostgreSQL数据
- `redis-data`: Redis缓存数据

## 安全建议
1. 修改默认PostgreSQL密码
2. 配置防火墙规则
3. 启用HTTPS（生产环境）
4. 定期备份数据

## 故障排除

### 端口冲突
如果端口被占用，修改`.env`文件中的端口配置。

### 内存不足
Metabase建议至少2GB内存，如果内存不足可能启动失败。

### 日志查看
```bash
docker-compose logs metabase
docker-compose logs postgres
```

## 进阶配置

### 连接外部数据库
修改`docker-compose.yml`中的环境变量，连接到外部PostgreSQL。

### 添加插件
将JAR文件放入`metabase-plugins/`目录并重启服务。

### 性能优化
1. 启用Redis缓存
2. 配置数据库连接池
3. 设置合适的Java堆内存

## 支持
- 官方文档: https://www.metabase.com/docs/
- 社区论坛: https://discourse.metabase.com/
- GitHub: https://github.com/metabase/metabase
