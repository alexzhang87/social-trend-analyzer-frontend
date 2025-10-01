"""
Product Hunt 官方API服务

Product Hunt提供官方GraphQL API，适合获取产品发布信息。

API文档：https://api.producthunt.com/v2/docs
认证方式：OAuth2（需要应用注册）
免费额度：每月1000次请求（足够使用）

注册流程：
1. 访问：https://api.producthunt.com/v2/oauth/applications
2. 创建应用，获取 client_id 和 client_secret
3. 设置重定向URI（可以是本地地址用于开发）

优势：
- 官方API，数据准确
- 获取完整产品信息
- 支持多种查询方式
- 创业者用户群体的刚需功能
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from ..services.enhanced_text_analysis_service import enhanced_text_analysis_service

logger = logging.getLogger(__name__)


class ProductHuntOfficialService:
    """Product Hunt 官方API服务"""
    
    def __init__(self):
        # 从环境变量获取认证信息
        self.client_id = os.getenv("PRODUCT_HUNT_CLIENT_ID")
        self.client_secret = os.getenv("PRODUCT_HUNT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("PRODUCT_HUNT_REDIRECT_URI", "http://localhost:8000/auth/callback")
        
        self.access_token = None
        self.token_expires_at = None
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        
        # 速率限制
        self.rate_limit_delay = 1.0  # 每秒最多1次请求
    
    async def _get_access_token(self) -> str:
        """获取访问令牌（使用Client Credentials流程）"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        if not all([self.client_id, self.client_secret]):
            logger.error("Product Hunt API认证信息不完整")
            raise ValueError("请配置Product Hunt API认证信息：PRODUCT_HUNT_CLIENT_ID, PRODUCT_HUNT_CLIENT_SECRET")
        
        token_url = "https://api.producthunt.com/v2/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data['access_token']
                        expires_in = token_data.get('expires_in', 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("Product Hunt访问令牌获取成功")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Product Hunt认证失败: {response.status} - {error_text}")
                        raise Exception(f"Product Hunt认证失败: {response.status}")
        
        except Exception as e:
            logger.error(f"获取Product Hunt访问令牌失败: {e}")
            raise
    
    async def _make_graphql_request(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """发起GraphQL请求"""
        token = await self._get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            await asyncio.sleep(self.rate_limit_delay)  # 速率限制
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'errors' in result:
                            logger.error(f"GraphQL错误: {result['errors']}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Product Hunt API请求失败: {response.status} - {error_text}")
                        return {"data": None}
        
        except Exception as e:
            logger.error(f"Product Hunt API请求异常: {e}")
            return {"data": None}
    
    async def get_daily_products(self, date: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取指定日期的产品列表
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天
            limit: 返回结果数量限制
            
        Returns:
            产品列表
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        query GetPosts($postedAfter: DateTime, $postedBefore: DateTime, $first: Int) {
          posts(postedAfter: $postedAfter, postedBefore: $postedBefore, first: $first) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                website
                votesCount
                commentsCount
                createdAt
                featuredAt
                makers {
                  name
                  username
                }
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
                thumbnail {
                  url
                }
              }
            }
          }
        }
        """
        
        # 设置时间范围（指定日期的24小时）
        start_datetime = f"{date}T00:00:00Z"
        end_datetime = f"{date}T23:59:59Z"
        
        variables = {
            'postedAfter': start_datetime,
            'postedBefore': end_datetime,
            'first': limit
        }
        
        logger.info(f"获取Product Hunt {date} 的产品，limit={limit}")
        
        try:
            response = await self._make_graphql_request(query, variables)
            
            if not response.get('data') or not response['data'].get('posts'):
                logger.warning("Product Hunt API响应为空")
                return []
            
            products = []
            for edge in response['data']['posts']['edges']:
                product_data = edge['node']
                
                # 提取制作者信息
                makers = [maker['name'] for maker in product_data.get('makers', [])]
                
                # 提取主题标签
                topics = []
                for topic_edge in product_data.get('topics', {}).get('edges', []):
                    topics.append(topic_edge['node']['name'])
                
                product = {
                    "url": product_data.get('url', ''),
                    "content": f"{product_data.get('name', '')} - {product_data.get('tagline', '')}. {product_data.get('description', '')}",
                    "author": ", ".join(makers) if makers else "Unknown",
                    "source": "product_hunt",
                    "published_at": product_data.get('createdAt', ''),
                    "votes": product_data.get('votesCount', 0),
                    "comments_count": product_data.get('commentsCount', 0),
                    "platform_specific": {
                        "product_hunt_id": product_data.get('id'),
                        "name": product_data.get('name'),
                        "tagline": product_data.get('tagline'),
                        "website": product_data.get('website'),
                        "thumbnail_url": product_data.get('thumbnail', {}).get('url'),
                        "topics": topics,
                        "featured_at": product_data.get('featuredAt'),
                        "makers": makers
                    }
                }
                
                products.append(product)
            
            logger.info(f"从Product Hunt获取到 {len(products)} 个产品")
            return products
            
        except Exception as e:
            logger.error(f"获取Product Hunt产品失败: {e}")
            return []
    
    async def search_products(self, keywords: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索相关产品
        
        Args:
            keywords: 关键词列表
            limit: 返回结果数量限制
            
        Returns:
            产品列表
        """
        # 获取最近一周的产品，然后进行关键词过滤
        products = []
        
        # 获取最近7天的产品
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_products = await self.get_daily_products(date, 20)
            products.extend(daily_products)
            
            if len(products) >= limit:
                break
        
        # 基于关键词过滤
        relevant_products = []
        for product in products:
            content_lower = product['content'].lower()
            if any(keyword.lower() in content_lower for keyword in keywords):
                relevant_products.append(product)
        
        # 按投票数排序
        relevant_products.sort(key=lambda x: x.get('votes', 0), reverse=True)
        
        logger.info(f"从Product Hunt搜索到 {len(relevant_products)} 个相关产品")
        return relevant_products[:limit]
    
    async def get_trending_topics(self) -> List[str]:
        """
        获取热门主题标签
        
        Returns:
            热门主题列表
        """
        query = """
        query GetTopics($first: Int) {
          topics(first: $first) {
            edges {
              node {
                name
                postsCount
              }
            }
          }
        }
        """
        
        variables = {'first': 50}
        
        try:
            response = await self._make_graphql_request(query, variables)
            
            if not response.get('data') or not response['data'].get('topics'):
                return []
            
            topics = []
            for edge in response['data']['topics']['edges']:
                topic_data = edge['node']
                topics.append({
                    'name': topic_data['name'],
                    'posts_count': topic_data.get('postsCount', 0)
                })
            
            # 按产品数量排序
            topics.sort(key=lambda x: x['posts_count'], reverse=True)
            
            # 返回前20个热门主题名称
            return [topic['name'] for topic in topics[:20]]
            
        except Exception as e:
            logger.error(f"获取Product Hunt热门主题失败: {e}")
            return []
    
    async def get_daily_products_enhanced(self, date: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取指定日期的产品列表（增强版，包含文本分析）
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天
            limit: 返回结果数量限制
            
        Returns:
            包含文本分析的产品列表
        """
        # 先获取基础产品数据
        products = await self.get_daily_products(date, limit)
        
        # 为每个产品添加文本分析
        enhanced_products = []
        for product in products:
            try:
                # 构建分析文本
                analysis_text = product.get('content', '')
                
                # 执行文本分析
                sentiment_analysis = enhanced_text_analysis_service.analyze_sentiment_comprehensive(analysis_text)
                keywords_extracted = enhanced_text_analysis_service.extract_keywords(analysis_text, max_keywords=8)
                text_stats = enhanced_text_analysis_service.analyze_text_statistics(analysis_text)
                
                # 添加分析结果
                product['text_analysis'] = {
                    "sentiment": sentiment_analysis,
                    "keywords": keywords_extracted,
                    "statistics": text_stats
                }
                
                enhanced_products.append(product)
                
            except Exception as e:
                logger.error(f"Product Hunt产品文本分析失败: {e}")
                # 即使分析失败，也保留原始产品数据
                enhanced_products.append(product)
        
        logger.info(f"Product Hunt增强分析完成，处理了 {len(enhanced_products)} 个产品")
        return enhanced_products


# 全局实例
product_hunt_service = ProductHuntOfficialService()