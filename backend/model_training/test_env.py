#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境变量加载
"""

import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
print(f"项目根目录: {project_root}")

# 检查.env文件是否存在
env_path = project_root / '.env'
print(f".env文件路径: {env_path}")
print(f".env文件存在: {env_path.exists()}")

if env_path.exists():
    print(f".env文件大小: {env_path.stat().st_size} bytes")
    
    # 手动读取.env文件
    print("\n手动读取.env文件内容:")
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:20], 1):  # 只显示前20行
            if 'REDDIT' in line or 'GITHUB' in line or 'PRODUCT_HUNT' in line:
                print(f"第{i}行: {line.strip()}")

# 尝试加载环境变量
print("\n尝试加载环境变量...")
try:
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                if 'REDDIT' in key or 'GITHUB' in key or 'PRODUCT_HUNT' in key:
                    print(f"设置环境变量: {key} = {value[:20]}...")
except Exception as e:
    print(f"加载环境变量失败: {e}")

# 检查关键环境变量
print("\n检查关键环境变量:")
keys_to_check = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET', 
    'REDDIT_USERNAME',
    'REDDIT_PASSWORD',
    'GITHUB_CLIENT_ID',
    'GITHUB_CLIENT_SECRET',
    'PRODUCT_HUNT_CLIENT_ID',
    'PRODUCT_HUNT_CLIENT_SECRET',
    'TWITTERAPI_IO_KEY'
]

for key in keys_to_check:
    value = os.getenv(key, '')
    status = '✅' if value else '❌'
    print(f"{status} {key}: {'已设置' if value else '未设置'}")