"""数据服务单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService
from app.services.google_trends_service import GoogleTrendsService


class TestRedditService:
    """Reddit服务测试类"""
    
    @pytest.fixture
    def mock_reddit_client(self):
        """模拟Reddit客户端"""
        client = Mock()
        client.subreddit = Mock()
        return client
    
    @pytest.fixture
    def reddit_service(self, mock_reddit_client):
        """创建Reddit服务实例"""
        with patch('app.services.reddit_service.praw.Reddit', return_value=mock_reddit_client):
            return RedditService(
                client_id="test_id",
                client_secret="test_secret",
                user_agent="test_agent"
            )
    
    @pytest.fixture
    def sample_reddit_posts(self):
        """示例Reddit帖子数据"""
        posts = []
        for i in range(5):
            post = Mock()
            post.id = f"post_{i}"
            post.title = f"Test Post {i} about Vision Pro"
            post.selftext = f"This is the content of post {i}"
            post.score = 100 + i * 10
            post.num_comments = 20 + i * 5
            post.created_utc = datetime.now().timestamp() - i * 3600
            post.author = Mock()
            post.author.name = f"user_{i}"
            post.subreddit = Mock()
            post.subreddit.display_name = "technology"
            post.url = f"https://reddit.com/r/technology/post_{i}"
            post.permalink = f"/r/technology/comments/post_{i}"
            posts.append(post)
        return posts
    
    def test_initialization(self):
        """测试初始化"""
        with patch('app.services.reddit_service.praw.Reddit') as mock_reddit:
            service = RedditService(
                client_id="test_id",
                client_secret="test_secret",
                user_agent="test_agent"
            )
            
            mock_reddit.assert_called_once_with(
                client_id="test_id",
                client_secret="test_secret",
                user_agent="test_agent"
            )
    
    @pytest.mark.asyncio
    async def test_search_posts_success(self, reddit_service, mock_reddit_client, sample_reddit_posts):
        """测试成功搜索帖子"""
        # 模拟搜索结果
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = sample_reddit_posts
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        results = await reddit_service.search_posts(
            keyword="Vision Pro",
            subreddits=["technology", "apple"],
            time_filter="week",
            limit=10
        )
        
        # 验证搜索调用
        mock_reddit_client.subreddit.assert_called()
        mock_subreddit.search.assert_called()
        
        # 验证结果格式
        assert len(results) == len(sample_reddit_posts)
        
        for result in results:
            assert "id" in result
            assert "content" in result
            assert "platform" in result
            assert "score" in result
            assert "comments_count" in result
            assert "created_at" in result
            assert "author" in result
            assert "url" in result
            assert result["platform"] == "reddit"
    
    @pytest.mark.asyncio
    async def test_search_posts_with_time_range(self, reddit_service, mock_reddit_client, sample_reddit_posts):
        """测试时间范围搜索"""
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = sample_reddit_posts
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        results = await reddit_service.search_posts(
            keyword="Vision Pro",
            start_date=start_date,
            end_date=end_date
        )
        
        # 验证时间过滤
        for result in results:
            post_date = datetime.fromisoformat(result["created_at"].replace('Z', '+00:00'))
            assert start_date <= post_date <= end_date
    
    @pytest.mark.asyncio
    async def test_search_posts_api_error(self, reddit_service, mock_reddit_client):
        """测试API错误处理"""
        # 模拟API错误
        mock_reddit_client.subreddit.side_effect = Exception("Reddit API Error")
        
        results = await reddit_service.search_posts(keyword="Vision Pro")
        
        # 应该返回空列表而不是崩溃
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_posts_empty_results(self, reddit_service, mock_reddit_client):
        """测试空结果"""
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = []
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        results = await reddit_service.search_posts(keyword="NonexistentKeyword")
        
        assert results == []
    
    def test_format_post(self, reddit_service, sample_reddit_posts):
        """测试帖子格式化"""
        post = sample_reddit_posts[0]
        formatted = reddit_service._format_post(post)
        
        assert formatted["id"] == post.id
        assert formatted["platform"] == "reddit"
        assert formatted["score"] == post.score
        assert formatted["comments_count"] == post.num_comments
        assert formatted["author"] == post.author.name
        assert "reddit.com" in formatted["url"]
    
    def test_format_post_with_missing_fields(self, reddit_service):
        """测试缺少字段的帖子格式化"""
        post = Mock()
        post.id = "test_id"
        post.title = "Test Title"
        post.selftext = "Test Content"
        post.score = 100
        post.num_comments = 10
        post.created_utc = datetime.now().timestamp()
        post.author = None  # 缺少作者
        post.subreddit = Mock()
        post.subreddit.display_name = "test"
        post.url = "https://reddit.com/test"
        post.permalink = "/r/test/comments/test"
        
        formatted = reddit_service._format_post(post)
        
        assert formatted["author"] == "[deleted]"
        assert formatted["platform"] == "reddit"
    
    @pytest.mark.asyncio
    async def test_get_trending_posts(self, reddit_service, mock_reddit_client, sample_reddit_posts):
        """测试获取热门帖子"""
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = sample_reddit_posts
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        results = await reddit_service.get_trending_posts(
            subreddits=["technology"],
            limit=5
        )
        
        assert len(results) <= 5
        mock_subreddit.hot.assert_called_with(limit=5)
    
    @pytest.mark.asyncio
    async def test_get_post_comments(self, reddit_service, mock_reddit_client):
        """测试获取帖子评论"""
        # 模拟评论数据
        comments = []
        for i in range(3):
            comment = Mock()
            comment.id = f"comment_{i}"
            comment.body = f"This is comment {i}"
            comment.score = 10 + i
            comment.created_utc = datetime.now().timestamp()
            comment.author = Mock()
            comment.author.name = f"commenter_{i}"
            comments.append(comment)
        
        mock_submission = Mock()
        mock_submission.comments.list.return_value = comments
        mock_reddit_client.submission.return_value = mock_submission
        
        results = await reddit_service.get_post_comments("test_post_id", limit=10)
        
        assert len(results) == 3
        mock_reddit_client.submission.assert_called_with("test_post_id")
        
        for result in results:
            assert "id" in result
            assert "content" in result
            assert "score" in result
            assert "author" in result
            assert "created_at" in result


class TestTwitterService:
    """Twitter服务测试类"""
    
    @pytest.fixture
    def mock_twitter_client(self):
        """模拟Twitter客户端"""
        client = Mock()
        return client
    
    @pytest.fixture
    def twitter_service(self, mock_twitter_client):
        """创建Twitter服务实例"""
        with patch('app.services.twitter_service.tweepy.Client', return_value=mock_twitter_client):
            return TwitterService(
                bearer_token="test_token",
                api_key="test_key",
                api_secret="test_secret"
            )
    
    @pytest.fixture
    def sample_tweets(self):
        """示例推文数据"""
        tweets = []
        for i in range(5):
            tweet = Mock()
            tweet.id = f"tweet_{i}"
            tweet.text = f"This is tweet {i} about Vision Pro"
            tweet.public_metrics = {
                "retweet_count": 10 + i,
                "like_count": 50 + i * 10,
                "reply_count": 5 + i,
                "quote_count": 2 + i
            }
            tweet.created_at = datetime.now() - timedelta(hours=i)
            tweet.author_id = f"user_{i}"
            tweets.append(tweet)
        return tweets
    
    def test_initialization(self):
        """测试初始化"""
        with patch('app.services.twitter_service.tweepy.Client') as mock_client:
            service = TwitterService(
                bearer_token="test_token",
                api_key="test_key",
                api_secret="test_secret"
            )
            
            mock_client.assert_called_once_with(
                bearer_token="test_token",
                consumer_key="test_key",
                consumer_secret="test_secret",
                wait_on_rate_limit=True
            )
    
    @pytest.mark.asyncio
    async def test_search_tweets_success(self, twitter_service, mock_twitter_client, sample_tweets):
        """测试成功搜索推文"""
        # 模拟搜索结果
        mock_response = Mock()
        mock_response.data = sample_tweets
        mock_response.includes = {"users": []}
        mock_twitter_client.search_recent_tweets.return_value = mock_response
        
        results = await twitter_service.search_tweets(
            keyword="Vision Pro",
            max_results=10
        )
        
        # 验证搜索调用
        mock_twitter_client.search_recent_tweets.assert_called_once()
        call_args = mock_twitter_client.search_recent_tweets.call_args
        assert "Vision Pro" in call_args[1]["query"]
        assert call_args[1]["max_results"] == 10
        
        # 验证结果格式
        assert len(results) == len(sample_tweets)
        
        for result in results:
            assert "id" in result
            assert "content" in result
            assert "platform" in result
            assert "score" in result
            assert "comments_count" in result
            assert "created_at" in result
            assert "author" in result
            assert "url" in result
            assert result["platform"] == "twitter"
    
    @pytest.mark.asyncio
    async def test_search_tweets_with_filters(self, twitter_service, mock_twitter_client, sample_tweets):
        """测试带过滤条件的搜索"""
        mock_response = Mock()
        mock_response.data = sample_tweets
        mock_response.includes = {"users": []}
        mock_twitter_client.search_recent_tweets.return_value = mock_response
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        results = await twitter_service.search_tweets(
            keyword="Vision Pro",
            start_time=start_date,
            end_time=end_date,
            lang="en"
        )
        
        # 验证过滤参数
        call_args = mock_twitter_client.search_recent_tweets.call_args
        assert call_args[1]["start_time"] == start_date
        assert call_args[1]["end_time"] == end_date
        assert "lang:en" in call_args[1]["query"]
    
    @pytest.mark.asyncio
    async def test_search_tweets_api_error(self, twitter_service, mock_twitter_client):
        """测试API错误处理"""
        # 模拟API错误
        mock_twitter_client.search_recent_tweets.side_effect = Exception("Twitter API Error")
        
        results = await twitter_service.search_tweets(keyword="Vision Pro")
        
        # 应该返回空列表而不是崩溃
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_tweets_no_results(self, twitter_service, mock_twitter_client):
        """测试无结果"""
        mock_response = Mock()
        mock_response.data = None
        mock_twitter_client.search_recent_tweets.return_value = mock_response
        
        results = await twitter_service.search_tweets(keyword="NonexistentKeyword")
        
        assert results == []
    
    def test_format_tweet(self, twitter_service, sample_tweets):
        """测试推文格式化"""
        tweet = sample_tweets[0]
        users_map = {"user_0": {"username": "testuser", "name": "Test User"}}
        
        formatted = twitter_service._format_tweet(tweet, users_map)
        
        assert formatted["id"] == tweet.id
        assert formatted["platform"] == "twitter"
        assert formatted["content"] == tweet.text
        assert formatted["score"] == tweet.public_metrics["like_count"]
        assert formatted["comments_count"] == tweet.public_metrics["reply_count"]
        assert "twitter.com" in formatted["url"]
    
    def test_calculate_engagement_score(self, twitter_service, sample_tweets):
        """测试参与度分数计算"""
        tweet = sample_tweets[0]
        score = twitter_service._calculate_engagement_score(tweet.public_metrics)
        
        assert isinstance(score, (int, float))
        assert score > 0
        
        # 验证计算逻辑
        expected = (
            tweet.public_metrics["like_count"] +
            tweet.public_metrics["retweet_count"] * 2 +
            tweet.public_metrics["reply_count"] * 3 +
            tweet.public_metrics["quote_count"] * 2
        )
        assert score == expected
    
    @pytest.mark.asyncio
    async def test_get_trending_hashtags(self, twitter_service, mock_twitter_client):
        """测试获取热门话题标签"""
        # 模拟热门话题数据
        mock_trends = [
            {"name": "#VisionPro", "tweet_volume": 10000},
            {"name": "#Apple", "tweet_volume": 5000},
            {"name": "#AR", "tweet_volume": 3000}
        ]
        
        mock_twitter_client.get_place_trends.return_value = [{"trends": mock_trends}]
        
        results = await twitter_service.get_trending_hashtags(woeid=1)  # 全球
        
        assert len(results) == 3
        assert results[0]["name"] == "#VisionPro"
        assert results[0]["volume"] == 10000


class TestGoogleTrendsService:
    """Google Trends服务测试类"""
    
    @pytest.fixture
    def trends_service(self):
        """创建Google Trends服务实例"""
        return GoogleTrendsService()
    
    @pytest.fixture
    def mock_pytrends(self):
        """模拟pytrends客户端"""
        with patch('app.services.google_trends_service.TrendReq') as mock_trends:
            mock_instance = Mock()
            mock_trends.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.asyncio
    async def test_get_interest_over_time(self, trends_service, mock_pytrends):
        """测试获取时间趋势数据"""
        # 模拟趋势数据
        mock_data = {
            "Vision Pro": [10, 20, 30, 40, 50],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
        }
        mock_pytrends.interest_over_time.return_value = mock_data
        
        results = await trends_service.get_interest_over_time(
            keywords=["Vision Pro"],
            timeframe="today 5-y"
        )
        
        # 验证调用
        mock_pytrends.build_payload.assert_called_once_with(
            ["Vision Pro"],
            timeframe="today 5-y",
            geo=""
        )
        mock_pytrends.interest_over_time.assert_called_once()
        
        # 验证结果
        assert "Vision Pro" in results
        assert "date" in results
    
    @pytest.mark.asyncio
    async def test_get_related_queries(self, trends_service, mock_pytrends):
        """测试获取相关查询"""
        # 模拟相关查询数据
        mock_data = {
            "Vision Pro": {
                "top": {
                    "query": ["apple vision pro", "vision pro price", "vision pro review"],
                    "value": [100, 80, 60]
                },
                "rising": {
                    "query": ["vision pro apps", "vision pro games"],
                    "value": ["Breakout", "+150%"]
                }
            }
        }
        mock_pytrends.related_queries.return_value = mock_data
        
        results = await trends_service.get_related_queries(keyword="Vision Pro")
        
        # 验证调用
        mock_pytrends.build_payload.assert_called_once_with(["Vision Pro"])
        mock_pytrends.related_queries.assert_called_once()
        
        # 验证结果
        assert "top" in results
        assert "rising" in results
        assert len(results["top"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_regional_interest(self, trends_service, mock_pytrends):
        """测试获取地区兴趣数据"""
        # 模拟地区数据
        mock_data = {
            "geoName": ["United States", "China", "Japan"],
            "Vision Pro": [100, 80, 60]
        }
        mock_pytrends.interest_by_region.return_value = mock_data
        
        results = await trends_service.get_regional_interest(
            keyword="Vision Pro",
            resolution="COUNTRY"
        )
        
        # 验证调用
        mock_pytrends.build_payload.assert_called_once_with(["Vision Pro"])
        mock_pytrends.interest_by_region.assert_called_once_with(
            resolution="COUNTRY",
            inc_low_vol=True,
            inc_geo_code=False
        )
        
        # 验证结果
        assert "geoName" in results
        assert "Vision Pro" in results
    
    @pytest.mark.asyncio
    async def test_get_trending_searches(self, trends_service, mock_pytrends):
        """测试获取热门搜索"""
        # 模拟热门搜索数据
        mock_data = {
            "title": ["Vision Pro", "Apple Event", "AR Technology"],
            "traffic": ["500K+", "200K+", "100K+"]
        }
        mock_pytrends.trending_searches.return_value = mock_data
        
        results = await trends_service.get_trending_searches(pn="united_states")
        
        # 验证调用
        mock_pytrends.trending_searches.assert_called_once_with(pn="united_states")
        
        # 验证结果
        assert "title" in results
        assert "traffic" in results
    
    @pytest.mark.asyncio
    async def test_compare_keywords(self, trends_service, mock_pytrends):
        """测试关键词比较"""
        # 模拟比较数据
        mock_data = {
            "Vision Pro": [30, 40, 50],
            "Meta Quest": [20, 25, 30],
            "HoloLens": [10, 15, 20],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"]
        }
        mock_pytrends.interest_over_time.return_value = mock_data
        
        results = await trends_service.compare_keywords(
            keywords=["Vision Pro", "Meta Quest", "HoloLens"]
        )
        
        # 验证调用
        mock_pytrends.build_payload.assert_called_once_with(
            ["Vision Pro", "Meta Quest", "HoloLens"],
            timeframe="today 12-m",
            geo=""
        )
        
        # 验证结果
        for keyword in ["Vision Pro", "Meta Quest", "HoloLens"]:
            assert keyword in results
        assert "date" in results
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, trends_service, mock_pytrends):
        """测试API错误处理"""
        # 模拟API错误
        mock_pytrends.interest_over_time.side_effect = Exception("Google Trends API Error")
        
        results = await trends_service.get_interest_over_time(["Vision Pro"])
        
        # 应该返回空结果而不是崩溃
        assert results == {}
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, trends_service, mock_pytrends):
        """测试速率限制处理"""
        # 模拟速率限制错误
        mock_pytrends.interest_over_time.side_effect = [
            Exception("429 Too Many Requests"),
            {"Vision Pro": [10, 20, 30]}  # 重试后成功
        ]
        
        with patch('asyncio.sleep', return_value=None):  # 模拟延迟
            results = await trends_service.get_interest_over_time(["Vision Pro"])
        
        # 应该在重试后成功
        assert "Vision Pro" in results
        assert mock_pytrends.interest_over_time.call_count == 2
    
    def test_format_timeframe(self, trends_service):
        """测试时间范围格式化"""
        # 测试不同的时间范围格式
        test_cases = [
            ("1d", "now 1-d"),
            ("7d", "now 7-d"),
            ("1m", "today 1-m"),
            ("3m", "today 3-m"),
            ("1y", "today 12-m"),
            ("5y", "today 5-y")
        ]
        
        for input_format, expected in test_cases:
            result = trends_service._format_timeframe(input_format)
            assert result == expected
    
    def test_validate_keywords(self, trends_service):
        """测试关键词验证"""
        # 测试有效关键词
        valid_keywords = ["Vision Pro", "Apple", "AR Technology"]
        result = trends_service._validate_keywords(valid_keywords)
        assert result == valid_keywords
        
        # 测试无效关键词（空字符串、过长等）
        invalid_keywords = ["", "a" * 200, None]
        result = trends_service._validate_keywords(invalid_keywords)
        assert len(result) == 0
        
        # 测试混合情况
        mixed_keywords = ["Vision Pro", "", "Apple", "a" * 200, "Valid Keyword"]
        result = trends_service._validate_keywords(mixed_keywords)
        assert len(result) == 3
        assert "Vision Pro" in result
        assert "Apple" in result
        assert "Valid Keyword" in result
    
    @pytest.mark.asyncio
    async def test_batch_keyword_analysis(self, trends_service, mock_pytrends):
        """测试批量关键词分析"""
        keywords = ["Vision Pro", "Meta Quest", "HoloLens", "Magic Leap"]
        
        # 模拟批量分析结果
        mock_results = []
        for i, keyword in enumerate(keywords):
            mock_data = {
                keyword: [10 + i * 5, 20 + i * 5, 30 + i * 5],
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"]
            }
            mock_results.append(mock_data)
        
        mock_pytrends.interest_over_time.side_effect = mock_results
        
        results = await trends_service.batch_keyword_analysis(keywords)
        
        # 验证结果
        assert len(results) == len(keywords)
        for keyword in keywords:
            assert keyword in results
            assert len(results[keyword]) > 0
    
    @pytest.mark.parametrize("geo,expected_calls", [
        ("", 1),  # 全球
        ("US", 1),  # 美国
        ("CN", 1),  # 中国
    ])
    @pytest.mark.asyncio
    async def test_different_geo_regions(self, trends_service, mock_pytrends, geo, expected_calls):
        """参数化测试：不同地理区域"""
        mock_data = {"Vision Pro": [10, 20, 30]}
        mock_pytrends.interest_over_time.return_value = mock_data
        
        results = await trends_service.get_interest_over_time(
            keywords=["Vision Pro"],
            geo=geo
        )
        
        # 验证调用次数和参数
        assert mock_pytrends.build_payload.call_count == expected_calls
        call_args = mock_pytrends.build_payload.call_args
        assert call_args[1]["geo"] == geo
        
        # 验证结果
        assert "Vision Pro" in results