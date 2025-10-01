#!/usr/bin/env python3
"""
快速Reddit API测试脚本
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from app.services.reddit_official_service import reddit_service


async def quick_test():
    print("🔍 快速测试Reddit API搜索功能...")
    
    try:
        # 测试搜索
        results = await reddit_service.search_posts(['AI'], limit=3)
        print(f"✅ 搜索成功！找到 {len(results)} 条帖子")
        
        for i, post in enumerate(results[:2]):
            print(f"{i+1}. {post['content'][:80]}...")
            print(f"   - 分数: {post['score']}, 评论: {post['comments_count']}")
    
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
    
    try:
        # 测试子版块
        results = await reddit_service.get_subreddit_posts('technology', limit=2)
        print(f"✅ 子版块获取成功！找到 {len(results)} 条帖子")
    
    except Exception as e:
        print(f"❌ 子版块测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(quick_test())