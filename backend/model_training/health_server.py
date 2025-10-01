#!/usr/bin/env python3
"""
健康检查服务器 - Railway部署专用
为数据收集系统提供健康检查端点
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """健康检查处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/health':
            self.handle_health_check()
        elif self.path == '/status':
            self.handle_status_check()
        elif self.path == '/stats':
            self.handle_stats_check()
        else:
            self.send_error(404, "Not Found")
    
    def handle_health_check(self):
        """基础健康检查"""
        try:
            # 检查数据库连接
            db_status = self.check_database()
            
            # 检查文件系统
            fs_status = self.check_filesystem()
            
            # 检查环境变量
            env_status = self.check_environment()
            
            health_data = {
                "status": "healthy" if all([db_status, fs_status, env_status]) else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": db_status,
                    "filesystem": fs_status,
                    "environment": env_status
                }
            }
            
            self.send_json_response(health_data, 200 if health_data["status"] == "healthy" else 503)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.send_json_response({"status": "error", "message": str(e)}, 500)
    
    def handle_status_check(self):
        """详细状态检查"""
        try:
            status_data = {
                "system": "AI Data Collection System",
                "version": "1.0.0",
                "uptime": self.get_uptime(),
                "collections_today": self.get_collections_count(),
                "last_collection": self.get_last_collection_time(),
                "storage_usage": self.get_storage_usage()
            }
            
            self.send_json_response(status_data, 200)
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_stats_check(self):
        """统计信息检查"""
        try:
            stats_data = {
                "total_collections": self.get_total_collections(),
                "quality_distribution": self.get_quality_distribution(),
                "expert_type_distribution": self.get_expert_distribution(),
                "source_distribution": self.get_source_distribution()
            }
            
            self.send_json_response(stats_data, 200)
            
        except Exception as e:
            logger.error(f"Stats check failed: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def check_database(self):
        """检查数据库连接"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT 1")
                conn.close()
                return True
            return False
        except:
            return False
    
    def check_filesystem(self):
        """检查文件系统"""
        try:
            # 检查必要目录
            required_dirs = ["collected_data", "huggingface_data", "logs"]
            for dir_name in required_dirs:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
            return True
        except:
            return False
    
    def check_environment(self):
        """检查环境变量"""
        required_vars = ["REDDIT_CLIENT_ID", "GITHUB_TOKENS", "TWITTER_BEARER_TOKEN"]
        return any(os.getenv(var) for var in required_vars)
    
    def get_uptime(self):
        """获取运行时间"""
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.readline().split()[0])
                return f"{uptime_seconds:.0f} seconds"
        except:
            return "unknown"
    
    def get_collections_count(self):
        """获取今日收集数量"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM collections 
                    WHERE DATE(created_at) = DATE('now')
                """)
                count = cursor.fetchone()[0]
                conn.close()
                return count
            return 0
        except:
            return 0
    
    def get_last_collection_time(self):
        """获取最后收集时间"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT MAX(created_at) FROM collections
                """)
                result = cursor.fetchone()[0]
                conn.close()
                return result or "never"
            return "never"
        except:
            return "never"
    
    def get_storage_usage(self):
        """获取存储使用情况"""
        try:
            total_size = 0
            for root, dirs, files in os.walk("collected_data"):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            return f"{total_size / 1024 / 1024:.2f} MB"
        except:
            return "unknown"
    
    def get_total_collections(self):
        """获取总收集数量"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT COUNT(*) FROM collections")
                count = cursor.fetchone()[0]
                conn.close()
                return count
            return 0
        except:
            return 0
    
    def get_quality_distribution(self):
        """获取质量分布"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT 
                        CASE 
                            WHEN quality_score >= 0.9 THEN 'excellent'
                            WHEN quality_score >= 0.8 THEN 'good'
                            WHEN quality_score >= 0.7 THEN 'acceptable'
                            ELSE 'poor'
                        END as quality_level,
                        COUNT(*) as count
                    FROM collections 
                    GROUP BY quality_level
                """)
                result = dict(cursor.fetchall())
                conn.close()
                return result
            return {}
        except:
            return {}
    
    def get_expert_distribution(self):
        """获取专家类型分布"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT expert_type, COUNT(*) as count
                    FROM collections 
                    GROUP BY expert_type
                """)
                result = dict(cursor.fetchall())
                conn.close()
                return result
            return {}
        except:
            return {}
    
    def get_source_distribution(self):
        """获取数据源分布"""
        try:
            db_path = "collection_tracking.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("""
                    SELECT source, COUNT(*) as count
                    FROM collections 
                    GROUP BY source
                """)
                result = dict(cursor.fetchall())
                conn.close()
                return result
            return {}
        except:
            return {}
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """重写日志方法，避免过多输出"""
        pass

def start_health_server(port=8000):
    """启动健康检查服务器"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    
    def run_server():
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Health check server stopped")
            server.shutdown()
    
    # 在后台线程中运行服务器
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return server

if __name__ == "__main__":
    # 启动健康检查服务器
    port = int(os.getenv("PORT", 8000))
    start_health_server(port)
    
    # 保持主线程运行
    try:
        while True:
            asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down health server...")