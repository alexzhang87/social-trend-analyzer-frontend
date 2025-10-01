#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速依赖检查脚本
检查后端项目中所有必需的Python模块是否已安装
"""

import sys
import importlib
from typing import List, Tuple

# 根据代码分析确定的必需依赖列表
REQUIRED_MODULES = [
    # 核心框架
    ('fastapi', 'FastAPI web框架'),
    ('uvicorn', 'ASGI服务器'),
    ('pydantic', '数据验证'),
    ('sqlalchemy', '数据库ORM'),
    
    # 认证和安全
    ('jose', 'JWT处理'),
    ('passlib', '密码哈希'),
    ('email_validator', '邮箱验证'),
    
    # 任务队列和缓存
    ('celery', '任务队列'),
    ('redis', 'Redis客户端'),
    
    # 文本分析
    ('vaderSentiment', '情感分析'),
    ('jieba', '中文分词'),
    ('textblob', '文本处理'),
    ('nltk', '自然语言处理'),
    
    # 数据处理
    ('pandas', '数据分析'),
    ('numpy', '数值计算'),
    ('sklearn', '机器学习'),
    
    # 网络和爬虫
    ('requests', 'HTTP客户端'),
    ('aiohttp', '异步HTTP客户端'),
    ('bs4', 'BeautifulSoup HTML解析'),
    ('snscrape', '社交媒体爬虫'),
    ('pytrends', 'Google Trends'),
    ('feedparser', 'RSS解析'),
    
    # 其他工具
    ('zhipuai', '智谱AI SDK'),
    ('reportlab', 'PDF生成'),
    ('stripe', '支付处理'),
    ('emoji', 'Emoji处理'),
    ('retrying', '重试机制'),
    
    # 标准库扩展
    ('dotenv', '环境变量'),
    ('multipart', '文件上传'),
]

def check_module(module_name: str, description: str) -> Tuple[bool, str]:
    """检查单个模块是否可导入"""
    try:
        # 特殊处理一些模块名映射
        import_name = module_name
        if module_name == 'bs4':
            import_name = 'bs4'
        elif module_name == 'dotenv':
            import_name = 'dotenv'
        elif module_name == 'multipart':
            import_name = 'multipart'
        elif module_name == 'sklearn':
            import_name = 'sklearn'
        
        importlib.import_module(import_name)
        return True, f"✅ {module_name} ({description})"
    except ImportError as e:
        return False, f"❌ {module_name} ({description}) - 缺失: {str(e)}"
    except Exception as e:
        return False, f"⚠️  {module_name} ({description}) - 错误: {str(e)}"

def main():
    """主检查函数"""
    print("🔍 开始检查后端Python依赖...")
    print("=" * 60)
    
    missing_modules = []
    available_modules = []
    error_modules = []
    
    for module_name, description in REQUIRED_MODULES:
        success, message = check_module(module_name, description)
        print(message)
        
        if success:
            available_modules.append(module_name)
        elif "缺失" in message:
            missing_modules.append(module_name)
        else:
            error_modules.append(module_name)
    
    print("\n" + "=" * 60)
    print(f"📊 检查结果统计:")
    print(f"   ✅ 可用模块: {len(available_modules)}")
    print(f"   ❌ 缺失模块: {len(missing_modules)}")
    print(f"   ⚠️  错误模块: {len(error_modules)}")
    
    if missing_modules:
        print(f"\n🔧 需要安装的模块:")
        pip_commands = []
        for module in missing_modules:
            if module == 'jose':
                pip_commands.append('python-jose[cryptography]')
            elif module == 'bs4':
                pip_commands.append('beautifulsoup4')
            elif module == 'sklearn':
                pip_commands.append('scikit-learn')
            elif module == 'dotenv':
                pip_commands.append('python-dotenv')
            elif module == 'multipart':
                pip_commands.append('python-multipart')
            else:
                pip_commands.append(module)
        
        print(f"   pip install {' '.join(pip_commands)}")
    
    if error_modules:
        print(f"\n⚠️  有错误的模块需要检查: {', '.join(error_modules)}")
    
    if not missing_modules and not error_modules:
        print("\n🎉 所有依赖都已正确安装！")
        return True
    else:
        print(f"\n❌ 发现 {len(missing_modules + error_modules)} 个问题需要解决")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)