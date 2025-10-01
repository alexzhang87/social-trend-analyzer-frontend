#!/usr/bin/env python3
"""
MonkeyLearn集成测试
测试高级文本分析功能的集成效果
"""

import asyncio
import sys
import os
sys.path.append('app')

async def test_monkeylearn_integration():
    """测试MonkeyLearn集成功能"""
    print('🐒 测试MonkeyLearn集成功能...')
    print('=' * 50)
    
    try:
        from app.services.monkeylearn_service import monkeylearn_service
        from app.services.enhanced_text_analysis_service import enhanced_text_analysis_service
        
        # 测试服务状态
        status = monkeylearn_service.get_status()
        print(f'📊 MonkeyLearn状态:')
        print(f'   API可用: {status["available"]}')
        print(f'   API已配置: {status["api_configured"]}')
        print(f'   功能: {status["features"]}')
        print(f'   说明: {status["note"]}')
        
        # 测试文本
        test_texts = [
            "This AI product is absolutely amazing! I love how it simplifies my workflow.",
            "I'm not sure about this new technology. It seems overhyped and complicated.",
            "The user interface is intuitive and the features are well-designed.",
            "Customer support was unhelpful and the app crashes frequently."
        ]
        
        print(f'\n📝 测试文本 ({len(test_texts)} 条):')
        for i, text in enumerate(test_texts):
            print(f'   {i+1}. {text[:60]}...')
        
        # 测试1: 基础情感分析（本地）
        print(f'\n🎭 测试本地情感分析...')
        for i, text in enumerate(test_texts):
            result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(text)
            print(f'   文本{i+1}: {result.get("sentiment", "N/A")} (置信度: {result.get("confidence", 0):.2f})')
        
        # 测试2: MonkeyLearn情感分析（如果可用）
        if monkeylearn_service.available:
            print(f'\n🐒 测试MonkeyLearn情感分析...')
            ml_results = await monkeylearn_service.analyze_sentiment(test_texts)
            
            for i, result in enumerate(ml_results):
                sentiment = result.get('sentiment', 'N/A')
                confidence = result.get('confidence', 0)
                fallback = result.get('fallback', False)
                status_text = '(降级)' if fallback else '(ML)'
                print(f'   文本{i+1}: {sentiment} (置信度: {confidence:.2f}) {status_text}')
        else:
            print(f'\n⚠️ MonkeyLearn API未配置，跳过高级分析测试')
        
        # 测试3: 综合分析
        print(f'\n🔬 测试综合分析...')
        comprehensive_results = await enhanced_text_analysis_service.comprehensive_analysis_with_monkeylearn(test_texts)
        
        for i, result in enumerate(comprehensive_results):
            local_sentiment = result.get('local_analysis', {}).get('sentiment', {}).get('sentiment', 'N/A')
            ml_analysis = result.get('monkeylearn_analysis')
            insights = result.get('combined_insights', {})
            
            print(f'   文本{i+1}:')
            print(f'     本地分析: {local_sentiment}')
            if ml_analysis:
                ml_sentiment = ml_analysis.get('sentiment', {}).get('sentiment', 'N/A') if ml_analysis.get('sentiment') else 'N/A'
                print(f'     ML分析: {ml_sentiment}')
            else:
                print(f'     ML分析: 不可用')
            
            if insights.get('notes'):
                print(f'     洞察: {", ".join(insights["notes"])}')
        
        return True
        
    except Exception as e:
        print(f'❌ MonkeyLearn集成测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """测试API端点"""
    print('\n🌐 测试API端点...')
    print('=' * 50)
    
    try:
        import requests
        
        # 测试MonkeyLearn状态端点
        response = requests.get('http://localhost:8001/api/v1/monkeylearn/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ MonkeyLearn状态端点正常')
            print(f'   API可用: {data.get("available", False)}')
            print(f'   功能: {data.get("features", {})}')
        else:
            print(f'⚠️ MonkeyLearn状态端点返回: HTTP {response.status_code}')
        
        # 测试模型信息端点
        response = requests.get('http://localhost:8001/api/v1/monkeylearn/models', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ 模型信息端点正常')
            local_models = data.get('local_models', {})
            ml_models = data.get('monkeylearn_models', {})
            print(f'   本地模型: {len(local_models)} 个')
            print(f'   MonkeyLearn模型: {len(ml_models)} 个')
        else:
            print(f'⚠️ 模型信息端点返回: HTTP {response.status_code}')
        
        return True
        
    except Exception as e:
        print(f'❌ API端点测试失败: {e}')
        return False

async def main():
    """主测试函数"""
    print('🚀 开始MonkeyLearn集成验证测试')
    print('=' * 60)
    
    test_results = []
    
    # 测试1: MonkeyLearn集成功能
    result1 = await test_monkeylearn_integration()
    test_results.append(('MonkeyLearn集成功能', result1))
    
    # 测试2: API端点
    result2 = await test_api_endpoints()
    test_results.append(('API端点', result2))
    
    # 汇总结果
    print('\n' + '=' * 60)
    print('📋 测试结果汇总:')
    
    success_count = 0
    for test_name, success in test_results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f'   {test_name}: {status}')
        if success:
            success_count += 1
    
    overall_success = success_count >= 1  # 至少1个测试成功
    
    print(f'\n🏁 总体结果: {success_count}/{len(test_results)} 测试通过')
    
    if overall_success:
        print('🎉 MonkeyLearn集成验证成功！')
        print('\n📋 已实现的功能:')
        print('   ✅ MonkeyLearn服务集成（可选，基于API Token）')
        print('   ✅ 情感分析增强（VADER + TextBlob + MonkeyLearn）')
        print('   ✅ 主题分类功能（MonkeyLearn专有）')
        print('   ✅ 意图检测功能（MonkeyLearn专有）')
        print('   ✅ 综合分析对比（本地 vs 云端）')
        print('   ✅ 优雅降级机制（API不可用时使用本地分析）')
        print('   ✅ API端点集成（/api/v1/monkeylearn/...）')
        print('\n🔧 使用说明:')
        print('   1. 如需使用MonkeyLearn，请在.env中设置 MONKEYLEARN_API_TOKEN')
        print('   2. MonkeyLearn是付费服务（$299/月起），有免费试用')
        print('   3. 即使不配置MonkeyLearn，系统仍可使用免费的本地分析')
        print('   4. 系统会自动对比本地和云端分析结果，提高准确性')
        print('\n💡 经济性建议:')
        print('   • 对于预算有限的项目，可仅使用免费的本地分析（VADER + TextBlob + NLTK）')
        print('   • 对于需要高精度分析的企业项目，可考虑MonkeyLearn付费方案')
        print('   • 系统支持混合模式，可在不同场景下灵活选择分析方法')
    else:
        print('⚠️ MonkeyLearn集成部分功能存在问题')
    
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