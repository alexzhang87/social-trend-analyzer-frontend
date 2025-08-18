# 🚀 EIQ Platform 后端开发方案 - 7天MVP实现

## 📋 **执行摘要**

基于前端需求规格和风险分析，本方案专注于核心功能的快速实现，确保单人开发者能在7天内完成MVP交付。采用渐进式开发策略，优先实现前端已有组件的数据支撑功能。

---

## 🏗️ **技术架构设计**

### 核心技术栈
```yaml
框架: FastAPI (Python 3.11+)
数据库: SQLite + Redis (缓存)
部署: Railway/Render + Vercel
监控: Sentry (错误追踪)
API文档: 自动生成 Swagger UI
```

### 项目结构
```
eiq-backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── trends.py          # 核心趋势API
│   │   └── health.py          # 健康检查
│   ├── core/
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── security.py        # 安全配置
│   ├── data/
│   │   ├── collectors/
│   │   │   ├── reddit_collector.py
│   │   │   ├── twitter_collector.py
│   │   │   └── base_collector.py
│   │   ├── processors/
│   │   │   ├── text_processor.py
│   │   │   ├── trend_analyzer.py
│   │   │   └── llm_processor.py
│   │   └── models/
│   │       ├── schemas.py     # Pydantic模型
│   │       └── database.py    # SQLAlchemy模型
│   ├── services/
│   │   ├── trend_service.py
│   │   └── cache_service.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

---

## 📡 **数据抓取模块设计**

### 1. Twitter数据抓取 (使用TwitterAPI.io)

根据调研，TwitterAPI.io提供了比官方API更经济的解决方案，每1000条推文仅需$0.15，比X Pro计划节省97%。

```python
# app/data/collectors/twitter_collector.py
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os

