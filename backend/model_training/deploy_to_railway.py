#!/usr/bin/env python3
"""
Railway自动部署脚本
自动化部署AI数据收集系统到Railway平台
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """检查部署要求"""
    print("🔍 检查部署要求...")
    
    # 检查Railway CLI
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI: {result.stdout.strip()}")
        else:
            print("❌ Railway CLI未安装")
            print("请运行: npm install -g @railway/cli")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI未找到")
        print("请运行: npm install -g @railway/cli")
        return False
    
    # 检查必要文件
    required_files = [
        "Dockerfile",
        "requirements.txt",
        "railway.toml",
        "master_data_scheduler.py",
        "health_server.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ 缺少文件: {file}")
            return False
    
    return True

def login_to_railway():
    """登录Railway"""
    print("🔐 登录Railway...")
    try:
        result = subprocess.run(['railway', 'login'], check=True, shell=True)
        print("✅ Railway登录成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ Railway登录失败")
        return False

def create_railway_project():
    """创建Railway项目"""
    print("\n📦 创建Railway项目...")
    
    project_name = "ai-data-collector"
    try:
        result = subprocess.run(['railway', 'init', project_name], check=True, capture_output=True, text=True, shell=True)
        print(f"✅ 项目创建成功: {project_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 项目创建失败: {e}")
        return False

def set_environment_variables():
    """设置环境变量"""
    print("\n🔧 设置环境变量...")
    
    # 基础环境变量
    env_vars = {
        'PYTHONPATH': '/app',
        'PORT': '8080',
        'ENVIRONMENT': 'production',
        'DATA_COLLECTION_ENABLED': 'true',
        'COLLECTION_INTERVAL_HOURS': '6',
        'MAX_DAILY_COLLECTIONS': '4',
        'QUALITY_THRESHOLD': '0.7'
    }
    
    for key, value in env_vars.items():
        try:
            result = subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], 
                                  check=True, capture_output=True, text=True, shell=True)
            print(f"✅ {key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 设置 {key} 失败: {e}")
            return False
    
    print("\n⚠️ 请手动设置以下API密钥:")
    print("railway variables set ZHIPU_API_KEY=your_zhipu_api_key")
    print("railway variables set TWITTERAPI_IO_KEY=your_twitter_api_key")
    print("railway variables set REDDIT_CLIENT_ID=your_reddit_client_id")
    print("railway variables set REDDIT_CLIENT_SECRET=your_reddit_client_secret")
    print("railway variables set GITHUB_TOKEN=your_github_token")
    
    return True

def deploy_to_railway():
    """执行部署"""
    print("\n🚀 开始部署...")
    
    try:
        result = subprocess.run(['railway', 'up'], check=True, capture_output=True, text=True, shell=True)
        print("✅ 部署成功!")
        print(f"部署输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 部署失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*60)
    print("🎉 部署完成! 后续步骤:")
    print("="*60)
    print("1. 🔑 在Railway控制台设置API密钥:")
    print("   - 访问 https://railway.app/dashboard")
    print("   - 选择您的项目")
    print("   - 进入 Variables 标签页")
    print("   - 添加所有必要的API密钥")
    print()
    print("2. 🔍 监控系统状态:")
    print("   - 健康检查: /health")
    print("   - 详细状态: /status") 
    print("   - 统计信息: /stats")
    print()
    print("3. 📊 查看日志:")
    print("   - 运行: railway logs")
    print("   - 或在Railway控制台查看")
    print()
    print("4. 🎯 验证数据收集:")
    print("   - 等待几分钟后检查 /stats 端点")
    print("   - 确认数据收集正常运行")
    print()
    print("🚀 系统将在假期期间24/7自动收集数据!")

def main():
    """主函数"""
    print("🚀 Railway自动部署脚本")
    print("=" * 50)
    
    # 检查要求
    if not check_requirements():
        print("\n❌ 部署要求检查失败，请解决上述问题后重试")
        sys.exit(1)
    
    # 登录Railway
    if not login_to_railway():
        print("\n❌ Railway登录失败")
        sys.exit(1)
    
    # 创建项目
    if not create_railway_project():
        print("\n❌ 创建Railway项目失败")
        sys.exit(1)
    
    # 设置环境变量
    set_environment_variables()
    
    # 部署
    if not deploy_to_railway():
        print("\n❌ 部署失败")
        sys.exit(1)
    
    # 显示后续步骤
    show_next_steps()

if __name__ == "__main__":
    main()