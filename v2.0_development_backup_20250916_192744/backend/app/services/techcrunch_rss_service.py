"""TechCrunch RSS服务

TechCrunch提供RSS feeds，适合获取权威科技新闻、行业分析数据。

RSS Feeds:
- 主要新闻: https://techcrunch.com/feed/
- 创业公司: https://techcrunch.com/category/startups/feed/
- 应用程序: https://techcrunch.com/category/apps/feed/

优势：
- 权威科技媒体
- 高质量行业分析
- 实时新闻更新
- 免费RSS访问
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from html import unescape
import re

logger = logging.getLogger(__name__)

class TechCrunchRSSService:
    """TechCrunch RSS服务"""
    
    def __init__(self):
        self.feeds = {
            'main': 'https://techcrunch.com/feed/',
            'startups': 'https://techcrunch.com/category/startups/feed/',
            'apps': 'https://techcrunch.com/category/apps/feed/',
            'ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'security': 'https://techcrunch.com/category/security/feed/',
            'venture': 'https://techcrunch.com/category/venture/feed/'
        }
        
        self.session = None
        
        # 更新频率控制
        self.update_interval = 30 * 60  # 30分钟
        self.last_update = {}
        
        logger.info("TechCrunch RSS服务初始化成功")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def _fetch_rss_feed(self, feed_url: str) -> str:
        """获取RSS feed内容"""
        session = await self._get_session()
        
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    logger.error(f"RSS feed请求失败: {response.status} - {feed_url}")
                    return None
                    
        except Exception as e:
            logger.error(f"RSS feed请求异常: {e} - {feed_url}")
            return None
    
    def _parse_rss_content(self, rss_content: str, feed_category: str) -> List[Dict[str, Any]]:
        """解析RSS内容"""
        try:
            root = ET.fromstring(rss_content)
            items = []
            
            # 查找所有item元素
            for item in root.findall('.//item'):
                try:
                    # 提取基本信息
                    title = item.find('title')
                    title_text = unescape(title.text) if title is not None and title.text else ''
                    
                    link = item.find('link')
                    link_text = link.text if link is not None and link.text else ''
                    
                    description = item.find('description')
                    description_text = ''
                    if description is not None and description.text:
                        # 清理HTML标签
                        description_text = re.sub(r'<[^>]+>', '', unescape(description.text))
                    
                    pub_date = item.find('pubDate')
                    pub_date_text = pub_date.text if pub_date is not None and pub_date.text else ''
                    
                    # 解析发布时间
                    published_at = None
                    if pub_date_text:
                        try:
                            # RFC 2822 格式解析
                            from email.utils import parsedate_to_datetime
                            published_at = parsedate_to_datetime(pub_date_text).isoformat()
                        except:
                            published_at = pub_date_text
                    
                    # 提取作者信息
                    author = item.find('dc:creator', {'dc': 'http://purl.org/dc/elements/1.1/'})
                    author_text = author.text if author is not None and author.text else ''
                    
                    # 提取分类标签
                    categories = []
                    for category in item.findall('category'):
                        if category.text:
                            categories.append(category.text)
                    
                    if title_text and link_text:
                        items.append({
                            'title': title_text,
                            'url': link_text,
                            'description': description_text,
                            'author': author_text,
                            'published_at': published_at,
                            'categories': categories,
                            'feed_category': feed_category,
                            'source': 'techcrunch',
                            'content_type': 'news_article'
                        })
                        
                except Exception as e:
                    logger.warning(f"解析RSS item失败: {e}")
                    continue
            
            logger.info(f"成功解析{len(items)}篇{feed_category}文章")
            return items
            
        except Exception as e:
            logger.error(f"解析RSS内容失败: {e}")
            return []
    
    async def get_latest_articles(self, categories: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最新文章
        
        Args:
            categories: 指定分类列表，如果为None则获取所有分类
            limit: 每个分类的文章数量限制
            
        Returns:
            最新文章列表
        """
        if categories is None:
            categories = list(self.feeds.keys())
        
        all_articles = []
        
        # 并行获取各分类的RSS feed
        tasks = []
        for category in categories:
            if category in self.feeds:
                tasks.append(self._get_category_articles(category, limit))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"获取分类文章失败: {result}")
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        logger.info(f"总共获取{len(all_articles)}篇TechCrunch文章")
        return all_articles
    
    async def _get_category_articles(self, category: str, limit: int) -> List[Dict[str, Any]]:
        """获取指定分类的文章"""
        feed_url = self.feeds.get(category)
        if not feed_url:
            return []
        
        # 检查更新频率
        now = datetime.now()
        last_update = self.last_update.get(category)
        if last_update and (now - last_update).total_seconds() < self.update_interval:
            logger.debug(f"分类 {category} 未到更新时间，跳过")
            return []
        
        try:
            # 获取RSS内容
            rss_content = await self._fetch_rss_feed(feed_url)
            if not rss_content:
                return []
            
            # 解析RSS内容
            articles = self._parse_rss_content(rss_content, category)
            
            # 限制数量
            articles = articles[:limit]
            
            # 更新最后更新时间
            self.last_update[category] = now
            
            return articles
            
        except Exception as e:
            logger.error(f"获取分类 {category} 文章失败: {e}")
            return []
    
    async def search_articles(self, keywords: List[str], categories: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索相关文章
        
        Args:
            keywords: 搜索关键词列表
            categories: 指定分类列表
            limit: 返回的文章数量限制
            
        Returns:
            相关文章列表
        """
        try:
            # 获取最新文章
            all_articles = await self.get_latest_articles(categories, 100)
            
            # 关键词匹配
            matched_articles = []
            keywords_lower = [kw.lower() for kw in keywords]
            
            for article in all_articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                categories_text = ' '.join(article.get('categories', [])).lower()
                
                # 检查标题、描述和分类是否包含关键词
                for keyword in keywords_lower:
                    if (keyword in title or 
                        keyword in description or 
                        keyword in categories_text):
                        article['matched_keyword'] = keyword
                        matched_articles.append(article)
                        break
            
            # 按发布时间排序并限制数量
            matched_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            result = matched_articles[:limit]
            
            logger.info(f"关键词搜索找到{len(result)}篇相关文章")
            return result
            
        except Exception as e:
            logger.error(f"搜索文章失败: {e}")
            return []
    
    async def get_trending_topics(self, limit: int = 20) -> List[str]:
        """获取热门话题
        
        Args:
            limit: 返回的话题数量
            
        Returns:
            热门话题关键词列表
        """
        try:
            # 获取最新文章
            articles = await self.get_latest_articles(limit=100)
            
            # 提取标题和分类中的关键词
            all_words = []
            for article in articles:
                title = article.get('title', '')
                categories = article.get('categories', [])
                
                # 从标题提取关键词
                title_words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
                all_words.extend(title_words)
                
                # 从分类提取关键词
                for category in categories:
                    category_words = re.findall(r'\b[a-zA-Z]{4,}\b', category.lower())
                    all_words.extend(category_words)
            
            # 过滤常见词汇
            stop_words = {
                'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know', 
                'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 
                'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 
                'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your',
                'about', 'after', 'again', 'could', 'first', 'other', 'right',
                'should', 'their', 'these', 'think', 'where', 'would', 'years'
            }
            
            filtered_words = [w for w in all_words if w not in stop_words and len(w) > 3]
            
            # 统计词频
            from collections import Counter
            word_counts = Counter(filtered_words)
            
            # 返回最常见的词汇
            trending_topics = [word for word, count in word_counts.most_common(limit)]
            
            logger.info(f"提取到{len(trending_topics)}个热门话题")
            return trending_topics
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return []
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()

# 创建服务实例
techcrunch_rss_service = TechCrunchRSSService()