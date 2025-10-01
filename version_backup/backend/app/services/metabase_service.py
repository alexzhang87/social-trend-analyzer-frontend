"""
Metabase开源BI工具集成服务

提供专业的商业智能和数据可视化解决方案
- 完全开源免费
- 支持Docker部署
- 专业的仪表盘制作
- 丰富的图表类型
- 自助式数据分析

部署方案：
1. Docker Compose一键部署
2. PostgreSQL作为应用数据库
3. 连接现有的趋势分析数据库
4. 预配置仪表盘模板
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
from pathlib import Path

logger = logging.getLogger("trend-analyzer")

class MetabaseService:
    """Metabase集成服务"""
    
    def __init__(self):
        self.metabase_port = os.getenv("METABASE_PORT", "3001")
        self.postgres_port = os.getenv("METABASE_POSTGRES_PORT", "5433")
        self.postgres_password = os.getenv("METABASE_POSTGRES_PASSWORD", "metabase_secure_password")
        self.postgres_user = os.getenv("METABASE_POSTGRES_USER", "metabase")
        self.postgres_db = os.getenv("METABASE_POSTGRES_DB", "metabaseappdb")
        
        self.docker_compose_template = self._generate_docker_compose()
        
        logger.info("Metabase服务已初始化")
    
    def _generate_docker_compose(self) -> str:
        """生成Docker Compose配置"""
        return f"""version: '3.8'

