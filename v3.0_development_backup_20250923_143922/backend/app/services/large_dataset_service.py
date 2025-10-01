import json
import os
from typing import List, Dict, Any
from datetime import datetime
from ..utils.logger import logger

class LargeDatasetService:
    """
    大规模数据集服务 - 使用预生成的1000条模拟数据
    """
    
    def __init__(self):
        self.dataset_path = "large_social_dataset.json"
        self.dataset = None
        self._load_dataset()
        logger.info("LargeDatasetService 已初始化")

    def _load_dataset(self):
        """加载预生成的数据集"""
        try:
            if os.path.exists(self.dataset_path):
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    self.dataset = json.load(f)
                logger.info(f"✅ 成功加载数据集: {len(self.dataset['data'])} 条数据")
            else:
                logger.error(f"❌ 数据集文件不存在: {self.dataset_path}")
                self.dataset = None
        except Exception as e:
            logger.error(f"❌ 加载数据集失败: {e}")
            self.dataset = None

    def search_posts(self, keywords: List[str], limit: int = 1000, platform_filter: str = None, time_range: str = None) -> List[Dict[str, Any]]:
        """
        从大规模数据集中搜索相关帖子
        
        Args:
            keywords: 搜索关键词列表
            limit: 返回结果数量限制
            platform_filter: 平台过滤器 ('X', 'Reddit', 'twitter', 'reddit', None表示所有平台)
            time_range: 时间范围过滤器 ('1 Week', '1 Month', '3 Months', '6 Months')
        """
        if not self.dataset:
            logger.error("数据集未加载，无法搜索")
            return []

        # 平台名称映射：前端传来的值 -> 数据集中的值
        platform_mapping = {
            'X': 'twitter',
            'x': 'twitter', 
            'Twitter': 'twitter',
            'twitter': 'twitter',
            'Reddit': 'reddit',
            'reddit': 'reddit'
        }
        
        # 转换平台过滤器
        mapped_platform = None
        if platform_filter:
            mapped_platform = platform_mapping.get(platform_filter, platform_filter.lower())
            
        logger.info(f"从大规模数据集搜索关键词: {keywords}, 原始平台过滤: {platform_filter}, 映射后平台过滤: {mapped_platform}, 时间范围: {time_range}, 限制: {limit}")
        
        all_posts = self.dataset['data']
        matched_posts = []
        
        # 时间范围过滤
        filtered_posts = self._filter_posts_by_time_range(all_posts, time_range)
        
        # 关键词匹配逻辑
        seen_posts = set()  # 用于去重的集合
        for post in filtered_posts:
            # 平台过滤
            if mapped_platform and post.get('platform', '').lower() != mapped_platform:
                continue
                
            post_text = post.get('text', '').lower()
            post_title = post.get('title', '').lower()
            
            # 检查是否包含任何关键词
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if (keyword_lower in post_text or 
                    keyword_lower in post_title or
                    keyword in post.get('keywords_matched', [])):
                    
                    # 去重逻辑：基于文本内容和作者
                    post_key = (post.get('text', '').strip().lower(), post.get('author', ''))
                    if post_key not in seen_posts:
                        seen_posts.add(post_key)
                        matched_posts.append(post)
                    break  # 找到匹配就跳出内层循环
            
            if len(matched_posts) >= limit:
                break
        
        logger.info(f"✅ 找到 {len(matched_posts)} 条匹配的帖子 (平台: {platform_filter or '所有'})")
        
        # 按时间排序（最新的在前）
        matched_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return matched_posts[:limit]

    def _filter_posts_by_time_range(self, posts: List[Dict[str, Any]], time_range: str) -> List[Dict[str, Any]]:
        """
        根据时间范围过滤帖子
        
        Args:
            posts: 帖子列表
            time_range: 时间范围 ('1 Week', '1 Month', '3 Months', '6 Months')
        """
        if not time_range:
            return posts
            
        from datetime import datetime, timedelta
        
        # 时间范围映射
        time_mapping = {
            '1 Week': 7,
            '1 Month': 30,
            '3 Months': 90,
            '6 Months': 180
        }
        
        days = time_mapping.get(time_range)
        if not days:
            logger.warning(f"未知的时间范围: {time_range}，返回所有数据")
            return posts
            
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_posts = []
        
        for post in posts:
            try:
                # 解析帖子的创建时间
                created_at_str = post.get('created_at', '')
                if created_at_str:
                    # 尝试多种日期格式
                    for date_format in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            post_date = datetime.strptime(created_at_str, date_format)
                            break
                        except ValueError:
                            continue
                    else:
                        # 如果所有格式都失败，跳过这个帖子
                        continue
                        
                    # 检查是否在时间范围内
                    if post_date >= cutoff_date:
                        filtered_posts.append(post)
                        
            except Exception as e:
                logger.warning(f"解析帖子时间失败: {e}")
                # 如果解析失败，保留帖子（避免丢失数据）
                filtered_posts.append(post)
                
        logger.info(f"时间范围过滤: {time_range} ({days}天) - 从 {len(posts)} 条帖子过滤到 {len(filtered_posts)} 条")
        return filtered_posts

    def get_platform_distribution(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取平台分布统计"""
        distribution = {}
        for post in posts:
            platform = post.get('platform', 'unknown')
            distribution[platform] = distribution.get(platform, 0) + 1
        return distribution

    def get_sentiment_distribution(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取情感分布统计"""
        distribution = {}
        for post in posts:
            sentiment = post.get('sentiment', 'neutral')
            distribution[sentiment] = distribution.get(sentiment, 0) + 1
        return distribution

    def get_engagement_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取互动数据统计"""
        if not posts:
            return {}
        
        twitter_posts = [p for p in posts if p.get('platform') == 'twitter']
        reddit_posts = [p for p in posts if p.get('platform') == 'reddit']
        
        stats = {
            'total_posts': len(posts),
            'twitter_stats': {
                'count': len(twitter_posts),
                'avg_likes': sum(p.get('likes', 0) for p in twitter_posts) / len(twitter_posts) if twitter_posts else 0,
                'avg_retweets': sum(p.get('retweets', 0) for p in twitter_posts) / len(twitter_posts) if twitter_posts else 0,
                'total_engagement': sum(p.get('likes', 0) + p.get('retweets', 0) + p.get('replies', 0) for p in twitter_posts)
            },
            'reddit_stats': {
                'count': len(reddit_posts),
                'avg_upvotes': sum(p.get('upvotes', 0) for p in reddit_posts) / len(reddit_posts) if reddit_posts else 0,
                'avg_comments': sum(p.get('comments', 0) for p in reddit_posts) / len(reddit_posts) if reddit_posts else 0,
                'total_engagement': sum(p.get('upvotes', 0) + p.get('comments', 0) for p in reddit_posts)
            }
        }
        
        return stats

    def format_posts_for_analysis(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化帖子数据供LLM分析使用
        """
        formatted_posts = []
        
        for post in posts:
            formatted_post = {
                "platform": post.get("platform", "unknown"),
                "author": post.get("author", "anonymous"),
                "text": post.get("text", ""),
                "url": post.get("url", ""),
                "created_at": post.get("created_at", ""),
                "sentiment": post.get("sentiment", "neutral"),
                "engagement": self._calculate_engagement_score(post),
                "metadata": {
                    "language": post.get("language", "en"),
                    "verified": post.get("verified", False) if post.get("platform") == "twitter" else None,
                    "subreddit": post.get("subreddit") if post.get("platform") == "reddit" else None
                }
            }
            formatted_posts.append(formatted_post)
        
        return formatted_posts

    def _calculate_engagement_score(self, post: Dict[str, Any]) -> int:
        """计算帖子的综合互动分数"""
        if post.get("platform") == "twitter":
            return (post.get("likes", 0) + 
                   post.get("retweets", 0) * 2 + 
                   post.get("replies", 0) * 3)
        elif post.get("platform") == "reddit":
            return (post.get("upvotes", 0) + 
                   post.get("comments", 0) * 2 + 
                   post.get("awards", 0) * 5)
        else:
            return 0

    def get_dataset_info(self) -> Dict[str, Any]:
        """获取数据集基本信息"""
        if not self.dataset:
            return {"error": "数据集未加载"}
        
        return {
            "total_posts": len(self.dataset['data']),
            "generated_at": self.dataset.get('generated_at'),
            "keywords": self.dataset.get('keywords', []),
            "stats": self.dataset.get('stats', {}),
            "platforms": list(set(post.get('platform') for post in self.dataset['data'])),
            "date_range": self.dataset.get('stats', {}).get('date_range', {})
        }