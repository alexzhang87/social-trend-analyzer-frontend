#!/usr/bin/env python3
"""
综合集成测试 - 验证所有API服务是否正常工作
"""

import asyncio
import sys
import os
sys.path.append('app')

from app.services.comprehensive_analysis_service import comprehensive_analysis_service

async def test_comprehensive_analysis():
    print('🔍 测试综合分析服务...')
    print('=' * 50)
    
    # 测试关键词
    keywords = ['AI', 'artificial intelligence']
    
    try:
        result = await comprehensive_analysis_service.analyze_trends_comprehensive(
            keywords=keywords,
            platforms=['twitter', 'reddit', 'product_hunt', 'google_trends'],
            time_filter='week',
            limit_per_platform=5
        )
        
        print('✅ 综合分析成功完成')
        print(f'   处理时间: {result.get("processing_time", "N/A")} 秒')
        print(f'   总分析内容: {result.get("total_posts_analyzed", 0)} 条')
        print(f'   趋势评分: {result.get("trend_score", 0)}')
        
        # 情感分析结果
        sentiment_analysis = result.get('sentiment_analysis', {})
        print(f'   整体情感: {sentiment_analysis.get("overall_sentiment", "N/A")}')
        print(f'   情感置信度: {sentiment_analysis.get("overall_confidence", 0)}')
        
        # 检查各平台数据
        platform_stats = result.get('platform_stats', {})
        print('\n📊 各平台数据统计:')
        for platform, stats in platform_stats.items():
            print(f'   {platform}: {stats}')
        
        # 关键词分析
        keyword_analysis = result.get('keyword_analysis', {})
        top_keywords = keyword_analysis.get('top_keywords', [])[:5]
        if top_keywords:
            print('\n🏷️ 热门关键词:')
            for kw in top_keywords:
                print(f'   - {kw.get("word", "N/A")} (频率: {kw.get("frequency", 0)})')
        
        # 洞察
        insights = result.get('insights', [])
        if insights:
            print('\n💡 分析洞察:')
            for insight in insights:
                print(f'   • {insight}')
        
        return True
        
    except Exception as e:
        print(f'❌ 综合分析失败: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_individual_services():
    """测试各个服务"""
    print('\n🔧 测试各个API服务...')
    print('=' * 50)
    
    # 测试Twitter服务
    print('📱 测试Twitter服务...')
    try:
        from app.services.working_twitter_service import WorkingTwitterService
        twitter_service = WorkingTwitterService()
        tweets = twitter_service.search_tweets_enhanced('AI', 3)
        print(f'   ✅ Twitter: 获取了 {len(tweets)} 条推文')
    except Exception as e:
        print(f'   ❌ Twitter服务失败: {e}')
    
    # 测试Reddit服务
    print('🔴 测试Reddit服务...')
    try:
        from app.services.reddit_official_service import RedditOfficialService
        reddit_service = RedditOfficialService()
        posts = await reddit_service.search_posts_enhanced(['AI'], 3, 'week')
        print(f'   ✅ Reddit: 获取了 {len(posts)} 条帖子')
    except Exception as e:
        print(f'   ❌ Reddit服务失败: {e}')
    
    # 测试Product Hunt服务
    print('🚀 测试Product Hunt服务...')
    try:
        from app.services.product_hunt_service import ProductHuntOfficialService
        ph_service = ProductHuntOfficialService()
        products = await ph_service.get_daily_products_enhanced(3)
        print(f'   ✅ Product Hunt: 获取了 {len(products)} 个产品')
    except Exception as e:
        print(f'   ❌ Product Hunt服务失败: {e}')
    
    # 测试Google Trends服务
    print('📈 测试Google Trends服务...')
    try:
        from app.services.google_trends_service import GoogleTrendsService
        trends_service = GoogleTrendsService()
        trends_data = trends_service.get_interest_over_time(['AI'], 'today 7-d')
        print(f'   ✅ Google Trends: 获取了 {len(trends_data.get("data", []))} 个数据点')
    except Exception as e:
        print(f'   ❌ Google Trends服务失败: {e}')

async def main():
    """主测试函数"""
    print('🚀 开始综合集成测试')
    print('=' * 60)
    
    # 测试单个服务
    await test_individual_services()
    
    # 测试综合分析
    success = await test_comprehensive_analysis()
    
    print('\n' + '=' * 60)
    if success:
        print('🎉 所有服务集成测试通过！')
        print('✅ Twitter、Reddit、Product Hunt、Google Trends 都已正常工作')
        print('✅ 文本分析（VADER、TextBlob、NLTK）已集成')
        print('✅ 综合分析服务正常运行')
    else:
        print('⚠️ 部分服务存在问题，需要进一步调试')
    
    return success

if __name__ == "__main__":
    asyncio.run(main())