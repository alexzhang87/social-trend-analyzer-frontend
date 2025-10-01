"""分析服务单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.analysis_service import AnalysisService
from app.services.enhanced_sentiment_analyzer import EnhancedSentimentAnalyzer, SentimentResult, SentimentLabel


class TestAnalysisService:
    """分析服务测试类"""
    
    @pytest.fixture
    def analysis_service(self):
        """创建分析服务实例"""
        return AnalysisService()
    
    @pytest.fixture
    def sample_posts(self, sample_posts_data):
        """示例帖子数据"""
        return sample_posts_data
    
    @pytest.mark.asyncio
    async def test_analyze_basic_success(self, analysis_service, sample_posts, 
                                       mock_reddit_service, mock_llm_service):
        """测试基础分析成功场景"""
        # 模拟数据收集
        mock_reddit_service.search_posts.return_value = sample_posts
        
        # 执行分析
        result = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证结果结构
        assert "hypeIndex" in result
        assert "sentimentSpectrum" in result
        assert "keyThemes" in result
        assert "top_mentions" in result
        
        # 验证热度指数
        hype_index = result["hypeIndex"]
        assert "score" in hype_index
        assert 0 <= hype_index["score"] <= 100
        assert "trend" in hype_index
        assert "factors" in hype_index
        
        # 验证情感分布
        sentiment = result["sentimentSpectrum"]
        assert "positive" in sentiment
        assert "negative" in sentiment
        assert "neutral" in sentiment
        assert abs(sum(sentiment.values()) - 100) < 1
    
    @pytest.mark.asyncio
    async def test_analyze_basic_no_data(self, analysis_service, mock_reddit_service):
        """测试无数据情况"""
        # 模拟无数据返回
        mock_reddit_service.search_posts.return_value = []
        
        result = await analysis_service.analyze_basic(
            keywords=["NonExistentKeyword"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证空结果处理
        assert result is not None
        assert "hypeIndex" in result
        assert result["hypeIndex"]["score"] == 0
        assert "message" in result
        assert "no data" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_standard_with_llm(self, analysis_service, sample_posts,
                                           mock_reddit_service, mock_llm_service):
        """测试标准分析（包含LLM）"""
        mock_reddit_service.search_posts.return_value = sample_posts
        
        result = await analysis_service.analyze_standard(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证LLM增强结果
        assert "aiInsights" in result
        assert "enhancedThemes" in result
        assert "marketOpportunities" in result
        
        # 验证LLM服务被调用
        mock_llm_service.analyze_trends.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_premium_full_features(self, analysis_service, sample_posts,
                                                mock_reddit_service, mock_twitter_service,
                                                mock_llm_service):
        """测试高级分析（完整功能）"""
        mock_reddit_service.search_posts.return_value = sample_posts
        mock_twitter_service.search_tweets.return_value = sample_posts
        
        result = await analysis_service.analyze_premium(
            keywords=["Vision Pro"],
            platforms=["reddit", "twitter"],
            timeframe="30d"
        )
        
        # 验证高级功能
        assert "competitorAnalysis" in result
        assert "marketSegmentation" in result
        assert "trendPrediction" in result
        assert "actionableOpportunities" in result
        assert "riskAssessment" in result
        
        # 验证数据量更大
        assert len(result.get("top_mentions", [])) > 0
    
    def test_calculate_hype_score(self, analysis_service, sample_posts):
        """测试热度分数计算"""
        score = analysis_service._calculate_basic_hype_score(sample_posts)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
    
    def test_calculate_hype_score_empty_posts(self, analysis_service):
        """测试空帖子列表的热度分数"""
        score = analysis_service._calculate_basic_hype_score([])
        
        assert score == 0
    
    def test_extract_keywords(self, analysis_service, sample_posts):
        """测试关键词提取"""
        keywords = analysis_service._extract_keywords(sample_posts)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # 验证关键词格式
        for keyword in keywords:
            assert isinstance(keyword, dict)
            assert "word" in keyword
            assert "frequency" in keyword
            assert "relevance" in keyword
    
    def test_analyze_sentiment_distribution(self, analysis_service, sample_posts):
        """测试情感分布分析"""
        sentiment_dist = analysis_service._analyze_sentiment_distribution(sample_posts)
        
        assert isinstance(sentiment_dist, dict)
        assert "positive" in sentiment_dist
        assert "negative" in sentiment_dist
        assert "neutral" in sentiment_dist
        
        # 验证百分比总和
        total = sum(sentiment_dist.values())
        assert abs(total - 100) < 1
    
    def test_get_platform_stats(self, analysis_service, sample_posts):
        """测试平台统计"""
        stats = analysis_service._get_platform_stats(sample_posts)
        
        assert isinstance(stats, dict)
        
        for platform, platform_stats in stats.items():
            assert "post_count" in platform_stats
            assert "avg_score" in platform_stats
            assert "total_engagement" in platform_stats
            assert platform_stats["post_count"] >= 0
    
    def test_identify_trending_topics(self, analysis_service, sample_posts):
        """测试趋势话题识别"""
        topics = analysis_service._identify_trending_topics(sample_posts)
        
        assert isinstance(topics, list)
        
        for topic in topics:
            assert isinstance(topic, dict)
            assert "topic" in topic
            assert "mentions" in topic
            assert "growth_rate" in topic
            assert "sentiment" in topic
    
    @pytest.mark.asyncio
    async def test_analyze_with_cache(self, analysis_service, sample_posts,
                                    mock_reddit_service, mock_redis):
        """测试缓存功能"""
        mock_reddit_service.search_posts.return_value = sample_posts
        
        # 第一次调用
        result1 = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 第二次调用（应该使用缓存）
        result2 = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证结果一致
        assert result1 == result2
        
        # 验证缓存操作
        assert mock_redis.get.called
        assert mock_redis.set.called
    
    @pytest.mark.asyncio
    async def test_analyze_with_error_handling(self, analysis_service, mock_reddit_service):
        """测试错误处理"""
        # 模拟服务错误
        mock_reddit_service.search_posts.side_effect = Exception("Service error")
        
        result = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证错误处理
        assert result is not None
        assert "error" in result
        assert "Service error" in str(result["error"])
    
    @pytest.mark.asyncio
    async def test_analyze_with_timeout(self, analysis_service, mock_reddit_service):
        """测试超时处理"""
        import asyncio
        
        # 模拟超时
        mock_reddit_service.search_posts.side_effect = asyncio.TimeoutError("Timeout")
        
        result = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证超时处理
        assert result is not None
        assert "timeout" in str(result.get("error", "")).lower()
    
    def test_merge_llm_and_stats(self, analysis_service):
        """测试LLM结果与统计数据合并"""
        llm_result = {
            "summary": "AI generated summary",
            "themes": ["innovation", "technology"],
            "opportunities": ["market opportunity 1"]
        }
        
        stats_result = {
            "hypeIndex": {"score": 75},
            "sentimentSpectrum": {"positive": 60, "negative": 20, "neutral": 20},
            "top_mentions": [{"id": "post1", "score": 100}]
        }
        
        merged = analysis_service._merge_llm_and_stats(llm_result, stats_result)
        
        # 验证合并结果
        assert "summary" in merged  # LLM内容
        assert "hypeIndex" in merged  # 统计内容
        assert "aiInsights" in merged  # 增强内容
        assert merged["hypeIndex"]["score"] == 75
    
    def test_get_enhanced_fallback_analysis(self, analysis_service, sample_posts):
        """测试增强备用分析"""
        result = analysis_service._get_enhanced_fallback_analysis(sample_posts)
        
        # 验证备用分析包含基本要素
        assert "hypeIndex" in result
        assert "sentimentSpectrum" in result
        assert "keyThemes" in result
        assert "summary" in result
        
        # 验证备用分析的质量
        assert len(result["keyThemes"]) > 0
        assert len(result["summary"]) > 0
    
    @pytest.mark.parametrize("timeframe,expected_days", [
        ("1d", 1),
        ("7d", 7),
        ("30d", 30),
        ("90d", 90)
    ])
    def test_parse_timeframe(self, analysis_service, timeframe, expected_days):
        """测试时间范围解析"""
        days = analysis_service._parse_timeframe(timeframe)
        assert days == expected_days
    
    def test_parse_invalid_timeframe(self, analysis_service):
        """测试无效时间范围"""
        with pytest.raises(ValueError):
            analysis_service._parse_timeframe("invalid")
    
    def test_filter_posts_by_quality(self, analysis_service, sample_posts):
        """测试帖子质量过滤"""
        filtered = analysis_service._filter_posts_by_quality(
            sample_posts, 
            min_score=50, 
            min_comments=10
        )
        
        assert len(filtered) <= len(sample_posts)
        
        for post in filtered:
            assert post["score"] >= 50
            assert post["comments_count"] >= 10
    
    def test_deduplicate_posts(self, analysis_service):
        """测试帖子去重"""
        duplicate_posts = [
            {"id": "1", "content": "test content", "platform": "reddit"},
            {"id": "2", "content": "test content", "platform": "twitter"},  # 相同内容
            {"id": "3", "content": "different content", "platform": "reddit"}
        ]
        
        deduplicated = analysis_service._deduplicate_posts(duplicate_posts)
        
        # 应该移除重复内容
        assert len(deduplicated) < len(duplicate_posts)
        
        # 验证内容唯一性
        contents = [post["content"] for post in deduplicated]
        assert len(contents) == len(set(contents))
    
    @pytest.mark.asyncio
    async def test_analyze_with_multiple_keywords(self, analysis_service, 
                                                 mock_reddit_service, sample_posts):
        """测试多关键词分析"""
        mock_reddit_service.search_posts.return_value = sample_posts
        
        result = await analysis_service.analyze_basic(
            keywords=["Vision Pro", "Apple", "VR"],
            platforms=["reddit"],
            timeframe="7d"
        )
        
        # 验证多关键词处理
        assert "keywordAnalysis" in result
        keyword_analysis = result["keywordAnalysis"]
        
        for keyword in ["Vision Pro", "Apple", "VR"]:
            assert keyword in keyword_analysis
            assert "mentions" in keyword_analysis[keyword]
            assert "sentiment" in keyword_analysis[keyword]
    
    @pytest.mark.asyncio
    async def test_analyze_with_language_filter(self, analysis_service,
                                               mock_reddit_service, sample_posts):
        """测试语言过滤"""
        mock_reddit_service.search_posts.return_value = sample_posts
        
        result = await analysis_service.analyze_basic(
            keywords=["Vision Pro"],
            platforms=["reddit"],
            timeframe="7d",
            language="zh"
        )
        
        # 验证语言过滤生效
        assert result is not None
        # 具体验证逻辑取决于实现
    
    @pytest.mark.performance
    def test_analyze_performance(self, analysis_service, sample_posts, benchmark):
        """性能测试"""
        def run_analysis():
            return analysis_service._calculate_basic_hype_score(sample_posts)
        
        # 基准测试
        result = benchmark(run_analysis)
        
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, analysis_service):
        """集成测试：完整分析流程"""
        # 这个测试需要真实的服务连接
        # 在CI/CD中可能需要跳过
        pytest.skip("Integration test requires real services")
        
        result = await analysis_service.analyze_basic(
            keywords=["test"],
            platforms=["reddit"],
            timeframe="1d"
        )
        
        assert result is not None
        assert "hypeIndex" in result