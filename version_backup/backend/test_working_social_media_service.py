import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.working_social_media_service import WorkingSocialMediaService
from app.utils.logger import logger

async def test_working_social_media_service():
    """
    测试可工作的社交媒体服务
    """
    logger.info("=== 测试 WorkingSocialMediaService ===")
    
    # 初始化服务
    service = WorkingSocialMediaService()
    
    # 1. 测试连接
    logger.info("\n1. 测试连接...")
    if await service.test_connection():
        logger.info("✅ 连接测试通过")
    else:
        logger.error("❌ 连接测试失败")
        return False
    
    # 2. 测试 Twitter 帖子获取
    logger.info("\n2. 测试 Twitter 帖子获取...")
    twitter_posts = await service.get_twitter_posts("tesla", limit=10)
    
    if twitter_posts:
        logger.info(f"✅ 成功获取 {len(twitter_posts)} 条 Twitter 帖子")
        for i, post in enumerate(twitter_posts[:3], 1):
            logger.info(f"  {i}. @{post['author']}: {post['text'][:80]}...")
    else:
        logger.error("❌ Twitter 帖子获取失败")
        return False
    
    # 3. 测试 Reddit 帖子获取
    logger.info("\n3. 测试 Reddit 帖子获取...")
    reddit_posts = await service.get_reddit_posts("technology", limit=5)
    
    if reddit_posts:
        logger.info(f"✅ 成功获取 {len(reddit_posts)} 条 Reddit 帖子")
        for i, post in enumerate(reddit_posts[:3], 1):
            logger.info(f"  {i}. {post['title']}: {post['text'][:80]}...")
    else:
        logger.error("❌ Reddit 帖子获取失败")
        return False
    
    logger.info("\n=== 测试完成 ===")
    logger.info("🎉 所有测试通过！WorkingSocialMediaService 工作正常")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_working_social_media_service())
    if not success:
        logger.error("❌ 服务测试失败")
        sys.exit(1)
    else:
        logger.info("🎉 服务测试成功！")