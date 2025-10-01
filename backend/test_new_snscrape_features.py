#!/usr/bin/env python3
"""
测试新的snscrape功能：YouTube评论和Facebook数据抓取
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.snscrape_service import SNScrapeService
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_twitter_io_api():
    """测试Twitter.io API功能"""
    logger.info("=== 测试Twitter.io API ===")
    
    snscrape = SNScrapeService()
    
    try:
        # 测试Twitter搜索
        posts = await snscrape.scrape_twitter_search(
            query="AI",
            limit=5
        )
        
        logger.info(f"成功抓取到 {len(posts)} 条Twitter推文")
        
        if posts:
            logger.info("推文样本：")
            for i, post in enumerate(posts[:2]):
                logger.info(f"推文 {i+1}:")
                logger.info(f"  作者: @{post.get('user', {}).get('username', 'Unknown')}")
                logger.info(f"  内容: {post.get('content', '')[:100]}...")
                logger.info(f"  点赞数: {post.get('metrics', {}).get('like_count', 0)}")
                logger.info(f"  转发数: {post.get('metrics', {}).get('retweet_count', 0)}")
                logger.info(f"  URL: {post.get('url', '')}")
                logger.info("  ---")
        
        return True
        
    except Exception as e:
        logger.error(f"Twitter.io API测试失败: {e}")
        return False

async def test_instagram_hashtag():
    """测试Instagram hashtag抓取"""
    logger.info("=== 测试Instagram hashtag抓取 ===")
    
    snscrape = SNScrapeService()
    
    try:
        # 测试抓取AI相关的Instagram内容
        posts = await snscrape.scrape_instagram_hashtag(
            hashtag="ai",
            limit=10
        )
        
        logger.info(f"成功抓取到 {len(posts)} 条Instagram内容")
        
        if posts:
            logger.info("内容样本：")
            for i, post in enumerate(posts[:3]):
                logger.info(f"帖子 {i+1}:")
                logger.info(f"  作者: {post.get('user', {}).get('username', 'Unknown')}")
                logger.info(f"  内容: {post.get('caption', '')[:100]}...")
                logger.info(f"  点赞数: {post.get('metrics', {}).get('like_count', 0)}")
                logger.info(f"  评论数: {post.get('metrics', {}).get('comment_count', 0)}")
                logger.info(f"  URL: {post.get('url', '')}")
                logger.info("  ---")
        
        return True
        
    except Exception as e:
        logger.error(f"Instagram hashtag抓取测试失败: {e}")
        return False

async def test_facebook_search():
    """测试Facebook搜索"""
    logger.info("=== 测试Facebook搜索 ===")
    
    snscrape = SNScrapeService()
    
    try:
        # 测试Facebook帖子搜索
        posts = await snscrape.scrape_facebook_search(
            query="artificial intelligence",
            limit=5,
            post_type="posts"
        )
        
        logger.info(f"成功抓取到 {len(posts)} 条Facebook帖子")
        
        if posts:
            logger.info("帖子样本：")
            for i, post in enumerate(posts[:2]):
                logger.info(f"帖子 {i+1}:")
                logger.info(f"  作者: {post.get('user', {}).get('name', 'Unknown')}")
                logger.info(f"  内容: {post.get('content', '')[:100]}...")
                logger.info(f"  点赞数: {post.get('metrics', {}).get('like_count', 0)}")
                logger.info(f"  评论数: {post.get('metrics', {}).get('comment_count', 0)}")
                logger.info("  ---")
        
        return True
        
    except Exception as e:
        logger.error(f"Facebook搜索测试失败: {e}")
        return False

async def test_facebook_page():
    """测试Facebook页面抓取"""
    logger.info("=== 测试Facebook页面抓取 ===")
    
    snscrape = SNScrapeService()
    
    try:
        # 测试知名页面（如Microsoft、Google等）
        pages_to_test = ["Microsoft", "Google", "OpenAI"]
        
        for page_name in pages_to_test[:1]:  # 只测试第一个
            logger.info(f"测试页面: {page_name}")
            
            posts = await snscrape.scrape_facebook_page(
                page_name=page_name,
                limit=3
            )
            
            logger.info(f"从 {page_name} 页面抓取到 {len(posts)} 条帖子")
            
            if posts:
                for i, post in enumerate(posts[:1]):
                    logger.info(f"  帖子: {post.get('content', '')[:80]}...")
                    logger.info(f"  互动数: {post.get('metrics', {}).get('like_count', 0)} 赞")
        
        return True
        
    except Exception as e:
        logger.error(f"Facebook页面抓取测试失败: {e}")
        return False

async def test_cross_platform():
    """测试跨平台搜索（包含新平台）"""
    logger.info("=== 测试跨平台搜索 ===")
    
    snscrape = SNScrapeService()
    
    try:
        # 获取支持的平台
        platforms = snscrape.get_supported_platforms()
        logger.info(f"支持的平台: {platforms}")
        
        # 跨平台搜索
        results = await snscrape.scrape_cross_platform(
            query="machine learning",
            platforms=platforms[:3],  # 选择前3个平台
            limit_per_platform=3
        )
        
        logger.info("跨平台搜索结果:")
        for platform, data in results.items():
            logger.info(f"  {platform}: {len(data)} 条数据")
        
        return True
        
    except Exception as e:
        logger.error(f"跨平台搜索测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    logger.info("开始测试新的snscrape功能...")
    
    tests = [
        ("Twitter.io API测试", test_twitter_io_api),
        ("Instagram hashtag抓取", test_instagram_hashtag),
        ("Facebook搜索", test_facebook_search),
        ("Facebook页面抓取", test_facebook_page),
        ("跨平台搜索", test_cross_platform)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"执行测试: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results[test_name] = result
            logger.info(f"✅ {test_name} - {'通过' if result else '失败'}")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
            results[test_name] = False
    
    # 总结
    logger.info(f"\n{'='*50}")
    logger.info("测试总结:")
    logger.info(f"{'='*50}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！新功能工作正常。")
    else:
        logger.warning("⚠️ 部分测试失败，请检查配置和依赖。")

if __name__ == "__main__":
    asyncio.run(main())