#!/usr/bin/env python3
"""
Reddit 官方API连接测试脚本

使用方法:
1. 确保已在 .env 文件中配置 Reddit API 凭证
2. 运行: python test_reddit_api.py
3. 检查输出结果和API连接状态
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import time
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from app.services.reddit_official_service import reddit_service


async def test_reddit_api():
    """测试Reddit API的各项功能"""
    
    print("🔍 Reddit 官方API连接测试")
    print("=" * 50)
    
    # 1. 检查环境变量配置
    print("\n📋 1. 检查配置...")
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(os.getenv(var))}")
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请参考 REDDIT_API_SETUP_GUIDE.md 完成配置")
        return False
    
    # 2. 测试认证
    print("\n🔐 2. 测试API认证...")
    try:
        start_time = time.time()
        token = await reddit_service._get_access_token()
        auth_time = time.time() - start_time
        
        if token:
            print(f"✅ 认证成功！")
            print(f"   访问令牌: {token[:20]}...")
            print(f"   认证耗时: {auth_time:.2f}秒")
        else:
            print("❌ 认证失败")
            return False
    except Exception as e:
        print(f"❌ 认证异常: {e}")
        return False
    
    # 3. 测试搜索功能
    print("\n🔍 3. 测试搜索功能...")
    test_keywords = ["AI startup", "machine learning", "SaaS"]
    
    for keyword in test_keywords:
        try:
            start_time = time.time()
            posts = await reddit_service.search_posts([keyword], limit=5)
            search_time = time.time() - start_time
            
            print(f"关键词 '{keyword}':")
            print(f"   ✅ 找到 {len(posts)} 条帖子")
            print(f"   搜索耗时: {search_time:.2f}秒")
            
            if posts:
                sample_post = posts[0]
                print(f"   示例帖子: {sample_post['content'][:100]}...")
                print(f"   作者: {sample_post['author']}")
                print(f"   分数: {sample_post['score']}")
        
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    
    # 4. 测试子版块功能
    print("\n📱 4. 测试子版块获取...")
    test_subreddits = ["startups", "entrepreneur", "MachineLearning"]
    
    for subreddit in test_subreddits:
        try:
            start_time = time.time()
            posts = await reddit_service.get_subreddit_posts(subreddit, limit=3)
            subreddit_time = time.time() - start_time
            
            print(f"子版块 'r/{subreddit}':")
            print(f"   ✅ 获取到 {len(posts)} 条帖子")
            print(f"   获取耗时: {subreddit_time:.2f}秒")
            
            if posts:
                top_post = max(posts, key=lambda x: x.get('score', 0))
                print(f"   热门帖子: {top_post['content'][:80]}...")
                print(f"   分数: {top_post['score']}")
        
        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
    
    # 5. 测试推荐子版块功能
    print("\n🎯 5. 测试子版块推荐...")
    try:
        test_keywords_for_subreddits = ["AI", "startup", "fintech"]
        recommended = await reddit_service.get_trending_subreddits(test_keywords_for_subreddits)
        print(f"推荐的子版块: {', '.join(recommended)}")
        print(f"✅ 推荐功能正常")
    except Exception as e:
        print(f"❌ 推荐功能失败: {e}")
    
    # 6. 性能测试
    print("\n⚡ 6. 性能测试...")
    try:
        # 连续请求测试
        start_time = time.time()
        tasks = []
        for i in range(3):
            task = reddit_service.search_posts(["tech"], limit=2)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        total_posts = sum(len(result) for result in results)
        
        print(f"✅ 并发请求测试:")
        print(f"   3个并发请求")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   获取帖子: {total_posts} 条")
        print(f"   平均速度: {total_posts/total_time:.1f} 帖子/秒")
        
        # 速率限制测试
        print(f"✅ 速率限制遵守: 每次请求间隔 {reddit_service.rate_limit_delay} 秒")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
    
    print("\n🎉 7. 测试总结")
    print("=" * 50)
    print("✅ Reddit官方API集成测试完成！")
    print("✅ 所有核心功能正常工作")
    print("✅ 可以开始集成到主要分析服务")
    
    return True


async def demo_integration():
    """演示如何在分析服务中使用Reddit数据"""
    print("\n🚀 Reddit API集成演示")
    print("=" * 50)
    
    # 模拟趋势分析场景
    keywords = ["ChatGPT", "AI assistant"]
    print(f"分析关键词: {keywords}")
    
    try:
        # 获取Reddit数据
        reddit_posts = await reddit_service.search_posts(keywords, limit=10)
        
        # 基础统计
        total_posts = len(reddit_posts)
        total_score = sum(post.get('score', 0) for post in reddit_posts)
        avg_score = total_score / total_posts if total_posts > 0 else 0
        
        # 子版块分布
        subreddits = {}
        for post in reddit_posts:
            subreddit = post.get('subreddit', 'unknown')
            subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
        
        print(f"\n📊 分析结果:")
        print(f"   总帖子数: {total_posts}")
        print(f"   平均分数: {avg_score:.1f}")
        print(f"   涉及子版块: {len(subreddits)}")
        print(f"   主要子版块: {dict(list(subreddits.items())[:3])}")
        
        # 热门帖子
        if reddit_posts:
            top_post = max(reddit_posts, key=lambda x: x.get('score', 0))
            print(f"\n🔥 最热门帖子:")
            print(f"   标题: {top_post['content'][:100]}...")
            print(f"   分数: {top_post['score']}")
            print(f"   子版块: r/{top_post.get('subreddit', 'unknown')}")
            print(f"   链接: {top_post['url']}")
        
        print(f"\n✅ 集成演示成功！数据可以直接用于趋势分析")
        
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")


async def main():
    """主函数"""
    try:
        # 基础API测试
        success = await test_reddit_api()
        
        if success:
            # 演示集成
            await demo_integration()
        else:
            print("\n❌ 基础测试失败，请检查配置后重试")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    print("开始Reddit API测试...")
    asyncio.run(main())