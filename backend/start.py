#!/usr/bin/env python3
"""
Railway 部署启动脚本
简化版本，避免复杂的依赖问题
"""
import os
import sys
import subprocess

def main():
    print("🚀 启动AI数据收集系统...")
    
    # 设置环境变量
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('PYTHONPATH', '/app')
    os.environ.setdefault('ENVIRONMENT', 'production')
    
    # 切换到正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_training_dir = os.path.join(script_dir, 'model_training')
    
    if os.path.exists(model_training_dir):
        os.chdir(model_training_dir)
        print(f"📁 切换到目录: {model_training_dir}")
    
    # 启动主程序
    try:
        print("🔄 启动数据收集调度器...")
        subprocess.run([sys.executable, 'master_data_scheduler.py'], check=True)
    except FileNotFoundError:
        print("❌ 找不到master_data_scheduler.py，尝试启动健康检查服务器...")
        try:
            subprocess.run([sys.executable, 'health_server.py'], check=True)
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            # 作为最后的备选方案，启动一个简单的HTTP服务器
            print("🔄 启动备用HTTP服务器...")
            from http.server import HTTPServer, SimpleHTTPRequestHandler
            
            port = int(os.environ.get('PORT', 8000))
            server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
            print(f"✅ 服务器运行在端口 {port}")
            server.serve_forever()

if __name__ == "__main__":
    main()