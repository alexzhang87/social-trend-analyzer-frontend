#!/usr/bin/env python3
"""
简单测试Product Hunt服务
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加app路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv
from services.product_hunt_service import ProductHuntOfficialService

# 加载环境变量
load_dotenv()

async def test_product_hunt_service():
    """测试Product Hunt服务"""
    print("测试Product Hunt服务...")
    
    try:
        service = ProductHuntOfficialService()
        
        # 测试认证
        print("测试认证...")
        token = await service._get_access_token()
        print(f"✅ 认证成功，令牌: {token[:20]}...")
        
        # 测试获取产品
        print("测试获取产品...")
        today = datetime.now()
        products = await service.get_daily_products(date=today, limit=3)
        
        print(f"✅ 获取到 {len(products)} 个产品")
        
        if products:
            print("\n第一个产品信息:")
            product = products[0]
            print(f"- 标题: {product.get('title', 'N/A')}")
            print(f"- 内容: {product.get('content', 'N/A')[:100]}...")
            print(f"- 投票数: {product.get('votes', 0)}")
            print(f"- 评论数: {product.get('comments_count', 0)}")
            print(f"- 来源: {product.get('source', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_product_hunt_service())
    if success:
        print("\n🎉 Product Hunt服务测试成功!")
    else:
        print("\n💥 Product Hunt服务测试失败!")