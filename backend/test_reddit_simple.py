#!/usr/bin/env python3
"""
简单的Reddit API测试脚本
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_reddit_public_api():
    """测试Reddit公开API"""
    
    headers = {
        'User-Agent': 'trend-analyzer:v1.0.0 (by /u/test_user)'
    }
    
    # 测试获取r/programming的热门帖子
    url = "https://www.reddit.com/r/programming/hot.json?limit=5"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"状态码: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    logger.info(f"成功获取 {len(posts)} 条帖子")
                    
                    for i, post_item in enumerate(posts[:3]):
                        post = post_item.get('data', {})
                        title = post.get('title', 'No title')
                        score = post.get('score', 0)
                        comments = post.get('num_comments', 0)
                        
                        logger.info(f"帖子 {i+1}: {title[:50]}... (分数: {score}, 评论: {comments})")
                    
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"请求失败: {response.status} - {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"请求异常: {e}")
        return False

async def main():
    logger.info("开始测试Reddit公开API...")
    success = await test_reddit_public_api()
    
    if success:
        logger.info("✅ Reddit API测试成功！")
    else:
        logger.error("❌ Reddit API测试失败！")

if __name__ == "__main__":
    asyncio.run(main())