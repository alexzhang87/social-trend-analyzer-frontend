import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .social_media_service import SocialMediaService
from ..utils.logger import logger

class MockSocialMediaService(SocialMediaService):
    """模拟社交媒体服务，返回与真实API相同格式的数据"""
    
    def __init__(self):
        logger.info("初始化模拟社交媒体服务")
        
        # 模拟的Twitter用户数据
        self.mock_twitter_users = [
            {"userName": "elonmusk", "name": "Elon Musk", "followers": 150000000},
            {"userName": "OpenAI", "name": "OpenAI", "followers": 5000000},
            {"userName": "sundarpichai", "name": "Sundar Pichai", "followers": 3000000},
            {"userName": "satyanadella", "name": "Satya Nadella", "followers": 2500000},
            {"userName": "tim_cook", "name": "Tim Cook", "followers": 15000000},
        ]
        
        # 模拟的推文模板
        self.mock_tweet_templates = [
            "AI is revolutionizing {industry}. The future is here! #AI #Innovation",
            "Just launched our new {product} powered by artificial intelligence. Excited to see the impact! #Tech #AI",
            "The potential of machine learning in {field} is incredible. We're just getting started. #ML #Future",
            "Artificial intelligence will transform how we {action}. This is just the beginning. #AI #Transformation",
            "Our latest AI breakthrough in {domain} shows promising results. More updates coming soon! #Research #AI",
            "The intersection of AI and {sector} is creating amazing opportunities. #Innovation #Technology",
            "Proud to announce our AI-powered {solution} is now live! #AI #Product #Launch",
            "The future of {industry} is being shaped by artificial intelligence. Exciting times ahead! #AI #Future"
        ]
        
        # 模拟的Reddit帖子模板
        self.mock_reddit_templates = [
            "Discussion: How AI is changing {topic}",
            "What are your thoughts on {subject} in the age of AI?",
            "AI breakthrough in {field} - implications and analysis",
            "The future of {industry} with artificial intelligence",
            "New research on AI applications in {domain}",
            "How machine learning is revolutionizing {sector}",
            "AI ethics discussion: {ethical_topic}",
            "Technical deep dive: AI implementation in {technical_area}"
        ]
        
        # 填充词汇
        self.industries = ["healthcare", "finance", "education", "transportation", "manufacturing"]
        self.products = ["chatbot", "recommendation system", "analytics platform", "automation tool"]
        self.fields = ["medical diagnosis", "financial analysis", "content creation", "data processing"]
        self.actions = ["work", "communicate", "learn", "create", "analyze"]
        self.domains = ["computer vision", "natural language processing", "robotics", "predictive analytics"]
        self.sectors = ["retail", "banking", "media", "logistics", "energy"]
        self.solutions = ["customer service bot", "fraud detection system", "content generator"]
        self.topics = ["machine learning", "deep learning", "neural networks", "automation"]
        self.subjects = ["AI ethics", "job displacement", "privacy concerns", "algorithmic bias"]
        self.ethical_topics = ["AI bias in hiring", "privacy in AI systems", "autonomous decision making"]
        self.technical_areas = ["cloud computing", "edge computing", "mobile apps", "web services"]
    
    def get_twitter_posts(self, query: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """生成模拟的Twitter帖子数据"""
        try:
            logger.info(f"生成模拟Twitter帖子，查询: {query}, 限制: {limit}")
            
            posts = []
            for i in range(min(limit, 50)):  # 最多生成50条
                user = random.choice(self.mock_twitter_users)
                template = random.choice(self.mock_tweet_templates)
                
                # 随机填充模板
                text = template.format(
                    industry=random.choice(self.industries),
                    product=random.choice(self.products),
                    field=random.choice(self.fields),
                    action=random.choice(self.actions),
                    domain=random.choice(self.domains),
                    sector=random.choice(self.sectors),
                    solution=random.choice(self.solutions)
                )
                
                # 生成随机时间（过去7天内）
                created_time = datetime.now() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                post = {
                    "platform": "twitter",
                    "id": f"mock_tweet_{i}_{random.randint(1000, 9999)}",
                    "author": user["userName"],
                    "author_name": user["name"],
                    "text": text,
                    "url": f"https://twitter.com/{user['userName']}/status/{random.randint(1000000000000000000, 9999999999999999999)}",
                    "likes": random.randint(10, 10000),
                    "retweets": random.randint(5, 2000),
                    "replies": random.randint(0, 500),
                    "created_at": created_time.isoformat(),
                    "followers": user["followers"]
                }
                posts.append(post)
            
            logger.info(f"成功生成 {len(posts)} 条模拟Twitter帖子")
            return posts
            
        except Exception as e:
            logger.error(f"生成模拟Twitter帖子失败: {str(e)}")
            return []
    
    def get_reddit_posts(self, subreddit: str, limit: int = 100) -> List[Dict[Any, Any]]:
        """生成模拟的Reddit帖子数据"""
        try:
            logger.info(f"生成模拟Reddit帖子，子版块: {subreddit}, 限制: {limit}")
            
            posts = []
            for i in range(min(limit, 50)):  # 最多生成50条
                template = random.choice(self.mock_reddit_templates)
                
                # 随机填充模板
                title = template.format(
                    topic=random.choice(self.topics),
                    subject=random.choice(self.subjects),
                    field=random.choice(self.fields),
                    industry=random.choice(self.industries),
                    domain=random.choice(self.domains),
                    sector=random.choice(self.sectors),
                    ethical_topic=random.choice(self.ethical_topics),
                    technical_area=random.choice(self.technical_areas)
                )
                
                # 生成随机内容
                content_options = [
                    f"I've been researching this topic and found some interesting insights. What do you think about the implications for {random.choice(self.industries)}?",
                    f"This could be a game-changer for {random.choice(self.sectors)}. Has anyone here worked with similar technologies?",
                    f"The recent developments in this area are fascinating. I'm curious about the community's perspective on {random.choice(self.subjects)}.",
                    f"Looking for discussion on how this might impact {random.choice(self.fields)}. Any experts here?",
                    "Sharing some thoughts and would love to hear your opinions. What are the potential challenges and opportunities?"
                ]
                
                content = random.choice(content_options)
                
                # 生成随机时间（过去7天内）
                created_time = datetime.now() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                post = {
                    "platform": "reddit",
                    "id": f"mock_reddit_{i}_{random.randint(1000, 9999)}",
                    "author": f"user_{random.randint(1000, 9999)}",
                    "text": f"{title}\n\n{content}",
                    "title": title,
                    "subreddit": subreddit,
                    "url": f"https://reddit.com/r/{subreddit}/comments/{random.randint(1000000, 9999999)}/",
                    "likes": random.randint(1, 1000),
                    "comments": random.randint(0, 200),
                    "created_at": created_time.isoformat()
                }
                posts.append(post)
            
            logger.info(f"成功生成 {len(posts)} 条模拟Reddit帖子")
            return posts
            
        except Exception as e:
            logger.error(f"生成模拟Reddit帖子失败: {str(e)}")
            return []