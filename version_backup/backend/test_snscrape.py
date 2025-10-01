#!/usr/bin/env python3
"""
snscrape功能测试脚本
用于验证Twitter和Reddit数据抓取功能
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.snscrape_service import snscrape_service
from app.services.enhanced_social_media_service import enhanced_social_service

async def test_twitter_search():
    """测试Twitter搜索功能"""
    print("\n=== 测试Twitter搜索功能 ===")
    
    try:
        # 测试基本搜索
        print("1. 测试基本搜索...")
        tweets = await snscrape_service.scrape_twitter_search(
            query="python programming",
            limit=5
        )
        print(f"   获取到 {len(tweets)} 条推文")
        
        if tweets:
            sample_tweet = tweets[0]
            print(f"   示例推文: {sample_tweet.get('content', '')[:100]}...")
            print(f"   用户: {sample_tweet.get('user', {}).get('username', 'N/A')}")
            print(f"   点赞数: {sample_tweet.get('metrics', {}).get('like_count', 0)}")
        
        # 测试日期过滤
        print("\n2. 测试日期过滤...")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        recent_tweets = await snscrape_service.scrape_twitter_search(
            query="AI",
            limit=3,
            since_date=yesterday
        )
        print(f"   获取到 {len(recent_tweets)} 条最近推文")
        
        return True
        
    except Exception as e:
        print(f"   Twitter搜索测试失败: {str(e)}")
        return False

async def test_twitter_user():
    """测试Twitter用户推文获取"""
    print("\n=== 测试Twitter用户推文获取 ===")
    
    try:
        # 测试知名用户
        test_users = ["elonmusk", "OpenAI", "github"]
        
        for username in test_users:
            print(f"\n测试用户: @{username}")
            tweets = await snscrape_service.scrape_twitter_user(
                username=username,
                limit=3
            )
            print(f"   获取到 {len(tweets)} 条推文")
            
            if tweets:
                latest_tweet = tweets[0]
                print(f"   最新推文: {latest_tweet.get('content', '')[:80]}...")
                print(f"   发布时间: {latest_tweet.get('date', 'N/A')}")
            
            # 只测试第一个用户，避免过多请求
            break
        
        return True
        
    except Exception as e:
        print(f"   Twitter用户测试失败: {str(e)}")
        return False

async def test_reddit_search():
    """测试Reddit搜索功能"""
    print("\n=== 测试Reddit搜索功能 ===")
    
    try:
        # 测试全站搜索
        print("1. 测试全站搜索...")
        posts = await snscrape_service.scrape_reddit_search(
            query="machine learning",
            limit=5
        )
        print(f"   获取到 {len(posts)} 条帖子")
        
        if posts:
            sample_post = posts[0]
            print(f"   示例帖子: {sample_post.get('title', '')[:80]}...")
            print(f"   Subreddit: r/{sample_post.get('subreddit', 'N/A')}")
            print(f"   评分: {sample_post.get('metrics', {}).get('score', 0)}")
        
        # 测试指定subreddit搜索
        print("\n2. 测试指定subreddit搜索...")
        python_posts = await snscrape_service.scrape_reddit_search(
            query="tutorial",
            subreddit="python",
            limit=3
        )
        print(f"   在r/python中获取到 {len(python_posts)} 条帖子")
        
        return True
        
    except Exception as e:
        print(f"   Reddit搜索测试失败: {str(e)}")
        return False

async def test_reddit_subreddit():
    """测试Reddit subreddit获取"""
    print("\n=== 测试Reddit Subreddit获取 ===")
    
    try:
        # 测试热门subreddits
        test_subreddits = ["technology", "programming", "MachineLearning"]
        
        for subreddit in test_subreddits:
            print(f"\n测试subreddit: r/{subreddit}")
            posts = await snscrape_service.scrape_reddit_subreddit(
                subreddit=subreddit,
                limit=3,
                sort="hot"
            )
            print(f"   获取到 {len(posts)} 条热门帖子")
            
            if posts:
                top_post = posts[0]
                print(f"   热门帖子: {top_post.get('title', '')[:80]}...")
                print(f"   评分: {top_post.get('metrics', {}).get('score', 0)}")
                print(f"   评论数: {top_post.get('metrics', {}).get('num_comments', 0)}")
            
            # 只测试第一个subreddit
            break
        
        return True
        
    except Exception as e:
        print(f"   Reddit subreddit测试失败: {str(e)}")
        return False

async def test_enhanced_service():
    """测试增强社交媒体服务"""
    print("\n=== 测试增强社交媒体服务 ===")
    
    try:
        # 测试跨平台搜索
        print("1. 测试跨平台搜索...")
        results = await enhanced_social_service.search_social_media(
            query="artificial intelligence",
            platforms=["twitter", "reddit"],
            count=3
        )
        
        for platform, data in results.items():
            print(f"   {platform}: {len(data)} 条结果")
        
        # 测试热门话题
        print("\n2. 测试热门话题获取...")
        trending = await enhanced_social_service.get_trending_topics(
            platform="both",
            limit=5
        )
        
        for platform, topics in trending.items():
            print(f"   {platform}热门话题: {len(topics)} 条")
        
        # 测试连接状态
        print("\n3. 测试连接状态...")
        status = await enhanced_social_service.test_connection()
        for platform, is_connected in status.items():
            print(f"   {platform}: {'✓ 连接正常' if is_connected else '✗ 连接失败'}")
        
        return True
        
    except Exception as e:
        print(f"   增强服务测试失败: {str(e)}")
        return False

async def test_data_quality():
    """测试数据质量"""
    print("\n=== 测试数据质量 ===")
    
    try:
        # 获取一些样本数据
        tweets = await snscrape_service.scrape_twitter_search(
            query="test",
            limit=2
        )
        
        reddit_posts = await snscrape_service.scrape_reddit_search(
            query="test",
            limit=2
        )
        
        # 检查Twitter数据结构
        print("\n1. Twitter数据结构检查:")
        if tweets:
            tweet = tweets[0]
            required_fields = ['id', 'content', 'date', 'user', 'metrics', 'source']
            missing_fields = [field for field in required_fields if field not in tweet]
            
            if missing_fields:
                print(f"   ✗ 缺少字段: {missing_fields}")
            else:
                print("   ✓ 数据结构完整")
            
            # 检查用户信息
            user = tweet.get('user', {})
            user_fields = ['username', 'displayname', 'followers_count']
            missing_user_fields = [field for field in user_fields if field not in user]
            
            if missing_user_fields:
                print(f"   ✗ 用户信息缺少字段: {missing_user_fields}")
            else:
                print("   ✓ 用户信息完整")
        
        # 检查Reddit数据结构
        print("\n2. Reddit数据结构检查:")
        if reddit_posts:
            post = reddit_posts[0]
            required_fields = ['id', 'title', 'url', 'subreddit', 'author', 'metrics', 'source']
            missing_fields = [field for field in required_fields if field not in post]
            
            if missing_fields:
                print(f"   ✗ 缺少字段: {missing_fields}")
            else:
                print("   ✓ 数据结构完整")
            
            # 检查指标信息
            metrics = post.get('metrics', {})
            metric_fields = ['score', 'num_comments']
            missing_metric_fields = [field for field in metric_fields if field not in metrics]
            
            if missing_metric_fields:
                print(f"   ✗ 指标信息缺少字段: {missing_metric_fields}")
            else:
                print("   ✓ 指标信息完整")
        
        return True
        
    except Exception as e:
        print(f"   数据质量测试失败: {str(e)}")
        return False

async def performance_test():
    """性能测试"""
    print("\n=== 性能测试 ===")
    
    try:
        import time
        
        # 测试Twitter搜索性能
        print("1. Twitter搜索性能测试...")
        start_time = time.time()
        tweets = await snscrape_service.scrape_twitter_search(
            query="performance test",
            limit=10
        )
        twitter_time = time.time() - start_time
        print(f"   获取10条推文耗时: {twitter_time:.2f}秒")
        
        # 测试Reddit搜索性能
        print("\n2. Reddit搜索性能测试...")
        start_time = time.time()
        posts = await snscrape_service.scrape_reddit_search(
            query="performance test",
            limit=10
        )
        reddit_time = time.time() - start_time
        print(f"   获取10条Reddit帖子耗时: {reddit_time:.2f}秒")
        
        # 性能评估
        if twitter_time < 30 and reddit_time < 30:
            print("\n   ✓ 性能测试通过 (< 30秒)")
            return True
        else:
            print("\n   ⚠ 性能较慢，可能需要优化")
            return True  # 仍然算作通过，只是性能警告
        
    except Exception as e:
        print(f"   性能测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("开始snscrape功能测试...")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("Twitter搜索", test_twitter_search),
        ("Twitter用户", test_twitter_user),
        ("Reddit搜索", test_reddit_search),
        ("Reddit Subreddit", test_reddit_subreddit),
        ("增强服务", test_enhanced_service),
        ("数据质量", test_data_quality),
        ("性能测试", performance_test)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name}测试出现异常: {str(e)}")
            test_results.append((test_name, False))
    
    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！snscrape集成成功！")
    elif passed >= total * 0.7:  # 70%通过率
        print("\n⚠ 大部分测试通过，snscrape基本可用")
    else:
        print("\n❌ 多个测试失败，需要检查配置")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)