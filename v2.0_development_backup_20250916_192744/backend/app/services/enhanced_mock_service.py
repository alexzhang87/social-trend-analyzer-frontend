import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..utils.logger import logger

class EnhancedMockService:
    """
    增强的模拟数据服务 - 生成1000条高质量模拟数据
    500条Twitter + 500条Reddit
    """
    
    def __init__(self):
        self.twitter_templates = self._load_twitter_templates()
        self.reddit_templates = self._load_reddit_templates()
        self.sentiment_weights = {"positive": 0.4, "neutral": 0.35, "negative": 0.25}
        logger.info("EnhancedMockService 已初始化")

    def _load_twitter_templates(self) -> Dict[str, List[str]]:
        """加载Twitter内容模板"""
        return {
            "AI": [
                "Just tried the new AI tool and it's mind-blowing! 🤖 #AI #Technology",
                "AI is revolutionizing healthcare. Saw a demo today that could save lives 💊",
                "Worried about AI taking jobs, but excited about the possibilities 🤔",
                "ChatGPT helped me write better code today. AI is becoming essential 💻",
                "The AI hype is real, but are we ready for the consequences? 🚨",
                "Machine learning models are getting scary good at predictions 📊",
                "AI art is beautiful but raises questions about human creativity 🎨",
                "Investing in AI startups - this is the next big wave 💰",
                "AI customer service is improving but still lacks human touch 📞",
                "Ethical AI development should be our top priority right now ⚖️"
            ],
            "机器学习": [
                "机器学习正在改变我们的工作方式 🔬",
                "深度学习模型的准确率越来越高了 📈",
                "学习机器学习算法真的很有挑战性 💪",
                "机器学习在医疗诊断方面的应用令人惊叹 🏥",
                "数据质量对机器学习模型至关重要 📊",
                "机器学习工程师的需求量暴增 💼",
                "AutoML让机器学习变得更加普及 🚀",
                "机器学习模型的可解释性很重要 🔍",
                "边缘计算与机器学习的结合很有前景 📱",
                "机器学习在推荐系统中的应用太强了 🎯"
            ],
            "cryptocurrency": [
                "Bitcoin hitting new highs! 🚀 #BTC #Crypto",
                "DeFi is the future of finance, traditional banks are worried 🏦",
                "Lost money on that altcoin, crypto is so volatile 😭",
                "Ethereum 2.0 staking rewards are looking good 💎",
                "NFTs are dead, told you it was a bubble 💸",
                "Regulation is coming, crypto market is nervous 📉",
                "Web3 development is where the money is right now 💻",
                "HODL strategy paying off after 3 years 💪",
                "Crypto adoption by institutions is accelerating 🏢",
                "Mining costs are getting crazy with energy prices ⚡"
            ]
        }

    def _load_reddit_templates(self) -> Dict[str, List[str]]:
        """加载Reddit内容模板"""
        return {
            "AI": [
                "DAE think AI is overhyped? I work in tech and most 'AI' is just fancy algorithms",
                "LPT: Use AI tools to automate your boring tasks, but don't rely on them for critical thinking",
                "TIL that AI models can be biased based on their training data. This is concerning for society",
                "AITA for using AI to write my college essays? My professor says it's cheating",
                "ELI5: How do neural networks actually work? All the explanations I find are too complex",
                "Unpopular opinion: AI will create more jobs than it destroys, just like previous tech revolutions",
                "PSA: That viral AI-generated image is fake. We need better media literacy",
                "AMA Request: Someone who works on AI safety at a major tech company",
                "Shower thought: If AI becomes conscious, would turning it off be murder?",
                "TIFU by trusting AI to write important code without reviewing it first"
            ],
            "机器学习": [
                "刚入门机器学习，有什么好的学习路径推荐吗？",
                "分享一个机器学习项目：用深度学习识别猫咪品种",
                "机器学习面试题目越来越难了，大家都是怎么准备的？",
                "讨论：机器学习在小公司的实际应用价值",
                "求助：机器学习模型过拟合问题怎么解决？",
                "机器学习工程师 vs 数据科学家，哪个更有前景？",
                "推荐几个机器学习的开源项目，适合练手",
                "机器学习算法的数学基础到底有多重要？",
                "云平台的机器学习服务对比：AWS vs Azure vs GCP",
                "机器学习模型部署的最佳实践分享"
            ],
            "cryptocurrency": [
                "Crypto winter is here, time to DCA and wait for the next bull run",
                "Which altcoins are you accumulating during this bear market?",
                "Reminder: Only invest what you can afford to lose in crypto",
                "The technology behind blockchain is solid, price speculation is just noise",
                "Crypto regulation might actually be good for long-term adoption",
                "Hardware wallet recommendations for storing crypto safely?",
                "DeFi yields are dropping, is the party over?",
                "Crypto tax reporting is a nightmare, any good tools out there?",
                "Lightning Network adoption is growing, Bitcoin payments getting faster",
                "Staking rewards vs trading profits, what's your strategy?"
            ]
        }

    def _generate_realistic_metrics(self, platform: str, sentiment: str) -> Dict[str, int]:
        """生成真实的互动数据"""
        if platform == "twitter":
            base_likes = random.randint(1, 1000)
            if sentiment == "positive":
                base_likes = int(base_likes * random.uniform(1.2, 2.0))
            elif sentiment == "negative":
                base_likes = int(base_likes * random.uniform(0.5, 0.8))
            
            return {
                "likes": base_likes,
                "retweets": int(base_likes * random.uniform(0.1, 0.3)),
                "replies": int(base_likes * random.uniform(0.05, 0.15)),
                "views": int(base_likes * random.uniform(10, 50))
            }
        else:  # reddit
            base_upvotes = random.randint(1, 500)
            if sentiment == "positive":
                base_upvotes = int(base_upvotes * random.uniform(1.3, 2.5))
            elif sentiment == "negative":
                base_upvotes = int(base_upvotes * random.uniform(0.3, 0.7))
            
            return {
                "upvotes": base_upvotes,
                "downvotes": int(base_upvotes * random.uniform(0.1, 0.4)),
                "comments": int(base_upvotes * random.uniform(0.05, 0.2)),
                "awards": random.randint(0, 5) if base_upvotes > 100 else 0
            }

    def _get_random_sentiment(self) -> str:
        """根据权重随机选择情感"""
        rand = random.random()
        if rand < self.sentiment_weights["positive"]:
            return "positive"
        elif rand < self.sentiment_weights["positive"] + self.sentiment_weights["neutral"]:
            return "neutral"
        else:
            return "negative"

    def _generate_twitter_data(self, keywords: List[str], count: int = 500) -> List[Dict[str, Any]]:
        """生成Twitter模拟数据"""
        logger.info(f"生成 {count} 条Twitter模拟数据")
        
        twitter_data = []
        usernames = [
            "TechGuru2024", "AIEnthusiast", "CryptoTrader", "DataScientist", 
            "StartupFounder", "DigitalNomad", "CodeNewbie", "MLEngineer",
            "BlockchainDev", "TechReporter", "InnovationHub", "FutureBuilder",
            "TechCritic", "AIResearcher", "CryptoAnalyst", "DevCommunity"
        ]
        
        for i in range(count):
            keyword = random.choice(keywords)
            sentiment = self._get_random_sentiment()
            
            # 选择模板
            if keyword in self.twitter_templates:
                text = random.choice(self.twitter_templates[keyword])
            else:
                # 为其他关键词生成通用内容
                text = f"Interesting developments in {keyword} lately. What do you think? #tech"
            
            # 生成时间戳（过去30天内）
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # 生成互动数据
            metrics = self._generate_realistic_metrics("twitter", sentiment)
            
            tweet = {
                "platform": "twitter",
                "id": f"tweet_{i+1}",
                "author": random.choice(usernames),
                "text": text,
                "url": f"https://twitter.com/{random.choice(usernames)}/status/{1234567890 + i}",
                "created_at": created_at.isoformat(),
                "sentiment": sentiment,
                "likes": metrics["likes"],
                "retweets": metrics["retweets"],
                "replies": metrics["replies"],
                "views": metrics["views"],
                "verified": random.choice([True, False]) if random.random() < 0.2 else False,
                "follower_count": random.randint(100, 100000),
                "keywords_matched": [keyword],
                "language": "en" if keyword in ["AI", "cryptocurrency"] else "zh"
            }
            
            twitter_data.append(tweet)
        
        return twitter_data

    def _generate_reddit_data(self, keywords: List[str], count: int = 500) -> List[Dict[str, Any]]:
        """生成Reddit模拟数据"""
        logger.info(f"生成 {count} 条Reddit模拟数据")
        
        reddit_data = []
        subreddits = [
            "r/MachineLearning", "r/artificial", "r/cryptocurrency", "r/technology",
            "r/programming", "r/datascience", "r/startups", "r/investing",
            "r/futurology", "r/singularity", "r/cscareerquestions", "r/webdev"
        ]
        
        usernames = [
            "ml_researcher", "crypto_hodler", "tech_enthusiast", "data_wizard",
            "startup_founder", "code_monkey", "ai_skeptic", "future_predictor",
            "blockchain_believer", "tech_critic", "innovation_seeker", "dev_newbie"
        ]
        
        for i in range(count):
            keyword = random.choice(keywords)
            sentiment = self._get_random_sentiment()
            
            # 选择模板
            if keyword in self.reddit_templates:
                text = random.choice(self.reddit_templates[keyword])
            else:
                text = f"What are your thoughts on the recent developments in {keyword}?"
            
            # 生成时间戳
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # 生成互动数据
            metrics = self._generate_realistic_metrics("reddit", sentiment)
            
            post = {
                "platform": "reddit",
                "id": f"reddit_{i+1}",
                "author": random.choice(usernames),
                "text": text,
                "title": f"Discussion about {keyword}",
                "subreddit": random.choice(subreddits),
                "url": f"https://reddit.com/r/technology/comments/{random.randint(100000, 999999)}/",
                "created_at": created_at.isoformat(),
                "sentiment": sentiment,
                "upvotes": metrics["upvotes"],
                "downvotes": metrics["downvotes"],
                "comments": metrics["comments"],
                "awards": metrics["awards"],
                "score": metrics["upvotes"] - metrics["downvotes"],
                "keywords_matched": [keyword],
                "language": "en" if keyword in ["AI", "cryptocurrency"] else "zh"
            }
            
            reddit_data.append(post)
        
        return reddit_data

    def generate_large_dataset(self, keywords: List[str]) -> Dict[str, Any]:
        """生成大规模数据集（1000条数据）"""
        logger.info(f"开始生成大规模数据集，关键词: {keywords}")
        
        # 生成Twitter数据（500条）
        twitter_data = self._generate_twitter_data(keywords, 500)
        
        # 生成Reddit数据（500条）
        reddit_data = self._generate_reddit_data(keywords, 500)
        
        # 合并数据
        all_data = twitter_data + reddit_data
        
        # 生成统计信息
        stats = {
            "total_posts": len(all_data),
            "twitter_posts": len(twitter_data),
            "reddit_posts": len(reddit_data),
            "sentiment_distribution": {
                "positive": len([d for d in all_data if d["sentiment"] == "positive"]),
                "neutral": len([d for d in all_data if d["sentiment"] == "neutral"]),
                "negative": len([d for d in all_data if d["sentiment"] == "negative"])
            },
            "platform_distribution": {
                "twitter": len(twitter_data),
                "reddit": len(reddit_data)
            },
            "date_range": {
                "earliest": min(d["created_at"] for d in all_data),
                "latest": max(d["created_at"] for d in all_data)
            }
        }
        
        logger.info(f"✅ 成功生成 {len(all_data)} 条模拟数据")
        logger.info(f"📊 情感分布: {stats['sentiment_distribution']}")
        
        return {
            "data": all_data,
            "stats": stats,
            "keywords": keywords,
            "generated_at": datetime.now().isoformat()
        }

    def save_dataset_to_file(self, dataset: Dict[str, Any], filename: str = "large_mock_dataset.json"):
        """保存数据集到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 数据集已保存到 {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ 保存数据集失败: {e}")
            return None