services:
  metabase:
    image: metabase/metabase:latest
    container_name: metabase-app
    hostname: metabase
    volumes:
      - metabase-data:/metabase-data
      - ./metabase-plugins:/plugins
    ports:
      - "{self.metabase_port}:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: {self.postgres_db}
      MB_DB_PORT: 5432
      MB_DB_USER: {self.postgres_user}
      MB_DB_PASS: {self.postgres_password}
      MB_DB_HOST: postgres
      JAVA_TIMEZONE: Asia/Shanghai
      MB_SITE_NAME: "社交媒体趋势分析BI"
      MB_SITE_LOCALE: zh
    networks:
      - metabase-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: curl --fail -I http://localhost:3000/api/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: metabase-postgres
    hostname: postgres
    environment:
      POSTGRES_USER: {self.postgres_user}
      POSTGRES_DB: {self.postgres_db}
      POSTGRES_PASSWORD: {self.postgres_password}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "{self.postgres_port}:5432"
    networks:
      - metabase-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {self.postgres_user} -d {self.postgres_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # 可选：Redis缓存（提升性能）
  redis:
    image: redis:7-alpine
    container_name: metabase-redis
    hostname: redis
    ports:
      - "6379:6379"
    networks:
      - metabase-network
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  metabase-data:
    driver: local
  postgres-data:
    driver: local
  redis-data:
    driver: local

networks:
  metabase-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
"""

    async def create_deployment_files(self, target_dir: str = "./metabase-deployment") -> Dict[str, Any]:
        """
        创建Metabase部署文件
        
        Args:
            target_dir: 目标目录
            
        Returns:
            部署文件信息
        """
        try:
            # 创建目录
            deploy_path = Path(target_dir)
            deploy_path.mkdir(exist_ok=True)
            
            # 创建plugins目录
            plugins_path = deploy_path / "metabase-plugins"
            plugins_path.mkdir(exist_ok=True)
            
            # 写入docker-compose.yml
            compose_file = deploy_path / "docker-compose.yml"
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(self.docker_compose_template)
            
            # 创建环境变量文件
            env_file = deploy_path / ".env"
            env_content = f"""# Metabase部署配置
METABASE_PORT={self.metabase_port}
METABASE_POSTGRES_PORT={self.postgres_port}
METABASE_POSTGRES_PASSWORD={self.postgres_password}
METABASE_POSTGRES_USER={self.postgres_user}
METABASE_POSTGRES_DB={self.postgres_db}

# 安全提示：生产环境请修改默认密码
# 建议使用强密码，包含大小写字母、数字和特殊字符
"""
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # 创建启动脚本
            start_script = deploy_path / "start.sh"
            start_content = f"""#!/bin/bash
# Metabase启动脚本

echo "🚀 启动Metabase BI系统..."
echo "端口: {self.metabase_port}"
echo "PostgreSQL端口: {self.postgres_port}"

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
    echo "📊 访问地址: http://localhost:{self.metabase_port}"
    echo "🗄️ PostgreSQL地址: localhost:{self.postgres_port}"
    echo "👤 数据库用户: {self.postgres_user}"
    echo "📂 数据库名: {self.postgres_db}"
    echo ""
    echo "🔧 首次访问需要进行初始设置:"
    echo "   1. 创建管理员账号"
    echo "   2. 连接数据源"
    echo "   3. 创建仪表盘"
else
    echo "❌ 启动失败，请检查日志:"
    docker-compose logs
fi
"""
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(start_content)
            
            # 设置执行权限（Linux/Mac）
            try:
                os.chmod(start_script, 0o755)
            except:
                pass  # Windows系统忽略权限设置
            
            # 创建停止脚本
            stop_script = deploy_path / "stop.sh"
            stop_content = """#!/bin/bash
# Metabase停止脚本

echo "🛑 停止Metabase服务..."
docker-compose down

echo "✅ 服务已停止"
echo "💾 数据已保存在Docker volumes中"
echo "🔄 如需完全清理，运行: docker-compose down -v"
"""
            with open(stop_script, 'w', encoding='utf-8') as f:
                f.write(stop_content)
            
            try:
                os.chmod(stop_script, 0o755)
            except:
                pass
            
            # 创建README文件
            readme_file = deploy_path / "README.md"
            readme_content = f"""# Metabase BI 部署指南

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
- Metabase访问地址: http://localhost:{self.metabase_port}
- PostgreSQL端口: {self.postgres_port}

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
"""
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            return {
                "success": True,
                "deployment_path": str(deploy_path.absolute()),
                "files_created": [
                    "docker-compose.yml",
                    ".env", 
                    "start.sh",
                    "stop.sh",
                    "README.md"
                ],
                "metabase_url": f"http://localhost:{self.metabase_port}",
                "postgres_connection": {
                    "host": "localhost",
                    "port": self.postgres_port,
                    "database": self.postgres_db,
                    "username": self.postgres_user,
                    "password": self.postgres_password
                }
            }
            
        except Exception as e:
            logger.error(f"创建部署文件失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_dashboard_templates(self) -> Dict[str, Any]:
        """获取预配置的仪表盘模板"""
        return {
            "templates": [
                {
                    "name": "社交媒体趋势概览",
                    "description": "全平台趋势数据总览仪表盘",
                    "charts": [
                        {
                            "type": "number",
                            "title": "趋势评分",
                            "description": "当前整体趋势热度评分",
                            "query": "SELECT trend_score FROM trend_analysis ORDER BY created_at DESC LIMIT 1"
                        },
                        {
                            "type": "pie",
                            "title": "情感分布",
                            "description": "各平台情感分布比例",
                            "query": "SELECT sentiment, COUNT(*) as count FROM sentiment_data GROUP BY sentiment"
                        },
                        {
                            "type": "bar",
                            "title": "平台活跃度对比",
                            "description": "各平台讨论数量对比",
                            "query": "SELECT platform, SUM(posts_count) as total_posts FROM platform_stats GROUP BY platform"
                        },
                        {
                            "type": "line",
                            "title": "趋势变化",
                            "description": "过去30天趋势评分变化",
                            "query": "SELECT DATE(created_at) as date, AVG(trend_score) as avg_score FROM trend_analysis WHERE created_at >= NOW() - INTERVAL '30 days' GROUP BY DATE(created_at) ORDER BY date"
                        }
                    ]
                },
                {
                    "name": "关键词分析仪表盘",
                    "description": "热门关键词和话题分析",
                    "charts": [
                        {
                            "type": "table",
                            "title": "热门关键词Top 20",
                            "description": "使用频率最高的关键词列表",
                            "query": "SELECT keyword, frequency, platforms FROM keyword_analysis ORDER BY frequency DESC LIMIT 20"
                        },
                        {
                            "type": "wordcloud",
                            "title": "关键词云图",
                            "description": "可视化关键词分布",
                            "query": "SELECT keyword as word, frequency as weight FROM keyword_analysis WHERE frequency > 5"
                        },
                        {
                            "type": "funnel",
                            "title": "关键词传播路径",
                            "description": "关键词在各平台的传播情况",
                            "query": "SELECT platform, COUNT(DISTINCT keyword) as unique_keywords FROM keyword_platform_mapping GROUP BY platform ORDER BY unique_keywords DESC"
                        }
                    ]
                },
                {
                    "name": "平台深度分析",
                    "description": "各平台详细数据分析",
                    "charts": [
                        {
                            "type": "gauge",
                            "title": "Twitter活跃度",
                            "description": "Twitter平台参与度指标",
                            "query": "SELECT AVG(engagement_score) as score FROM platform_metrics WHERE platform = 'twitter'"
                        },
                        {
                            "type": "gauge", 
                            "title": "Reddit活跃度",
                            "description": "Reddit平台参与度指标",
                            "query": "SELECT AVG(engagement_score) as score FROM platform_metrics WHERE platform = 'reddit'"
                        },
                        {
                            "type": "map",
                            "title": "地理分布",
                            "description": "用户地理位置分布（如果有数据）",
                            "query": "SELECT country, COUNT(*) as users FROM user_locations GROUP BY country"
                        },
                        {
                            "type": "scatter",
                            "title": "参与度vs情感",
                            "description": "参与度与情感的关系分析",
                            "query": "SELECT engagement_score, sentiment_score FROM post_analysis WHERE engagement_score > 0"
                        }
                    ]
                }
            ],
            "setup_instructions": [
                "1. 确保Metabase已连接到趋势分析数据库",
                "2. 在Metabase中创建新仪表盘",
                "3. 根据模板添加图表，使用提供的SQL查询",
                "4. 调整图表样式和布局",
                "5. 设置自动刷新间隔",
                "6. 配置访问权限和分享设置"
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "Metabase开源BI工具",
            "version": "最新版",
            "deployment_method": "Docker Compose",
            "features": {
                "cost": "完全免费",
                "charts": "40+种图表类型",
                "dashboards": "自定义仪表盘",
                "sql_editor": "SQL查询编辑器",
                "alerts": "数据警报",
                "sharing": "仪表盘分享",
                "api": "REST API",
                "embedding": "嵌入式分析"
            },
            "requirements": {
                "docker": "Docker和Docker Compose",
                "memory": "推荐2GB+内存",
                "storage": "1GB+存储空间",
                "network": "网络访问权限"
            },
            "ports": {
                "metabase": f"http://localhost:{self.metabase_port}",
                "postgres": f"localhost:{self.postgres_port}"
            },
            "advantages": [
                "完全开源，无license费用",
                "一键Docker部署，简单快速",
                "专业的BI功能，企业级性能",
                "丰富的图表类型和可视化选项",
                "支持SQL查询和自助分析",
                "良好的中文支持",
                "活跃的社区和文档"
            ],
            "use_cases": [
                "业务数据可视化",
                "KPI监控仪表盘",
                "趋势分析报告",
                "实时数据监控",
                "自助式数据分析",
                "团队协作分析"
            ]
        }
    
    async def generate_sample_data_script(self) -> str:
        """生成示例数据脚本"""
        return """-- Metabase示例数据脚本
-- 创建趋势分析相关表和示例数据

-- 趋势分析主表
CREATE TABLE IF NOT EXISTS trend_analysis (
    id SERIAL PRIMARY KEY,
    keywords TEXT[],
    trend_score DECIMAL(5,2),
    total_posts INTEGER,
    processing_time DECIMAL(8,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 情感数据表
CREATE TABLE IF NOT EXISTS sentiment_data (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    sentiment VARCHAR(20),
    confidence DECIMAL(4,3),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关键词分析表
CREATE TABLE IF NOT EXISTS keyword_analysis (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100),
    frequency INTEGER,
    platforms TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 平台统计表
CREATE TABLE IF NOT EXISTS platform_stats (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    posts_count INTEGER,
    avg_engagement DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例数据
INSERT INTO trend_analysis (keywords, trend_score, total_posts, processing_time) VALUES
('{"AI", "人工智能"}', 85.5, 1250, 15.3),
('{"区块链", "比特币"}', 72.8, 890, 12.7),
('{"元宇宙", "VR"}', 68.2, 654, 8.9);

INSERT INTO sentiment_data (platform, sentiment, confidence, content) VALUES
('twitter', 'positive', 0.89, 'This AI product is amazing!'),
('reddit', 'neutral', 0.65, 'Not sure about this technology'),
('product_hunt', 'positive', 0.92, 'Great innovation in AI space');

INSERT INTO keyword_analysis (keyword, frequency, platforms) VALUES
('AI', 1500, '{"twitter", "reddit", "product_hunt"}'),
('机器学习', 890, '{"twitter", "reddit"}'),
('创新', 750, '{"product_hunt", "twitter"}');

INSERT INTO platform_stats (platform, posts_count, avg_engagement) VALUES
('twitter', 2500, 45.6),
('reddit', 1800, 78.3),
('product_hunt', 650, 125.4),
('google_trends', 0, 85.2);
"""

# 全局实例
metabase_service = MetabaseService()