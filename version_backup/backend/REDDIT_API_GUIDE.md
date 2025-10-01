# Reddit API 申请指南

## 概述
Reddit API是免费的，允许开发者访问Reddit的帖子、评论、用户信息等数据。推荐使用PRAW (Python Reddit API Wrapper)库。

## 申请步骤

### 1. 创建Reddit账户
1. 访问 [Reddit](https://www.reddit.com)
2. 注册或登录账户
3. 确保账户有良好的信誉记录

### 2. 创建Reddit应用
1. 访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. 点击"Create App" 或 "Create Another App"
3. 填写应用信息：
   - **Name**: 应用名称 (例如: "Social Trend Analyzer")
   - **App type**: 选择 "script" (用于个人使用) 或 "web app" (用于Web应用)
   - **Description**: 应用描述 (可选)
   - **About URL**: 应用介绍页面 (可选)
   - **Redirect URI**: 
     - Script类型: `http://localhost:8080`
     - Web app类型: 您的回调URL

### 3. 获取API凭据
应用创建后，您将获得：
- **Client ID**: 应用名称下的字符串
- **Client Secret**: 显示的secret字符串
- **User Agent**: 自定义的用户代理字符串

## 使用PRAW库

### 1. 安装PRAW
```bash
pip install praw
```

### 2. 配置认证
```python
import praw

# 方式1: 直接在代码中配置
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Social Trend Analyzer 1.0 by /u/yourusername",
    username="your_reddit_username",  # 可选，用于账户相关操作
    password="your_reddit_password"    # 可选，用于账户相关操作
)

# 方式2: 使用配置文件 (推荐)
# 创建 praw.ini 文件
reddit = praw.Reddit("bot1")
```

### 3. praw.ini 配置文件示例
```ini
[bot1]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
user_agent=Social Trend Analyzer 1.0 by /u/yourusername
username=your_reddit_username
password=your_reddit_password
```

## 使用示例

### 获取热门帖子
```python
import praw

reddit = praw.Reddit("bot1")

# 获取特定subreddit的热门帖子
subreddit = reddit.subreddit("technology")
for submission in subreddit.hot(limit=10):
    print(f"标题: {submission.title}")
    print(f"作者: {submission.author}")
    print(f"分数: {submission.score}")
    print(f"评论数: {submission.num_comments}")
    print(f"URL: {submission.url}")
    print("-" * 50)
```

### 搜索帖子
```python
# 在特定subreddit中搜索
subreddit = reddit.subreddit("MachineLearning")
for submission in subreddit.search("AI trends", limit=10):
    print(f"标题: {submission.title}")
    print(f"分数: {submission.score}")

# 全Reddit搜索
for submission in reddit.subreddit("all").search("machine learning", limit=10):
    print(f"标题: {submission.title}")
    print(f"Subreddit: {submission.subreddit}")
```

### 获取评论
```python
# 获取帖子的评论
submission = reddit.submission(id="POST_ID")
submission.comments.replace_more(limit=0)  # 加载所有评论

for comment in submission.comments.list():
    print(f"作者: {comment.author}")
    print(f"内容: {comment.body}")
    print(f"分数: {comment.score}")
    print("-" * 30)
```

### 获取用户信息
```python
# 获取用户信息
user = reddit.redditor("username")
print(f"用户: {user.name}")
print(f"积分: {user.link_karma + user.comment_karma}")
print(f"账户创建时间: {user.created_utc}")

# 获取用户的帖子
for submission in user.submissions.new(limit=10):
    print(f"标题: {submission.title}")
```

## 集成到您的项目

### 环境变量配置
```python
# .env 文件
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Social Trend Analyzer 1.0 by /u/yourusername
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### Reddit服务类示例
```python
import praw
import os
from typing import List, Dict, Any

class RedditService:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD")
        )
    
    def search_posts(self, query: str, subreddit: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """搜索Reddit帖子"""
        posts = []
        
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            for submission in subreddit_obj.search(query, limit=limit):
                post_data = {
                    "id": submission.id,
                    "title": submission.title,
                    "content": submission.selftext,
                    "url": submission.url,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "subreddit": str(submission.subreddit),
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "created_utc": submission.created_utc,
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    "flair": submission.link_flair_text,
                    "is_nsfw": submission.over_18
                }
                posts.append(post_data)
                
        except Exception as e:
            print(f"Reddit搜索错误: {e}")
            
        return posts
    
    def get_hot_posts(self, subreddit: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """获取热门帖子"""
        posts = []
        
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            for submission in subreddit_obj.hot(limit=limit):
                post_data = {
                    "id": submission.id,
                    "title": submission.title,
                    "content": submission.selftext,
                    "url": submission.url,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "subreddit": str(submission.subreddit),
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "created_utc": submission.created_utc,
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments
                }
                posts.append(post_data)
                
        except Exception as e:
            print(f"Reddit热门帖子获取错误: {e}")
            
        return posts
```

## API限制和最佳实践

### 速率限制
- **每分钟60次请求** (OAuth认证)
- **每分钟10次请求** (未认证)
- 建议在请求间添加延迟

### 最佳实践
```python
import time

def safe_reddit_request(func, *args, **kwargs):
    """安全的Reddit API请求，包含错误处理和延迟"""
    try:
        result = func(*args, **kwargs)
        time.sleep(1)  # 添加1秒延迟避免速率限制
        return result
    except Exception as e:
        print(f"Reddit API错误: {e}")
        time.sleep(5)  # 错误时等待更长时间
        return None
```

### 用户代理要求
Reddit要求使用描述性的用户代理字符串：
```
格式: <平台>:<应用ID>:<版本> (by /u/<reddit用户名>)
示例: "python:social_trend_analyzer:1.0 (by /u/yourusername)"
```

## 费用
Reddit API完全免费，但有以下限制：
- 速率限制：每分钟60次请求
- 需要遵守Reddit的使用条款和robots.txt

## 常见问题

### 1. 429错误 (Too Many Requests)
- 减少请求频率
- 添加适当的延迟
- 检查是否超出速率限制

### 2. 403错误 (Forbidden)
- 检查API凭据是否正确
- 确保用户代理字符串符合要求
- 检查是否违反了Reddit的使用条款

### 3. 获取更多数据
- 使用分页获取大量数据
- 合理使用`limit`参数
- 考虑缓存机制减少重复请求

## 集成建议
1. **错误处理**: 实现完善的错误处理和重试机制
2. **缓存策略**: 缓存频繁访问的数据
3. **监控**: 监控API使用情况和错误率
4. **更新策略**: 定期更新数据，避免过于频繁的请求