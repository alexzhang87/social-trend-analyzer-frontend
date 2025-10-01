import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.working_twitter_service import WorkingTwitterService
from app.utils.logger import logger

def test_working_service():
    """测试基于实际可用端点的服务"""
    logger.info("=== 测试 WorkingTwitterService ===")
    
    service = WorkingTwitterService()
    
    # 1. 测试所有端点
    logger.info("\n1. 测试所有可用端点...")
    available_endpoints = service.test_all_available_endpoints()
    
    # 2. 测试用户搜索（我们知道这个可用）
    logger.info("\n2. 测试用户搜索...")
    users = service.search_users("tesla", count=5)
    if users:
        logger.info(f"✅ 成功找到 {len(users)} 个用户")
        for user in users[:3]:
            logger.info(f"  - @{user.get('screen_name', 'unknown')}: {user.get('followers_count', 0)} 关注者")
    else:
        logger.warning("❌ 用户搜索失败")
    
    # 3. 测试基于用户的趋势内容生成
    logger.info("\n3. 测试趋势内容生成...")
    trending_content = service.get_trending_content_via_users("tesla", limit=10)
    if trending_content:
        logger.info(f"✅ 成功生成 {len(trending_content)} 条趋势内容")
        for item in trending_content[:3]:
            logger.info(f"  - {item['author']}: {item['text'][:100]}...")
    else:
        logger.warning("❌ 趋势内容生成失败")
    
    # 4. 如果找到了用户，尝试获取他们的推文
    if users:
        logger.info("\n4. 尝试获取用户推文...")
        first_user_id = users[0].get('id')
        if first_user_id:
            tweets = service.get_user_tweets_alternative_method(first_user_id, count=5)
            if tweets:
                logger.info(f"✅ 成功获取 {len(tweets)} 条推文")
            else:
                logger.info("ℹ️ 无法获取推文，但这是预期的")
    
    logger.info("\n=== 测试完成 ===")
    return len(users) > 0 and len(trending_content) > 0

if __name__ == "__main__":
    success = test_working_service()
    if success:
        logger.info("🎉 服务测试成功！我们有了一个可用的解决方案。")
    else:
        logger.error("❌ 服务测试失败")