class TwitterCollector:
    def __init__(self):
        self.api_key = os.getenv("TWITTERAPI_IO_KEY")
        self.base_url = "https://api.twitterapi.io/v2"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_tweets(
        self, 
        keyword: str, 
        time_range: str = "7days",
        max_results: int = 1000
    ) -> List[Dict]:
        """搜索推文数据"""
        try:
            # 构建查询参数
            end_time = datetime.utcnow()
            if time_range == "7days":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30days":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=7)
            
            params = {
                "query": f'"{keyword}" -is:retweet lang:en',
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations",
                "user.fields": "username,name,verified",
                "expansions": "author_id",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "max_results": min(max_results, 100)  # API限制
            }
            
            async with self.session.get(
                f"{self.base_url}/tweets/search/recent", 
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_twitter_data(data, keyword)
                else:
                    error_text = await response.text()
                    raise Exception(f"Twitter API Error: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"Error fetching Twitter data: {e}")
            return []
    
    def _process_twitter_data(self, raw_data: Dict, keyword: str) -> List[Dict]:
        """处理Twitter API响应数据"""
        processed_tweets = []
        
        tweets = raw_data.get("data", [])
        users = {user["id"]: user for user in raw_data.get("includes", {}).get("users", [])}
        
        for tweet in tweets:
            user = users.get(tweet["author_id"], {})
            
            processed_tweet = {
                "post_id": tweet["id"],
                "platform": "x",
                "keyword_query": keyword,
                "timestamp": tweet["created_at"],
                "text_content": tweet["text"],
                "author": user.get("username", "unknown"),
                "engagement_score": (
                    tweet.get("public_metrics", {}).get("like_count", 0) +
                    tweet.get("public_metrics", {}).get("retweet_count", 0) * 2 +
                    tweet.get("public_metrics", {}).get("reply_count", 0)
                ),
                "url": f"https://twitter.com/{user.get('username', 'unknown')}/status/{tweet['id']}"
            }
            processed_tweets.append(processed_tweet)
        
        return processed_tweets
```

### 2. Reddit数据抓取

```python
# app/data/collectors/reddit_collector.py
import praw
import asyncio
from typing import List, Dict
from datetime import datetime
import os

class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="EIQ-Platform/1.0"
        )
    
    async def search_posts(
        self, 
        keyword: str, 
        time_range: str = "week",
        limit: int = 1000
    ) -> List[Dict]:
        """搜索Reddit帖子"""
        try:
            # 搜索相关subreddits和帖子
            all_posts = []
            
            # 搜索帖子
            search_results = self.reddit.subreddit("all").search(
                keyword, 
                sort="relevance", 
                time_filter=time_range,
                limit=min(limit, 1000)  # API限制
            )
            
            for submission in search_results:
                # 获取评论(前10个)
                submission.comments.replace_more(limit=0)
                top_comments = [
                    {
                        "text": comment.body,
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "score": comment.score,
                        "created": datetime.fromtimestamp(comment.created_utc).isoformat()
                    }
                    for comment in submission.comments.list()[:10]
                    if hasattr(comment, 'body')
                ]
                
                processed_post = {
                    "post_id": submission.id,
                    "platform": "reddit", 
                    "keyword_query": keyword,
                    "timestamp": datetime.fromtimestamp(submission.created_utc).isoformat(),
                    "text_content": f"{submission.title}. {submission.selftext}",
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "engagement_score": submission.score + submission.num_comments,
                    "url": f"https://reddit.com{submission.permalink}",
                    "subreddit": submission.subreddit.display_name,
                    "comments": top_comments
                }
                all_posts.append(processed_post)
                
                # 添加延迟避免触发限制
                await asyncio.sleep(0.1)
            
            return all_posts
            
        except Exception as e:
            print(f"Error fetching Reddit data: {e}")
            return []
```

### 3. 统一数据收集器

```python
# app/data/collectors/base_collector.py
from abc import ABC, abstractmethod
from typing import List, Dict
import asyncio

class BaseCollector(ABC):
    @abstractmethod
    async def collect_data(self, keyword: str, **kwargs) -> List[Dict]:
        pass

class DataCollectionManager:
    def __init__(self):
        self.collectors = {}
    
    def register_collector(self, platform: str, collector):
        self.collectors[platform] = collector
    
    async def collect_all_platforms(
        self, 
        keyword: str, 
        platforms: List[str],
        **kwargs
    ) -> List[Dict]:
        """并行收集多个平台数据"""
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                collector = self.collectors[platform]
                if platform == "x":
                    task = collector.search_tweets(keyword, **kwargs)
                elif platform == "reddit":
                    task = collector.search_posts(keyword, **kwargs)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果，忽略异常
        all_data = []
        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
        
        return all_data
```

---

## 🧠 **数据分析模块设计**

### 1. 文本预处理

```python
# app/data/processors/text_processor.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter
from typing import List, Dict
import spacy

class TextProcessor:
    def __init__(self):
        # 下载必要的NLTK数据
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('omw-1.4')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # 尝试加载spaCy模型
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except IOError:
            print("spaCy model not found. Using NLTK only.")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # 移除用户提及和hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # 移除特殊字符，保留基本标点
        text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()
    
    def extract_keywords(self, texts: List[str], top_n: int = 20) -> List[Dict]:
        """提取关键词"""
        if not texts:
            return []
        
        all_words = []
        
        for text in texts:
            cleaned = self.clean_text(text)
            tokens = word_tokenize(cleaned)
            
            # 过滤停用词和短词
            filtered_tokens = [
                self.lemmatizer.lemmatize(word)
                for word in tokens
                if word not in self.stop_words 
                and len(word) > 2
                and word.isalpha()
            ]
            
            all_words.extend(filtered_tokens)
        
        # 计算词频
        word_counts = Counter(all_words)
        
        # 返回格式化的关键词列表
        return [
            {"word": word, "count": count, "weight": count / len(all_words)}
            for word, count in word_counts.most_common(top_n)
        ]
    
    def extract_sentiment_keywords(self, texts: List[str]) -> Dict[str, List[str]]:
        """提取情感相关的关键词"""
        positive_indicators = ['good', 'great', 'awesome', 'love', 'amazing', 'excellent']
        negative_indicators = ['bad', 'terrible', 'hate', 'awful', 'worst', 'sucks', 'frustrated']
        
        positive_words = []
        negative_words = []
        
        for text in texts:
            cleaned = self.clean_text(text)
            tokens = word_tokenize(cleaned)
            
            for word in tokens:
                if word in positive_indicators:
                    positive_words.append(word)
                elif word in negative_indicators:
                    negative_words.append(word)
        
        return {
            "positive": list(set(positive_words)),
            "negative": list(set(negative_words))
        }
```

### 2. 趋势分析器

```python
# app/data/processors/trend_analyzer.py
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import numpy as np

class TrendAnalyzer:
    def __init__(self):
        self.time_formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ", 
            "%Y-%m-%d %H:%M:%S"
        ]
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析时间戳"""
        for fmt in self.time_formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # 如果都失败了，返回当前时间
        return datetime.now()
    
    def calculate_trend_history(self, posts: List[Dict]) -> List[Dict]:
        """计算趋势历史数据"""
        if not posts:
            return []
        
        # 按日期分组帖子
        daily_counts = defaultdict(int)
        daily_engagement = defaultdict(list)
        
        for post in posts:
            timestamp = self.parse_timestamp(post.get("timestamp", ""))
            date_key = timestamp.date().isoformat()
            
            daily_counts[date_key] += 1
            daily_engagement[date_key].append(post.get("engagement_score", 0))
        
        # 生成趋势历史
        trend_history = []
        for date_str, count in sorted(daily_counts.items()):
            avg_engagement = np.mean(daily_engagement[date_str]) if daily_engagement[date_str] else 0
            
            # 计算综合分数（提及数 + 平均互动）
            score = count + (avg_engagement * 0.1)
            
            trend_history.append({
                "date": f"{date_str}T12:00:00Z",
                "score": round(score, 2)
            })
        
        return trend_history
    
    def calculate_hot_score(self, posts: List[Dict]) -> float:
        """计算热度分数"""
        if not posts:
            return 0.0
        
        total_engagement = sum(post.get("engagement_score", 0) for post in posts)
        post_count = len(posts)
        
        # 时间衰减因子
        now = datetime.now()
        time_weights = []
        
        for post in posts:
            post_time = self.parse_timestamp(post.get("timestamp", ""))
            time_diff = (now - post_time).total_seconds()
            
            # 24小时内权重1.0，之后每24小时衰减20%
            days_old = time_diff / 86400
            weight = max(0.1, 1.0 - (days_old * 0.2))
            time_weights.append(weight)
        
        # 加权平均
        weighted_engagement = sum(
            post.get("engagement_score", 0) * weight 
            for post, weight in zip(posts, time_weights)
        )
        
        avg_weighted_engagement = weighted_engagement / len(posts) if posts else 0
        
        # 综合热度分数 (0-100)
        hot_score = min(100, (post_count * 2) + (avg_weighted_engagement * 0.5))
        
        return round(hot_score, 1)
    
    def analyze_emotion(self, posts: List[Dict]) -> Dict[str, float]:
        """简单的情感分析"""
        if not posts:
            return {"joy": 0, "sadness": 0, "anger": 0, "sarcasm": 0, "neutral": 100}
        
        # 简单的情感词典
        emotion_keywords = {
            "joy": ["happy", "great", "awesome", "love", "amazing", "excited", "wonderful"],
            "sadness": ["sad", "disappointed", "depressed", "terrible", "awful", "bad"],
            "anger": ["angry", "furious", "hate", "annoying", "frustrated", "mad"],
            "sarcasm": ["yeah right", "sure", "obviously", "totally", "definitely", "lol", "lmao"]
        }
        
        emotion_scores = defaultdict(int)
        total_posts = len(posts)
        
        for post in posts:
            text = post.get("text_content", "").lower()
            post_emotions = set()
            
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        post_emotions.add(emotion)
            
            # 如果没有检测到情感，标记为中性
            if not post_emotions:
                post_emotions.add("neutral")
            
            for emotion in post_emotions:
                emotion_scores[emotion] += 1
        
        # 转换为百分比
        emotion_percentages = {}
        for emotion in ["joy", "sadness", "anger", "sarcasm"]:
            emotion_percentages[emotion] = round(
                (emotion_scores[emotion] / total_posts) * 100, 1
            )
        
        # 中性情感为剩余部分
        assigned_percentage = sum(emotion_percentages.values())
        emotion_percentages["neutral"] = round(100 - assigned_percentage, 1)
        
        return emotion_percentages
```

---

## 🤖 **LLM处理模块设计**

### 核心LLM处理器

```python
# app/data/processors/llm_processor.py
import openai
import asyncio
from typing import List, Dict, Optional
import os
import json
import backoff

class LLMProcessor:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # 成本效益最优
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _make_llm_call(
        self, 
        prompt: str, 
        system_prompt: str = "",
        max_tokens: int = 1000
    ) -> Optional[str]:
        """执行LLM调用，带重试机制"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ] if system_prompt else [{"role": "user", "content": prompt}]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM API Error: {e}")
            return None
    
    async def extract_core_need(self, posts: List[Dict], keyword: str) -> str:
        """提取核心需求"""
        # 准备文本样本
        text_samples = []
        for post in posts[:20]:  # 限制样本数量控制成本
            text = post.get("text_content", "")[:200]  # 截断长文本
            if text:
                text_samples.append(text)
        
        if not text_samples:
            return "Unable to identify core need due to insufficient data"
        
        combined_text = "\n".join(text_samples)
        
        system_prompt = """You are an expert market researcher. Analyze social media discussions to identify the core underlying need that users are expressing."""
        
        prompt = f"""
        Analyze these social media posts about "{keyword}" and identify the primary core need or pain point that users are expressing.
        
        Posts:
        {combined_text}
        
        Provide a concise, actionable core need statement (1-2 sentences).
        """
        
        response = await self._make_llm_call(prompt, system_prompt, 150)
        return response or "Core need analysis unavailable"
    
    async def extract_pain_points(self, posts: List[Dict], keyword: str) -> List[Dict]:
        """提取痛点和证据"""
        # 准备高质量样本
        text_samples = []
        evidence_posts = []
        
        # 按engagement排序，取前30个
        sorted_posts = sorted(
            posts, 
            key=lambda x: x.get("engagement_score", 0), 
            reverse=True
        )[:30]
        
        for post in sorted_posts:
            text = post.get("text_content", "")
            if len(text) > 50:  # 过滤太短的内容
                text_samples.append(text[:300])
                evidence_posts.append(post)
        
        if not text_samples:
            return []
        
        combined_text = "\n---\n".join(text_samples)
        
        system_prompt = """You are an expert at identifying customer pain points from social media discussions. Focus on finding actionable, specific problems that users face."""
        
        prompt = f"""
        Analyze these social media discussions about "{keyword}" and identify 3 distinct pain points.
        
        Posts:
        {combined_text}
        
        For each pain point, provide:
        1. A clear description of the problem
        2. The user intent behind it
        3. Severity score (0-100)
        4. How confident you are (0-1)
        
        Return ONLY valid JSON in this format:
        [
            {{
                "text": "Pain point description",
                "intent": "What users want to achieve", 
                "severity": 75,
                "confidence": 0.8
            }}
        ]
        """
        
        response = await self._make_llm_call(prompt, system_prompt, 800)
        
        if not response:
            return []
        
        try:
            pain_points = json.loads(response)
            
            # 为每个痛点添加证据
            for i, pain_point in enumerate(pain_points):
                # 选择3个最相关的帖子作为证据
                relevant_posts = evidence_posts[i*3:(i+1)*3] if evidence_posts else []
                
                pain_point["evidence"] = [
                    {
                        "text": post.get("text_content", "")[:200],
                        "author": post.get("author", "anonymous"), 
                        "platform": post.get("platform", "unknown"),
                        "url": post.get("url", "#")
                    }
                    for post in relevant_posts
                ]
            
            return pain_points[:3]  # 确保最多3个
            
        except json.JSONDecodeError:
            print("Failed to parse LLM pain points response")
            return []
    
    async def generate_opportunities(self, pain_points: List[Dict], keyword: str) -> List[Dict]:
        """生成商业机会"""
        if not pain_points:
            return []
        
        pain_points_text = "\n".join([
            f"- {pp.get('text', '')} (Severity: {pp.get('severity', 0)})"
            for pp in pain_points
        ])
        
        system_prompt = """You are a business strategy expert. Transform user pain points into concrete business opportunities with realistic impact and effort assessments."""
        
        prompt = f"""
        Based on these pain points related to "{keyword}":
        
        {pain_points_text}
        
        Generate 3 distinct business opportunities that could address these problems.
        
        For each opportunity:
        1. Describe the business solution
        2. Rate potential impact (1-10)
        3. Rate implementation effort (1-10)
        
        Return ONLY valid JSON:
        [
            {{
                "text": "Business opportunity description",
                "impact": 8,
                "effort": 6  
            }}
        ]
        """
        
        response = await self._make_llm_call(prompt, system_prompt, 600)
        
        if not response:
            return []
        
        try:
            opportunities = json.loads(response)
            return opportunities[:3]
        except json.JSONDecodeError:
            print("Failed to parse LLM opportunities response")
            return []
    
    async def generate_mvp_plan(self, opportunities: List[Dict], keyword: str) -> Dict:
        """生成MVP计划"""
        if not opportunities:
            return self._default_mvp_plan()
        
        top_opportunity = opportunities[0].get("text", "")
        
        system_prompt = """You are a lean startup advisor. Create practical 7-day MVP plans that entrepreneurs can execute immediately."""
        
        prompt = f"""
        Create a 7-day MVP development plan for this opportunity: "{top_opportunity}"
        Related to: {keyword}
        
        Provide:
        1. Clear goal statement
        2. Day-by-day tasks (7 days)
        3. Required resources
        4. Estimated budget in USD
        5. Key success metric
        
        Return ONLY valid JSON:
        {{
            "goal": "Specific MVP goal",
            "days": [
                "Day 1: Task description",
                "Day 2: Task description", 
                ...
            ],
            "resources": "Required resources",
            "budget_usd": 500,
            "kpi": "Success metric"
        }}
        """
        
        response = await self._make_llm_call(prompt, system_prompt, 800)
        
        if not response:
            return self._default_mvp_plan()
        
        try:
            mvp_plan = json.loads(response)
            return mvp_plan
        except json.JSONDecodeError:
            return self._default_mvp_plan()
    
    def _default_mvp_plan(self) -> Dict:
        """默认MVP计划"""
        return {
            "goal": "Validate market need with minimal viable product",
            "days": [
                "Day 1: Market research and competitor analysis",
                "Day 2: Define core features and user stories", 
                "Day 3: Create wireframes and basic design",
                "Day 4: Develop core functionality",
                "Day 5: Build basic landing page",
                "Day 6: Conduct user interviews and feedback",
                "Day 7: Iterate based on feedback and plan next steps"
            ],
            "resources": "1 developer, basic design tools, hosting platform",
            "budget_usd": 300,
            "kpi": "Number of users who express interest in the solution"
        }
```

---

## 🚀 **API端点实现**

### 核心趋势API

```python
# app/api/trends.py
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import asyncio

from ..services.trend_service import TrendService
from ..data.models.schemas import TrendClusterResponse

router = APIRouter()
trend_service = TrendService()

@router.get("/api/trends", response_model=List[TrendClusterResponse])
async def get_trends(
    background_tasks: BackgroundTasks,
    keyword: str = Query(..., description="分析关键词"),
    platform: Optional[str] = Query("both", description="平台: x, reddit, both"),
    time_range: Optional[str] = Query("1 Week", description="时间范围: 1 Week, 1 Month"),
    category: Optional[str] = Query("All Categories", description="分类")
):
    """获取趋势分析数据"""
    try:
        # 验证参数
        valid_platforms = ["x", "reddit", "both"]
        valid_time_ranges = ["1 Week", "1 Month"]
        
        if platform not in valid_platforms:
            platform = "both"
        