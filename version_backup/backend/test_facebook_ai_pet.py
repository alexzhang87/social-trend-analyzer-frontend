#!/usr/bin/env python3
"""
专门测试Facebook页面抓取AI pet相关内容
"""

import asyncio
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.snscrape_service import SNScrapeService
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_facebook_ai_pet_pages():
    """测试Facebook AI pet相关页面抓取"""
    logger.info("=== 测试Facebook AI pet页面抓取 ===")
    
    snscrape = SNScrapeService()
    
    # AI pet相关的页面名称（这些是可能存在的公司或产品页面）
    ai_pet_pages = [
        "Animo",  # AI宠物应用
        "Replika",  # AI伴侣
        "Vector",  # Anki的AI机器人
        "Sony",  # 制造AIBO的公司
        "Boston Dynamics",  # 机器人公司
        "Tesla",  # 有机器人项目
        "OpenAI",  # AI公司
        "Microsoft",  # 测试知名页面
        "Petoi",  # 机器宠物公司
        "Unitree"  # 机器狗公司
    ]
    
    all_results = {}
    
    for page_name in ai_pet_pages:
        logger.info(f"\n--- 测试页面: {page_name} ---")
        
        try:
            posts = await snscrape.scrape_facebook_page(
                page_name=page_name,
                limit=3
            )
            
            logger.info(f"从 {page_name} 页面抓取到 {len(posts)} 条帖子")
            
            if posts:
                all_results[page_name] = posts
                
                for i, post in enumerate(posts):
                    logger.info(f"\n📱 帖子 {i+1}:")
                    logger.info(f"   内容: {post.get('content', '')[:150]}...")
                    logger.info(f"   作者: {post.get('user', {}).get('name', 'Unknown')}")
                    logger.info(f"   时间: {post.get('created_at', 'Unknown')}")
                    logger.info(f"   URL: {post.get('url', 'No URL')}")
                    
                    metrics = post.get('metrics', {})
                    logger.info(f"   互动: 👍{metrics.get('like_count', 0)} 💬{metrics.get('comment_count', 0)} 🔄{metrics.get('share_count', 0)}")
                    
                    # 检查是否包含AI pet相关关键词
                    content = post.get('content', '').lower()
                    ai_keywords = ['ai', 'artificial intelligence', 'robot', 'pet', 'companion', 'smart', 'autonomous']
                    found_keywords = [kw for kw in ai_keywords if kw in content]
                    if found_keywords:
                        logger.info(f"   🔍 包含AI相关关键词: {found_keywords}")
            else:
                logger.info(f"   ❌ 无法获取 {page_name} 的内容")
                
        except Exception as e:
            logger.error(f"   ❌ 抓取 {page_name} 时出错: {e}")
            
        # 添加延迟避免请求过快
        await asyncio.sleep(1)
    
    return all_results

async def test_facebook_ai_pet_search():
    """测试Facebook搜索AI pet相关内容"""
    logger.info("\n=== 测试Facebook AI pet搜索 ===")
    
    snscrape = SNScrapeService()
    
    # AI pet相关的搜索关键词
    search_queries = [
        "AI pet",
        "artificial intelligence pet",
        "robot dog",
        "smart pet",
        "AI companion",
        "robotic pet"
    ]
    
    all_search_results = {}
    
    for query in search_queries:
        logger.info(f"\n--- 搜索关键词: '{query}' ---")
        
        try:
            posts = await snscrape.scrape_facebook_search(
                query=query,
                limit=3,
                post_type="posts"
            )
            
            logger.info(f"搜索 '{query}' 找到 {len(posts)} 条帖子")
            
            if posts:
                all_search_results[query] = posts
                
                for i, post in enumerate(posts):
                    logger.info(f"\n🔍 搜索结果 {i+1}:")
                    logger.info(f"   内容: {post.get('content', '')[:150]}...")
                    logger.info(f"   作者: {post.get('user', {}).get('name', 'Unknown')}")
                    logger.info(f"   时间: {post.get('created_at', 'Unknown')}")
                    
                    metrics = post.get('metrics', {})
                    logger.info(f"   互动: 👍{metrics.get('like_count', 0)} 💬{metrics.get('comment_count', 0)}")
            else:
                logger.info(f"   ❌ 搜索 '{query}' 无结果")
                
        except Exception as e:
            logger.error(f"   ❌ 搜索 '{query}' 时出错: {e}")
            
        await asyncio.sleep(1)
    
    return all_search_results

async def analyze_scraped_content(page_results, search_results):
    """分析抓取到的内容"""
    logger.info("\n" + "="*60)
    logger.info("📊 内容分析报告")
    logger.info("="*60)
    
    total_posts = 0
    ai_related_posts = 0
    
    # 分析页面抓取结果
    logger.info("\n📄 页面抓取结果分析:")
    for page_name, posts in page_results.items():
        total_posts += len(posts)
        page_ai_posts = 0
        
        for post in posts:
            content = post.get('content', '').lower()
            ai_keywords = ['ai', 'artificial intelligence', 'robot', 'pet', 'companion', 'smart', 'autonomous', 'machine learning']
            if any(kw in content for kw in ai_keywords):
                ai_related_posts += 1
                page_ai_posts += 1
        
        logger.info(f"   {page_name}: {len(posts)} 条帖子, {page_ai_posts} 条AI相关")
    
    # 分析搜索结果
    logger.info(f"\n🔍 搜索结果分析:")
    for query, posts in search_results.items():
        total_posts += len(posts)
        ai_related_posts += len(posts)  # 搜索结果默认为AI相关
        logger.info(f"   '{query}': {len(posts)} 条结果")
    
    logger.info(f"\n📈 总体统计:")
    logger.info(f"   总帖子数: {total_posts}")
    logger.info(f"   AI相关帖子: {ai_related_posts}")
    logger.info(f"   AI相关比例: {ai_related_posts/total_posts*100:.1f}%" if total_posts > 0 else "   无数据")
    
    # 数据质量评估
    logger.info(f"\n🎯 数据质量评估:")
    if total_posts == 0:
        logger.info("   ❌ 未获取到任何数据")
    elif total_posts < 10:
        logger.info("   ⚠️ 数据量较少，可能存在访问限制")
    else:
        logger.info("   ✅ 数据获取正常")

async def save_results_to_file(page_results, search_results):
    """将结果保存到文件"""
    results = {
        "page_results": page_results,
        "search_results": search_results,
        "timestamp": asyncio.get_event_loop().time(),
        "summary": {
            "total_pages_tested": len(page_results),
            "total_searches_tested": len(search_results),
            "total_posts": sum(len(posts) for posts in page_results.values()) + sum(len(posts) for posts in search_results.values())
        }
    }
    
    output_file = "facebook_ai_pet_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n💾 结果已保存到: {output_file}")
    except Exception as e:
        logger.error(f"❌ 保存结果时出错: {e}")

async def main():
    """主函数"""
    logger.info("🚀 开始Facebook AI pet内容抓取测试...")
    
    try:
        # 测试页面抓取
        page_results = await test_facebook_ai_pet_pages()
        
        # 测试搜索功能
        search_results = await test_facebook_ai_pet_search()
        
        # 分析结果
        await analyze_scraped_content(page_results, search_results)
        
        # 保存结果
        await save_results_to_file(page_results, search_results)
        
        logger.info("\n✅ 测试完成!")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())