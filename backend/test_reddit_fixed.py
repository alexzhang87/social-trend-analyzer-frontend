#!/usr/bin/env python3
"""
修复后的Reddit数据收集测试脚本
测试OAuth API是否正常工作
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from app.services.reddit_official_service import RedditOfficialService

async def test_reddit_oauth_api():
    """测试Reddit OAuth API"""
    print("=== Reddit OAuth API 测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建Reddit服务实例
    reddit_service = RedditOfficialService()
    
    # 测试关键词
    test_keywords = ["AI", "artificial intelligence", "machine learning"]
    
    print(f"\n🔍 搜索关键词: {test_keywords}")
    print("⏳ 正在搜索Reddit帖子...")
    
    try:
        # 搜索帖子
        posts = await reddit_service.search_posts(
            keywords=test_keywords,
            limit=10,
            time_filter="week",
            sort="relevance"
        )
        
        print(f"\n✅ 搜索完成！获取到 {len(posts)} 条帖子")
        
        if posts:
            print("\n📊 前5条帖子预览:")
            for i, post in enumerate(posts[:5], 1):
                print(f"\n{i}. 标题: {post.get('content', '')[:100]}...")
                print(f"   来源: r/{post.get('subreddit', 'unknown')}")
                print(f"   评分: {post.get('score', 0)} | 评论: {post.get('comments_count', 0)}")
                print(f"   发布时间: {post.get('published_at', 'unknown')}")
        
        # 保存测试结果
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'keywords': test_keywords,
            'posts_count': len(posts),
            'status': 'success',
            'posts': posts[:3]  # 保存前3条作为样本
        }
        
        filename = f"reddit_oauth_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        
        # 保存错误结果
        error_result = {
            'timestamp': datetime.now().isoformat(),
            'keywords': test_keywords,
            'status': 'error',
            'error': str(e)
        }
        
        filename = f"reddit_oauth_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 错误信息已保存: {filename}")
        
        return False

async def test_reddit_enhanced_search():
    """测试Reddit增强搜索功能"""
    print("\n=== Reddit 增强搜索测试 ===")
    
    reddit_service = RedditOfficialService()
    
    test_keywords = ["startup", "entrepreneur"]
    
    print(f"🔍 增强搜索关键词: {test_keywords}")
    print("⏳ 正在执行增强搜索...")
    
    try:
        # 增强搜索
        enhanced_posts = await reddit_service.search_posts_enhanced(
            keywords=test_keywords,
            limit=5,
            time_filter="week"
        )
        
        print(f"\n✅ 增强搜索完成！获取到 {len(enhanced_posts)} 条帖子")
        
        if enhanced_posts:
            print("\n📈 增强分析结果预览:")
            for i, post in enumerate(enhanced_posts[:3], 1):
                print(f"\n{i}. 内容: {post.get('content', '')[:80]}...")
                print(f"   情感分析: {post.get('sentiment_analysis', {}).get('label', 'unknown')}")
                print(f"   关键词: {', '.join(post.get('keywords', [])[:5])}")
                print(f"   质量评分: {post.get('quality_score', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 增强搜索测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Reddit API修复验证测试")
    
    # 检查环境变量
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {missing_vars}")
        print("请在.env文件中配置Reddit API凭据")
        return
    
    print("✅ 环境变量检查通过")
    
    # 运行测试
    test1_success = await test_reddit_oauth_api()
    test2_success = await test_reddit_enhanced_search()
    
    print("\n" + "="*50)
    print("📋 测试总结:")
    print(f"OAuth API测试: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"增强搜索测试: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n🎉 所有测试通过！Reddit API修复成功")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())