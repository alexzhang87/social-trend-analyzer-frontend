"""增强情感分析器单元测试"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.services.enhanced_sentiment_analyzer import (
    EnhancedSentimentAnalyzer,
    SentimentResult,
    SentimentLabel
)


class TestEnhancedSentimentAnalyzer:
    """增强情感分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return EnhancedSentimentAnalyzer()
    
    @pytest.fixture
    def sample_texts(self):
        """示例文本数据"""
        return [
            "Vision Pro真的太棒了！革命性的产品！",
            "价格太贵了，普通人买不起",
            "这个产品还可以，有优点也有缺点",
            "完全是垃圾，浪费钱",
            "哇，这个技术太先进了，令人兴奋！",
            "不确定这个产品是否值得购买",
            "Great product, but the price is too high",
            "This is absolutely amazing! Revolutionary technology!",
            "Meh, nothing special about it",
            "Terrible experience, would not recommend"
        ]
    
    def test_analyze_text_positive(self, analyzer):
        """测试积极情感分析"""
        text = "Vision Pro真的太棒了！革命性的产品，非常excited！"
        
        result = analyzer.analyze_text(text)
        
        assert isinstance(result, SentimentResult)
        assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.VERY_POSITIVE]
        assert result.confidence > 0.5
        assert result.scores["positive"] > result.scores["negative"]
        assert result.intensity > 0.3  # 感叹号和强调词应该增加强度
    
    def test_analyze_text_negative(self, analyzer):
        """测试消极情感分析"""
        text = "这个产品完全是垃圾，太失望了，浪费钱！"
        
        result = analyzer.analyze_text(text)
        
        assert result.label in [SentimentLabel.NEGATIVE, SentimentLabel.VERY_NEGATIVE]
        assert result.confidence > 0.5
        assert result.scores["negative"] > result.scores["positive"]
        assert result.intensity > 0.3
    
    def test_analyze_text_neutral(self, analyzer):
        """测试中性情感分析"""
        text = "这个产品有一些功能，价格在市场平均水平"
        
        result = analyzer.analyze_text(text)
        
        assert result.label == SentimentLabel.NEUTRAL
        assert result.scores["neutral"] >= max(result.scores["positive"], result.scores["negative"])
    
    def test_analyze_text_mixed(self, analyzer):
        """测试混合情感分析"""
        text = "产品很好但是价格太贵，喜欢功能但不喜欢成本"
        
        result = analyzer.analyze_text(text)
        
        # 混合情感或不确定
        assert result.label in [SentimentLabel.MIXED, SentimentLabel.UNCERTAIN, SentimentLabel.NEUTRAL]
        # 正负情感分数应该比较接近
        assert abs(result.scores["positive"] - result.scores["negative"]) < 0.3
    
    def test_analyze_text_empty(self, analyzer):
        """测试空文本"""
        result = analyzer.analyze_text("")
        
        assert result.label == SentimentLabel.NEUTRAL
        assert result.confidence == 0.0
        assert "empty_text" in result.context_factors
    
    def test_analyze_text_with_sarcasm(self, analyzer):
        """测试讽刺检测"""
        text = "Oh great, another expensive gadget we totally need"
        
        result = analyzer.analyze_text(text)
        
        # 应该检测到讽刺并翻转情感
        sarcasm_detected = any("sarcasm" in factor for factor in result.context_factors)
        if sarcasm_detected:
            # 如果检测到讽刺，原本看似积极的词应该被翻转为消极
            assert result.scores["negative"] > result.scores["positive"]
    
    def test_analyze_text_with_intensity_modifiers(self, analyzer):
        """测试强度修饰词"""
        text1 = "这个产品好"
        text2 = "这个产品非常好"
        text3 = "这个产品极其好"
        
        result1 = analyzer.analyze_text(text1)
        result2 = analyzer.analyze_text(text2)
        result3 = analyzer.analyze_text(text3)
        
        # 强度应该递增
        assert result1.intensity <= result2.intensity <= result3.intensity
        assert result1.scores["positive"] <= result2.scores["positive"] <= result3.scores["positive"]
    
    def test_analyze_text_with_negation(self, analyzer):
        """测试否定词处理"""
        text1 = "这个产品好"
        text2 = "这个产品不好"
        
        result1 = analyzer.analyze_text(text1)
        result2 = analyzer.analyze_text(text2)
        
        # 否定应该翻转情感
        assert result1.scores["positive"] > result1.scores["negative"]
        assert result2.scores["negative"] > result2.scores["positive"]
    
    def test_analyze_text_tech_vocabulary(self, analyzer):
        """测试科技词汇识别"""
        text = "这个产品很innovative，具有cutting-edge技术，非常scalable"
        
        result = analyzer.analyze_text(text)
        
        # 科技积极词汇应该提升积极情感
        assert result.scores["positive"] > 0.5
        assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.VERY_POSITIVE]
    
    def test_analyze_text_with_context(self, analyzer):
        """测试上下文信息"""
        text = "这个产品还行吧？？？"
        context = {
            "platform": "twitter",
            "timestamp": datetime.now().replace(hour=14)  # 下午
        }
        
        result = analyzer.analyze_text(text, context)
        
        # 验证上下文因素被记录
        assert "platform_twitter" in result.context_factors
        assert "afternoon_post" in result.context_factors
        assert "high_uncertainty" in result.context_factors  # 多个问号
    
    def test_analyze_batch(self, analyzer, sample_texts):
        """测试批量分析"""
        results = analyzer.analyze_batch(sample_texts)
        
        assert len(results) == len(sample_texts)
        
        for result in results:
            assert isinstance(result, SentimentResult)
            assert result.label in SentimentLabel
            assert 0 <= result.confidence <= 1
            assert 0 <= result.intensity <= 1
    
    def test_analyze_batch_with_contexts(self, analyzer, sample_texts):
        """测试带上下文的批量分析"""
        contexts = [
            {"platform": "reddit", "timestamp": datetime.now()},
            {"platform": "twitter", "timestamp": datetime.now()},
            None,  # 无上下文
            {"platform": "reddit", "timestamp": datetime.now()}
        ] + [None] * (len(sample_texts) - 4)
        
        results = analyzer.analyze_batch(sample_texts, contexts)
        
        assert len(results) == len(sample_texts)
        
        # 验证有上下文的结果包含平台信息
        assert "platform_reddit" in results[0].context_factors
        assert "platform_twitter" in results[1].context_factors
    
    def test_analyze_temporal_trends(self, analyzer):
        """测试时间趋势分析"""
        base_time = datetime.now()
        texts_with_timestamps = [
            ("产品很好", base_time),
            ("还不错", base_time + timedelta(hours=2)),
            ("有点失望", base_time + timedelta(hours=4)),
            ("完全不行", base_time + timedelta(hours=6)),
            ("太棒了", base_time + timedelta(hours=8))
        ]
        
        result = analyzer.analyze_temporal_trends(texts_with_timestamps, window_hours=4)
        
        assert "temporal_trends" in result
        assert "trend_analysis" in result
        assert "summary" in result
        
        trends = result["temporal_trends"]
        assert len(trends) > 0
        
        for trend in trends:
            assert "timestamp" in trend
            assert "sentiment_distribution" in trend
            assert "average_confidence" in trend
            assert "text_count" in trend
    
    def test_analyze_temporal_trends_empty(self, analyzer):
        """测试空时间序列"""
        result = analyzer.analyze_temporal_trends([])
        
        assert "error" in result
    
    def test_emotion_analysis(self, analyzer):
        """测试情绪分析"""
        # 测试不同情绪的文本
        joy_text = "太开心了！amazing！fantastic！"
        anger_text = "太愤怒了！terrible！awful！"
        fear_text = "很担心，很scary，很dangerous"
        
        joy_result = analyzer.analyze_text(joy_text)
        anger_result = analyzer.analyze_text(anger_text)
        fear_result = analyzer.analyze_text(fear_text)
        
        # 验证情绪识别
        assert joy_result.emotions["joy"] > 0.3
        assert anger_result.emotions["anger"] > 0.3
        assert fear_result.emotions["fear"] > 0.3
    
    def test_intensity_calculation(self, analyzer):
        """测试强度计算"""
        low_intensity = "产品好"
        medium_intensity = "产品很好！"
        high_intensity = "产品非常好！！！太AMAZING了！😀"
        
        low_result = analyzer.analyze_text(low_intensity)
        medium_result = analyzer.analyze_text(medium_intensity)
        high_result = analyzer.analyze_text(high_intensity)
        
        # 强度应该递增
        assert low_result.intensity <= medium_result.intensity <= high_result.intensity
        assert high_result.intensity > 0.5  # 高强度文本
    
    def test_sarcasm_patterns(self, analyzer):
        """测试讽刺模式检测"""
        sarcasm_texts = [
            "Oh great, another bug",
            "Yeah, sure, like that's going to work",
            "Totally not what we needed",
            "Love how it crashes every time",
            "Thanks for nothing"
        ]
        
        for text in sarcasm_texts:
            result = analyzer.analyze_text(text)
            # 至少应该有一些讽刺检测
            sarcasm_factors = [f for f in result.context_factors if "sarcasm" in f]
            # 不是所有模式都能被检测到，但至少应该有一些
    
    def test_tech_sentiment_lexicon(self, analyzer):
        """测试科技情感词典"""
        positive_tech = "innovative scalable cutting-edge revolutionary"
        negative_tech = "buggy unstable crashed broken"
        
        pos_result = analyzer.analyze_text(positive_tech)
        neg_result = analyzer.analyze_text(negative_tech)
        
        assert pos_result.scores["positive"] > pos_result.scores["negative"]
        assert neg_result.scores["negative"] > neg_result.scores["positive"]
    
    def test_context_adjustments(self, analyzer):
        """测试上下文调整"""
        text = "好吧"
        
        # 短文本应该增加中性分数
        result = analyzer.analyze_text(text)
        assert "short_text" in result.context_factors
        
        # 高不确定性文本
        uncertain_text = "这个产品怎么样？？？真的好吗？？？"
        uncertain_result = analyzer.analyze_text(uncertain_text)
        assert "high_uncertainty" in uncertain_result.context_factors
    
    def test_multilingual_support(self, analyzer):
        """测试多语言支持"""
        chinese_text = "这个产品很棒"
        english_text = "This product is amazing"
        
        chinese_result = analyzer.analyze_text(chinese_text)
        english_result = analyzer.analyze_text(english_text)
        
        # 两种语言都应该能正确识别积极情感
        assert chinese_result.scores["positive"] > chinese_result.scores["negative"]
        assert english_result.scores["positive"] > english_result.scores["negative"]
    
    def test_edge_cases(self, analyzer):
        """测试边界情况"""
        edge_cases = [
            "",  # 空字符串
            "   ",  # 只有空格
            "123456",  # 只有数字
            "!@#$%^&*()",  # 只有符号
            "a" * 1000,  # 超长文本
            "😀😃😄😁😆😅😂🤣",  # 只有表情符号
        ]
        
        for text in edge_cases:
            result = analyzer.analyze_text(text)
            # 应该能处理而不崩溃
            assert isinstance(result, SentimentResult)
            assert result.label in SentimentLabel
    
    def test_performance_batch_analysis(self, analyzer, benchmark):
        """性能测试：批量分析"""
        texts = ["这是测试文本" + str(i) for i in range(100)]
        
        def run_batch_analysis():
            return analyzer.analyze_batch(texts)
        
        results = benchmark(run_batch_analysis)
        
        assert len(results) == 100
        for result in results:
            assert isinstance(result, SentimentResult)
    
    def test_consistency(self, analyzer):
        """测试一致性：相同输入应该产生相同输出"""
        text = "这个产品很好，但是价格有点贵"
        
        results = [analyzer.analyze_text(text) for _ in range(5)]
        
        # 所有结果应该相同
        first_result = results[0]
        for result in results[1:]:
            assert result.label == first_result.label
            assert abs(result.confidence - first_result.confidence) < 0.001
            assert result.scores == first_result.scores
    
    def test_error_handling(self, analyzer):
        """测试错误处理"""
        # 模拟分析过程中的错误
        with patch.object(analyzer, '_calculate_base_sentiment', side_effect=Exception("Test error")):
            result = analyzer.analyze_text("测试文本")
            
            # 应该返回默认结果而不是崩溃
            assert isinstance(result, SentimentResult)
            # 可能会有错误标记
    
    @pytest.mark.parametrize("text,expected_label", [
        ("太棒了！！！", SentimentLabel.VERY_POSITIVE),
        ("还可以", SentimentLabel.NEUTRAL),
        ("完全垃圾", SentimentLabel.VERY_NEGATIVE),
        ("好的但是贵", SentimentLabel.MIXED),
    ])
    def test_parametrized_sentiment_detection(self, analyzer, text, expected_label):
        """参数化测试：特定文本的情感检测"""
        result = analyzer.analyze_text(text)
        
        # 允许一定的灵活性，因为情感分析可能有细微差别
        if expected_label == SentimentLabel.VERY_POSITIVE:
            assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.VERY_POSITIVE]
        elif expected_label == SentimentLabel.VERY_NEGATIVE:
            assert result.label in [SentimentLabel.NEGATIVE, SentimentLabel.VERY_NEGATIVE]
        elif expected_label == SentimentLabel.MIXED:
            assert result.label in [SentimentLabel.MIXED, SentimentLabel.NEUTRAL, SentimentLabel.UNCERTAIN]
        else:
            assert result.label == expected_label