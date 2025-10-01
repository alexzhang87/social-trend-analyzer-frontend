"""LLM服务单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from app.services.llm_service import (
    LLMProvider,
    ZhipuAIProvider,
    exponential_backoff_retry
)


class TestLLMProvider:
    """LLM提供者抽象基类测试"""
    
    def test_abstract_methods(self):
        """测试抽象方法"""
        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            LLMProvider()


class TestZhipuAIProvider:
    """智谱AI提供者测试类"""
    
    @pytest.fixture
    def mock_client(self):
        """模拟智谱AI客户端"""
        client = Mock()
        client.chat = Mock()
        client.chat.completions = Mock()
        return client
    
    @pytest.fixture
    def provider(self, mock_client):
        """创建提供者实例"""
        with patch('app.services.llm_service.ZhipuAI', return_value=mock_client):
            return ZhipuAIProvider(api_key="test_key")
    
    @pytest.fixture
    def sample_posts_data(self):
        """示例帖子数据"""
        return [
            {
                "id": "1",
                "content": "Vision Pro真的太棒了！革命性的产品！",
                "platform": "reddit",
                "score": 150,
                "comments_count": 25,
                "created_at": "2024-01-15T10:00:00Z",
                "author": "tech_enthusiast",
                "url": "https://reddit.com/r/technology/post1"
            },
            {
                "id": "2",
                "content": "价格太贵了，普通人买不起",
                "platform": "twitter",
                "score": 45,
                "comments_count": 8,
                "created_at": "2024-01-15T11:00:00Z",
                "author": "budget_user",
                "url": "https://twitter.com/user/status/123"
            },
            {
                "id": "3",
                "content": "这个产品还可以，有优点也有缺点",
                "platform": "reddit",
                "score": 80,
                "comments_count": 15,
                "created_at": "2024-01-15T12:00:00Z",
                "author": "balanced_reviewer",
                "url": "https://reddit.com/r/reviews/post3"
            }
        ]
    
    def test_initialization(self):
        """测试初始化"""
        with patch('app.services.llm_service.ZhipuAI') as mock_zhipu:
            provider = ZhipuAIProvider(api_key="test_key")
            
            mock_zhipu.assert_called_once_with(api_key="test_key")
            assert provider.model == "glm-4-flash"
            assert provider.timeout == 30
    
    def test_initialization_with_custom_params(self):
        """测试自定义参数初始化"""
        with patch('app.services.llm_service.ZhipuAI') as mock_zhipu:
            provider = ZhipuAIProvider(
                api_key="test_key",
                model="glm-4",
                timeout=60
            )
            
            assert provider.model == "glm-4"
            assert provider.timeout == 60
    
    @pytest.mark.asyncio
    async def test_analyze_posts_success(self, provider, mock_client, sample_posts_data):
        """测试成功分析帖子"""
        # 模拟成功的API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "sentiment_distribution": {
                "positive": 0.6,
                "negative": 0.2,
                "neutral": 0.2
            },
            "key_themes": [
                "革命性技术",
                "价格问题",
                "产品评价"
            ],
            "trending_topics": [
                "Vision Pro",
                "AR技术",
                "苹果产品"
            ],
            "business_opportunities": [
                "AR应用开发",
                "配件市场",
                "内容创作"
            ],
            "summary": "用户对Vision Pro的反应混合，技术创新受到赞赏但价格是主要关注点",
            "confidence_score": 0.85
        })
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = await provider.analyze_posts(sample_posts_data, "Vision Pro")
        
        # 验证API调用
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        
        assert call_args[1]["model"] == provider.model
        assert call_args[1]["timeout"] == provider.timeout
        assert len(call_args[1]["messages"]) == 2  # system + user message
        
        # 验证结果
        assert "sentiment_distribution" in result
        assert "key_themes" in result
        assert "trending_topics" in result
        assert "business_opportunities" in result
        assert "summary" in result
        assert "confidence_score" in result
        
        assert result["sentiment_distribution"]["positive"] == 0.6
        assert len(result["key_themes"]) == 3
        assert result["confidence_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_analyze_posts_api_error(self, provider, mock_client, sample_posts_data):
        """测试API错误处理"""
        # 模拟API错误
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = await provider.analyze_posts(sample_posts_data, "Vision Pro")
        
        # 应该返回降级响应
        assert "sentiment_distribution" in result
        assert "key_themes" in result
        assert "error" in result
        assert "fallback" in result
        assert result["fallback"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_posts_invalid_json_response(self, provider, mock_client, sample_posts_data):
        """测试无效JSON响应"""
        # 模拟无效JSON响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = await provider.analyze_posts(sample_posts_data, "Vision Pro")
        
        # 应该返回降级响应
        assert "fallback" in result
        assert result["fallback"] is True
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_analyze_posts_empty_data(self, provider):
        """测试空数据"""
        result = await provider.analyze_posts([], "Vision Pro")
        
        # 应该返回空结果的降级响应
        assert "sentiment_distribution" in result
        assert "fallback" in result
        assert result["fallback"] is True
        assert "no_data" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_posts_large_dataset(self, provider, mock_client):
        """测试大数据集处理"""
        # 创建大量帖子数据
        large_posts_data = [
            {
                "id": str(i),
                "content": f"测试帖子内容 {i}",
                "platform": "reddit",
                "score": i * 10,
                "comments_count": i,
                "created_at": "2024-01-15T10:00:00Z",
                "author": f"user_{i}",
                "url": f"https://reddit.com/post{i}"
            }
            for i in range(100)
        ]
        
        # 模拟成功响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "sentiment_distribution": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
            "key_themes": ["测试主题"],
            "trending_topics": ["测试话题"],
            "business_opportunities": ["测试机会"],
            "summary": "大数据集分析结果",
            "confidence_score": 0.75
        })
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = await provider.analyze_posts(large_posts_data, "测试关键词")
        
        # 验证能够处理大数据集
        assert "sentiment_distribution" in result
        assert "confidence_score" in result
        
        # 验证API调用中的数据被适当截断或采样
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]
        # 消息长度应该在合理范围内（不会过长导致API限制）
        assert len(user_message) < 50000  # 假设的合理长度限制
    
    def test_create_fallback_response_no_data(self, provider):
        """测试无数据的降级响应"""
        result = provider._create_fallback_response([], "Vision Pro")
        
        assert result["fallback"] is True
        assert "no_data" in result["error"]
        assert result["sentiment_distribution"]["neutral"] == 1.0
        assert len(result["key_themes"]) == 0
        assert len(result["trending_topics"]) == 1  # 只有关键词
    
    def test_create_fallback_response_with_data(self, provider, sample_posts_data):
        """测试有数据的降级响应"""
        result = provider._create_fallback_response(sample_posts_data, "Vision Pro")
        
        assert result["fallback"] is True
        assert "sentiment_distribution" in result
        assert "key_themes" in result
        assert "trending_topics" in result
        assert "business_opportunities" in result
        assert "summary" in result
        
        # 验证基础统计计算
        assert result["total_posts"] == len(sample_posts_data)
        assert result["total_engagement"] > 0
        assert result["average_score"] > 0
    
    def test_extract_keywords_chinese(self, provider):
        """测试中文关键词提取"""
        text = "Vision Pro是苹果公司推出的革命性AR设备，具有先进的显示技术"
        keywords = provider._extract_keywords(text)
        
        assert len(keywords) > 0
        # 应该包含一些重要词汇
        important_words = ["Vision", "Pro", "苹果", "革命性", "AR", "设备", "技术"]
        found_words = [word for word in important_words if any(word in kw for kw in keywords)]
        assert len(found_words) > 0
    
    def test_extract_keywords_english(self, provider):
        """测试英文关键词提取"""
        text = "The Vision Pro is an amazing revolutionary device with cutting-edge technology"
        keywords = provider._extract_keywords(text)
        
        assert len(keywords) > 0
        # 应该包含重要词汇
        important_words = ["Vision", "Pro", "amazing", "revolutionary", "device", "technology"]
        found_words = [word for word in important_words if any(word.lower() in kw.lower() for kw in keywords)]
        assert len(found_words) > 0
    
    def test_calculate_basic_sentiment(self, provider, sample_posts_data):
        """测试基础情感计算"""
        sentiment_dist = provider._calculate_basic_sentiment(sample_posts_data)
        
        assert "positive" in sentiment_dist
        assert "negative" in sentiment_dist
        assert "neutral" in sentiment_dist
        
        # 总和应该为1
        total = sum(sentiment_dist.values())
        assert abs(total - 1.0) < 0.01
        
        # 所有值应该在0-1之间
        for value in sentiment_dist.values():
            assert 0 <= value <= 1
    
    def test_calculate_hype_score(self, provider, sample_posts_data):
        """测试热度分数计算"""
        hype_score = provider._calculate_hype_score(sample_posts_data)
        
        assert isinstance(hype_score, (int, float))
        assert 0 <= hype_score <= 100
    
    def test_generate_basic_themes(self, provider, sample_posts_data):
        """测试基础主题生成"""
        themes = provider._generate_basic_themes(sample_posts_data)
        
        assert isinstance(themes, list)
        assert len(themes) > 0
        
        # 主题应该是字符串
        for theme in themes:
            assert isinstance(theme, str)
            assert len(theme) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_posts_with_retry(self, provider, mock_client, sample_posts_data):
        """测试重试机制"""
        # 模拟前两次失败，第三次成功
        mock_client.chat.completions.create.side_effect = [
            Exception("Temporary error"),
            Exception("Another error"),
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "sentiment_distribution": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
                "key_themes": ["主题"],
                "trending_topics": ["话题"],
                "business_opportunities": ["机会"],
                "summary": "重试成功",
                "confidence_score": 0.8
            })))
        ]
        
        # 使用重试装饰器
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        async def mock_analyze():
            return await provider.analyze_posts(sample_posts_data, "test")
        
        result = await mock_analyze()
        
        # 应该最终成功
        assert "sentiment_distribution" in result
        assert "fallback" not in result or not result["fallback"]
        assert mock_client.chat.completions.create.call_count == 3
    
    def test_prompt_construction(self, provider, sample_posts_data):
        """测试提示词构建"""
        # 通过分析调用来检查提示词
        with patch.object(provider.client.chat.completions, 'create') as mock_create:
            mock_create.return_value = Mock(
                choices=[Mock(message=Mock(content=json.dumps({
                    "sentiment_distribution": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
                    "key_themes": [],
                    "trending_topics": [],
                    "business_opportunities": [],
                    "summary": "",
                    "confidence_score": 0.5
                })))
            )
            
            # 同步调用以便检查参数
            import asyncio
            asyncio.run(provider.analyze_posts(sample_posts_data, "Vision Pro"))
            
            call_args = mock_create.call_args
            messages = call_args[1]["messages"]
            
            # 验证消息结构
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            
            # 验证系统消息包含关键指令
            system_content = messages[0]["content"]
            assert "情感分析" in system_content
            assert "JSON" in system_content
            
            # 验证用户消息包含数据
            user_content = messages[1]["content"]
            assert "Vision Pro" in user_content
            assert "帖子数据" in user_content or "posts" in user_content.lower()
    
    @pytest.mark.parametrize("posts_count", [1, 10, 50, 100])
    def test_different_data_sizes(self, provider, posts_count):
        """参数化测试：不同数据大小"""
        posts_data = [
            {
                "id": str(i),
                "content": f"测试内容 {i}",
                "platform": "reddit",
                "score": i,
                "comments_count": i,
                "created_at": "2024-01-15T10:00:00Z",
                "author": f"user_{i}",
                "url": f"https://example.com/{i}"
            }
            for i in range(posts_count)
        ]
        
        # 测试降级响应（不依赖API）
        result = provider._create_fallback_response(posts_data, "测试")
        
        assert "sentiment_distribution" in result
        assert result["total_posts"] == posts_count
        
        if posts_count > 0:
            assert len(result["key_themes"]) > 0
            assert result["total_engagement"] >= 0
        else:
            assert result["total_engagement"] == 0


class TestExponentialBackoffRetry:
    """指数退避重试装饰器测试"""
    
    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """测试第一次尝试成功"""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        async def mock_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await mock_function()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """测试失败后重试成功"""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Attempt {call_count} failed")
            return "success"
        
        result = await mock_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """测试超过最大重试次数"""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=2, base_delay=0.1)
        async def mock_function():
            nonlocal call_count
            call_count += 1
            raise Exception(f"Attempt {call_count} failed")
        
        with pytest.raises(Exception) as exc_info:
            await mock_function()
        
        assert "Attempt 2 failed" in str(exc_info.value)
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_with_different_exceptions(self):
        """测试不同类型的异常"""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        async def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Value error")
            elif call_count == 2:
                raise ConnectionError("Connection error")
            return "success"
        
        result = await mock_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_timing(self):
        """测试重试时间间隔"""
        import time
        
        call_times = []
        
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        async def mock_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Retry needed")
            return "success"
        
        start_time = time.time()
        result = await mock_function()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # 验证时间间隔递增（指数退避）
        if len(call_times) >= 2:
            interval1 = call_times[1] - call_times[0]
            assert interval1 >= 0.1  # 第一次重试延迟
        
        if len(call_times) >= 3:
            interval2 = call_times[2] - call_times[1]
            assert interval2 >= interval1  # 第二次重试延迟应该更长