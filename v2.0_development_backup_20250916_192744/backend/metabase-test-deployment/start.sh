#!/bin/bash
# Metabase启动脚本

echo "🚀 启动Metabase BI系统..."
echo "端口: 3001"
echo "PostgreSQL端口: 5433"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 启动服务
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo "✅ Metabase启动成功!"
    echo "📊 访问地址: http://localhost:3001"
    echo "🗄️ PostgreSQL地址: localhost:5433"
    echo "👤 数据库用户: metabase"
    echo "📂 数据库名: metabaseappdb"
    echo ""
    echo "🔧 首次访问需要进行初始设置:"
    echo "   1. 创建管理员账号"
    echo "   2. 连接数据源"
    echo "   3. 创建仪表盘"
else
    echo "❌ 启动失败，请检查日志:"
    docker-compose logs
fi
