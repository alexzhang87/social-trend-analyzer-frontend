import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.curl_twitter_service import CurlTwitterService
from app.utils.logger import logger

def test_curl_service():
    """
    测试基于 curl 的 Twitter 服务
    """
    logger.info("=== 测试 CurlTwitterService ===")
    
    # 初始化服务
    service = CurlTwitterService()
    
    # 1. 测试连接
    logger.info("\n1. 测试连接...")
    if service.test_connection():
        logger.info("✅ 连接测试通过")
    else:
        logger.error("❌ 连接测试失败")
        return False
    
    # 2. 测试用户搜索
    logger.info("\n2. 测试用户搜索...")
    users = service.search_users("tesla", count=5)
    
    if users:
        logger.info(f"✅ 成功获取 {len(users)} 个用户")
        for i, user in enumerate(users[:3], 1):
            logger.info(f"  {i}. @{user.get('screen_name', 'unknown')} - {user.get('followers_count', 0)} 关注者")
    else:
        logger.error("❌ 用户搜索失败")
        return False
    
    # 3. 测试趋势内容生成
    logger.info("\n3. 测试趋势内容生成...")
    trending_content = service.get_trending_content_via_users("tesla", limit=10)
    
    if trending_content:
        logger.info(f"✅ 成功生成 {len(trending_content)} 条趋势内容")
        for i, content in enumerate(trending_content[:3], 1):
            logger.info(f"  {i}. {content['author']}: {content['text'][:100]}...")
    else:
        logger.error("❌ 趋势内容生成失败")
        return False
    
    logger.info("\n=== 测试完成 ===")
    logger.info("✅ 所有测试通过！CurlTwitterService 工作正常")
    return True

if __name__ == "__main__":
    success = test_curl_service()
    if not success:
        logger.error("❌ 服务测试失败")
        sys.exit(1)
    else:
        logger.info("🎉 服务测试成功！")