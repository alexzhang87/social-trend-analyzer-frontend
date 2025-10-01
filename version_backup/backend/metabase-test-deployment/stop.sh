#!/bin/bash
# Metabase停止脚本

echo "🛑 停止Metabase服务..."
docker-compose down

echo "✅ 服务已停止"
echo "💾 数据已保存在Docker volumes中"
echo "🔄 如需完全清理，运行: docker-compose down -v"
