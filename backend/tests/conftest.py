"""pytest配置文件 - 全局测试配置和fixtures"""

import asyncio
import os
import pytest
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "testing"
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6380/1"

# 导入应用
from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """测试设置"""
    return get_settings()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """异步HTTP客户端"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """临时目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_redis():
    """模拟Redis连接"""
    with patch('app.core.cache.redis_client') as mock:
        mock_instance = Mock()
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.delete.return_value = True
        mock_instance.exists.return_value = False
        mock_instance.expire.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm_service():
    """模拟LLM服务"""
    with patch('app.services.llm_service.ZhipuAIProvider') as mock:
        mock_instance = Mock()
        mock_instance.analyze_trends.return_value = {
            "summary": "测试分析结果",
            "sentiment": {"positive": 0.6, "negative": 0.2, "neutral": 0.2},
            "themes": ["创新", "技术", "市场"],
            "opportunities": ["市场机会1", "市场机会2"]
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_reddit_service():
    """模拟Reddit服务"""
    with patch('app.services.reddit_official_service.reddit_service') as mock:
        mock.search_posts.return_value = [
            {
                "id": "test1",
                "title": "测试帖子1",
                "content": "这是一个测试帖子内容",
                "score": 100,
                "num_comments": 50,
                "created_utc": 1640995200,
                "subreddit": "technology",
                "author": "test_user",
                "url": "https://reddit.com/test1"
            },
            {
                "id": "test2",
                "title": "测试帖子2",
                "content": "另一个测试帖子内容",
                "score": 75,
                "num_comments": 25,
                "created_utc": 1640995300,
                "subreddit": "technology",
                "author": "test_user2",
                "url": "https://reddit.com/test2"
            }
        ]
        yield mock


@pytest.fixture
def mock_twitter_service():
    """模拟Twitter服务"""
    with patch('app.services.twitter_service.TwitterService') as mock:
        mock_instance = Mock()
        mock_instance.search_tweets.return_value = [
            {
                "id": "tweet1",
                "text": "这是一条测试推文",
                "public_metrics": {
                    "retweet_count": 10,
                    "like_count": 50,
                    "reply_count": 5,
                    "quote_count": 2
                },
                "created_at": "2024-01-01T00:00:00Z",
                "author_id": "user1",
                "lang": "zh"
            },
            {
                "id": "tweet2",
                "text": "另一条测试推文",
                "public_metrics": {
                    "retweet_count": 5,
                    "like_count": 25,
                    "reply_count": 3,
                    "quote_count": 1
                },
                "created_at": "2024-01-01T01:00:00Z",
                "author_id": "user2",
                "lang": "zh"
            }
        ]
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_google_trends():
    """模拟Google Trends服务"""
    with patch('app.services.google_trends_service.GoogleTrendsService') as mock:
        mock_instance = Mock()
        mock_instance.get_trends.return_value = {
            "interest_over_time": [
                {"date": "2024-01-01", "value": 80},
                {"date": "2024-01-02", "value": 85},
                {"date": "2024-01-03", "value": 90}
            ],
            "related_queries": [
                {"query": "相关查询1", "value": 100},
                {"query": "相关查询2", "value": 80}
            ],
            "regional_interest": [
                {"region": "中国", "value": 100},
                {"region": "美国", "value": 80}
            ]
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_analysis_request():
    """示例分析请求数据"""
    return {
        "keywords": ["Vision Pro", "Apple"],
        "platforms": ["reddit", "twitter"],
        "timeframe": "7d",
        "language": "zh",
        "region": "CN"
    }


@pytest.fixture
def sample_posts_data():
    """示例帖子数据"""
    return [
        {
            "id": "post1",
            "platform": "reddit",
            "title": "Vision Pro体验分享",
            "content": "刚刚体验了Vision Pro，感觉非常震撼！",
            "score": 150,
            "comments_count": 30,
            "created_at": "2024-01-01T10:00:00Z",
            "author": "tech_enthusiast",
            "url": "https://reddit.com/r/technology/post1"
        },
        {
            "id": "post2",
            "platform": "twitter",
            "title": "",
            "content": "Vision Pro的价格太高了，普通消费者买不起",
            "score": 25,
            "comments_count": 8,
            "created_at": "2024-01-01T11:00:00Z",
            "author": "budget_user",
            "url": "https://twitter.com/budget_user/status/123"
        },
        {
            "id": "post3",
            "platform": "reddit",
            "title": "Vision Pro vs Meta Quest 3对比",
            "content": "从技术角度对比两款VR设备的优缺点",
            "score": 200,
            "comments_count": 45,
            "created_at": "2024-01-01T12:00:00Z",
            "author": "vr_expert",
            "url": "https://reddit.com/r/virtualreality/post3"
        }
    ]


@pytest.fixture
def sample_sentiment_results():
    """示例情感分析结果"""
    return {
        "overall_sentiment": {
            "positive": 0.45,
            "negative": 0.25,
            "neutral": 0.30
        },
        "sentiment_by_platform": {
            "reddit": {"positive": 0.50, "negative": 0.20, "neutral": 0.30},
            "twitter": {"positive": 0.40, "negative": 0.30, "neutral": 0.30}
        },
        "emotion_analysis": {
            "joy": 0.35,
            "trust": 0.25,
            "anticipation": 0.20,
            "anger": 0.10,
            "fear": 0.05,
            "sadness": 0.05
        },
        "confidence_score": 0.82
    }


# 测试数据库设置
@pytest.fixture(scope="function")
def db_session():
    """数据库会话（如果使用数据库）"""
    # 这里可以添加数据库测试设置
    # 例如创建测试数据库、事务回滚等
    pass


# 清理函数
@pytest.fixture(autouse=True)
def cleanup():
    """每个测试后的清理工作"""
    yield
    # 清理临时文件、重置状态等
    pass


# 性能测试标记
# pytest_plugins = ["pytest_benchmark"]  # 暂时禁用，需要安装插件


# 自定义断言
def assert_valid_analysis_result(result):
    """验证分析结果的有效性"""
    assert "status" in result
    assert "result" in result
    assert "message" in result
    
    analysis_result = result["result"]
    assert "hypeIndex" in analysis_result
    assert "sentimentSpectrum" in analysis_result
    assert "keyThemes" in analysis_result
    assert "actionableOpportunities" in analysis_result
    
    # 验证热度指数
    hype_index = analysis_result["hypeIndex"]
    assert "score" in hype_index
    assert 0 <= hype_index["score"] <= 100
    
    # 验证情感分布
    sentiment = analysis_result["sentimentSpectrum"]
    assert "positive" in sentiment
    assert "negative" in sentiment
    assert "neutral" in sentiment
    assert abs(sum(sentiment.values()) - 100) < 1  # 总和应该接近100%


def assert_valid_post_data(post):
    """验证帖子数据的有效性"""
    required_fields = ["id", "platform", "content", "created_at", "author"]
    for field in required_fields:
        assert field in post, f"Missing required field: {field}"
    
    assert post["platform"] in ["reddit", "twitter", "google_trends"]
    assert isinstance(post["score"], (int, float))
    assert isinstance(post["comments_count"], int)