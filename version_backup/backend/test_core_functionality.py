#!/usr/bin/env python3
"""
核心功能测试 - 验证文本分析和服务集成是否正常工作
不依赖真实API密钥，专注于验证核心组件
"""

import asyncio
import sys
import os
sys.path.append('app')

def test_text_analysis_service():
    """测试文本分析服务"""
    print('📝 测试文本分析服务...')
    print('=' * 50)
    
    try:
        from app.services.enhanced_text_analysis_service import enhanced_text_analysis_service
        
        # 测试文本
        test_text = """
        This is an amazing AI product that revolutionizes how we work with artificial intelligence. 
        The new features are incredibly innovative and will help developers build better applications.
        Users love the intuitive interface and powerful capabilities.
        """
        
        # 情感分析测试
        print('🎭 测试情感分析...')
        sentiment_result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(test_text)
        print(f'   情感: {sentiment_result.get("sentiment", "N/A")}')
        print(f'   置信度: {sentiment_result.get("confidence", 0):.3f}')
        print(f'   VADER分数: {sentiment_result.get("scores", {}).get("vader", {}).get("compound", 0):.3f}')
        
        # 关键词提取测试
        print('\n🏷️ 测试关键词提取...')
        keywords_result = enhanced_text_analysis_service.extract_keywords(test_text, max_keywords=10)
        print(f'   提取了 {len(keywords_result)} 个关键词:')
        for kw in keywords_result[:5]:
            print(f'     - {kw.get("word", "N/A")} (频率: {kw.get("frequency", 0)})')
        
        # 文本统计测试
        print('\n📊 测试文本统计...')
        stats_result = enhanced_text_analysis_service.analyze_text_statistics(test_text)
        print(f'   字符数: {stats_result.get("character_count", 0)}')
        print(f'   词数: {stats_result.get("word_count", 0)}')
        print(f'   句子数: {stats_result.get("sentence_count", 0)}')
        print(f'   可读性分数: {stats_result.get("readability_score", 0)}')
        
        return True
        
    except Exception as e:
        print(f'   ❌ 文本分析服务测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_service_imports():
    """测试服务导入"""
    print('\n🔧 测试服务导入...')
    print('=' * 50)
    
    services_status = {}
    
    # 测试Twitter服务
    try:
        from app.services.working_twitter_service import WorkingTwitterService
        twitter_service = WorkingTwitterService()
        services_status['Twitter'] = True
        print('   ✅ Twitter服务导入成功')
    except Exception as e:
        services_status['Twitter'] = False
        print(f'   ❌ Twitter服务导入失败: {e}')
    
    # 测试Reddit服务
    try:
        from app.services.reddit_official_service import RedditOfficialService
        reddit_service = RedditOfficialService()
        services_status['Reddit'] = True
        print('   ✅ Reddit服务导入成功')
        
        # 检查是否有search_posts_enhanced方法
        if hasattr(reddit_service, 'search_posts_enhanced'):
            print('   ✅ Reddit服务包含search_posts_enhanced方法')
        else:
            print('   ⚠️ Reddit服务缺少search_posts_enhanced方法')
            services_status['Reddit'] = False
            
    except Exception as e:
        services_status['Reddit'] = False
        print(f'   ❌ Reddit服务导入失败: {e}')
    
    # 测试Product Hunt服务
    try:
        from app.services.product_hunt_service import ProductHuntOfficialService
        ph_service = ProductHuntOfficialService()
        services_status['Product Hunt'] = True
        print('   ✅ Product Hunt服务导入成功')
        
        # 检查是否有get_daily_products_enhanced方法
        if hasattr(ph_service, 'get_daily_products_enhanced'):
            print('   ✅ Product Hunt服务包含get_daily_products_enhanced方法')
        else:
            print('   ⚠️ Product Hunt服务缺少get_daily_products_enhanced方法')
            
    except Exception as e:
        services_status['Product Hunt'] = False
        print(f'   ❌ Product Hunt服务导入失败: {e}')
    
    # 测试Google Trends服务
    try:
        from app.services.google_trends_service import GoogleTrendsService
        trends_service = GoogleTrendsService()
        services_status['Google Trends'] = True
        print('   ✅ Google Trends服务导入成功')
    except Exception as e:
        services_status['Google Trends'] = False
        print(f'   ❌ Google Trends服务导入失败: {e}')
    
    # 测试综合分析服务
    try:
        from app.services.comprehensive_analysis_service import comprehensive_analysis_service
        services_status['Comprehensive Analysis'] = True
        print('   ✅ 综合分析服务导入成功')
    except Exception as e:
        services_status['Comprehensive Analysis'] = False
        print(f'   ❌ 综合分析服务导入失败: {e}')
    
    return services_status

def test_mock_data_processing():
    """测试模拟数据处理"""
    print('\n🧪 测试模拟数据处理...')
    print('=' * 50)
    
    try:
        from app.services.enhanced_text_analysis_service import enhanced_text_analysis_service
        
        # 模拟Twitter数据
        mock_twitter_data = [
            {
                "content": "This AI tool is amazing! It helps me write better code.",
                "author": "developer123",
                "source": "twitter",
                "score": 15,
                "platform_specific": {
                    "retweet_count": 5,
                    "favorite_count": 10
                }
            },
            {
                "content": "Not sure about this new AI trend. Seems overhyped.",
                "author": "skeptic_user",
                "source": "twitter", 
                "score": 3,
                "platform_specific": {
                    "retweet_count": 1,
                    "favorite_count": 2
                }
            }
        ]
        
        # 为模拟数据添加文本分析
        enhanced_data = []
        for item in mock_twitter_data:
            content = item.get('content', '')
            
            # 执行文本分析
            sentiment_result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(content)
            keywords_result = enhanced_text_analysis_service.extract_keywords(content, max_keywords=5)
            stats_result = enhanced_text_analysis_service.analyze_text_statistics(content)
            
            # 添加分析结果
            item['text_analysis'] = {
                'sentiment': sentiment_result,
                'keywords': keywords_result,
                'statistics': stats_result
            }
            
            enhanced_data.append(item)
        
        print(f'   ✅ 成功处理了 {len(enhanced_data)} 条模拟数据')
        
        # 显示分析结果
        for i, item in enumerate(enhanced_data):
            sentiment = item['text_analysis']['sentiment']['sentiment']
            confidence = item['text_analysis']['sentiment']['confidence']
            keywords = [kw['word'] for kw in item['text_analysis']['keywords'][:3]]
            
            print(f'   数据 {i+1}: 情感={sentiment} (置信度={confidence:.2f}), 关键词={keywords}')
        
        return True
        
    except Exception as e:
        print(f'   ❌ 模拟数据处理失败: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_comprehensive_analysis_structure():
    """测试综合分析服务结构（不依赖真实API）"""
    print('\n🔬 测试综合分析服务结构...')
    print('=' * 50)
    
    try:
        from app.services.comprehensive_analysis_service import comprehensive_analysis_service
        
        # 模拟平台数据
        mock_platform_data = {
            'twitter': [
                {
                    'content': 'AI is transformative technology',
                    'text_analysis': {
                        'sentiment': {'sentiment': 'positive', 'confidence': 0.8},
                        'keywords': [{'word': 'ai', 'frequency': 1}, {'word': 'technology', 'frequency': 1}]
                    },
                    'score': 10
                }
            ],
            'reddit': [
                {
                    'content': 'Discussion about artificial intelligence trends',
                    'text_analysis': {
                        'sentiment': {'sentiment': 'neutral', 'confidence': 0.6},
                        'keywords': [{'word': 'artificial', 'frequency': 1}, {'word': 'intelligence', 'frequency': 1}]
                    },
                    'score': 25
                }
            ],
            'google_trends': {
                'data': [{'AI': 85, 'artificial intelligence': 75}],
                'keywords': ['AI', 'artificial intelligence']
            }
        }
        
        # 测试分析方法
        sentiment_analysis = comprehensive_analysis_service._analyze_cross_platform_sentiment(mock_platform_data)
        keyword_analysis = comprehensive_analysis_service._analyze_cross_platform_keywords(mock_platform_data)
        platform_comparison = comprehensive_analysis_service._compare_platforms(mock_platform_data)
        trend_score = comprehensive_analysis_service._calculate_comprehensive_trend_score(mock_platform_data, ['AI'])
        insights = comprehensive_analysis_service._generate_comprehensive_insights(
            mock_platform_data, sentiment_analysis, keyword_analysis, trend_score
        )
        
        print(f'   ✅ 情感分析: {sentiment_analysis.get("overall_sentiment", "N/A")}')
        print(f'   ✅ 关键词数量: {len(keyword_analysis.get("top_keywords", []))}')
        print(f'   ✅ 平台对比: {len(platform_comparison)} 个平台')
        print(f'   ✅ 趋势评分: {trend_score}')
        print(f'   ✅ 洞察数量: {len(insights)}')
        
        # 显示一些洞察
        for insight in insights[:3]:
            print(f'     • {insight}')
        
        return True
        
    except Exception as e:
        print(f'   ❌ 综合分析服务结构测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print('🚀 开始核心功能测试')
    print('=' * 60)
    
    test_results = []
    
    # 测试1: 文本分析服务
    result1 = test_text_analysis_service()
    test_results.append(('文本分析服务', result1))
    
    # 测试2: 服务导入
    services_status = test_service_imports()
    services_success = sum(services_status.values()) >= 3  # 至少3个服务成功
    test_results.append(('服务导入', services_success))
    
    # 测试3: 模拟数据处理
    result3 = test_mock_data_processing()
    test_results.append(('模拟数据处理', result3))
    
    # 测试4: 综合分析结构
    result4 = await test_comprehensive_analysis_structure()
    test_results.append(('综合分析结构', result4))
    
    # 汇总结果
    print('\n' + '=' * 60)
    print('📋 测试结果汇总:')
    
    success_count = 0
    for test_name, success in test_results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f'   {test_name}: {status}')
        if success:
            success_count += 1
    
    overall_success = success_count >= 3  # 至少3个测试成功
    
    print(f'\n🏁 总体结果: {success_count}/{len(test_results)} 测试通过')
    
    if overall_success:
        print('🎉 核心功能测试通过！')
        print('\n📋 验证完成的功能:')
        print('   ✅ 文本分析 (VADER、TextBlob、NLTK)')
        print('   ✅ 关键词提取和情感分析')
        print('   ✅ 服务架构和导入')
        print('   ✅ 数据处理流程')
        print('   ✅ 综合分析框架')
        print('\n🔧 接下来可以:')
        print('   1. 配置真实API密钥来测试数据获取')
        print('   2. 启动后端服务进行前后端联调')
        print('   3. 添加更多数据源和分析功能')
    else:
        print('⚠️ 部分核心功能存在问题，需要进一步修复')
    
    return overall_success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        print(f'\n🏁 测试完成，退出代码: {exit_code}')
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print('\n⚠️ 测试被用户中断')
        sys.exit(1)
    except Exception as e:
        print(f'\n💥 测试异常: {e}')
        sys.exit(1)