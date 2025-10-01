from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pytrends.request import TrendReq
import pandas as pd
import time
import random

logger = logging.getLogger(__name__)

class GoogleTrendsService:
    """Google Trends数据抓取服务"""
    
    def __init__(self):
        self.pytrends = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Google Trends客户端"""
        try:
            # 使用最简单的配置来避免初始化错误
            self.pytrends = TrendReq(
                hl='zh-CN',  # 语言设置为中文
                tz=480       # 时区设置为中国时区 (UTC+8)
            )
            logger.info("Google Trends客户端初始化成功")
        except Exception as e:
            logger.error(f"Google Trends客户端初始化失败: {e}")
            # 如果中文配置失败，尝试英文配置
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
                logger.info("Google Trends客户端使用英文配置初始化成功")
            except Exception as e2:
                logger.error(f"Google Trends客户端英文配置也失败: {e2}")
                # 最后尝试默认配置
                try:
                    self.pytrends = TrendReq()
                    logger.info("Google Trends客户端使用默认配置初始化成功")
                except Exception as e3:
                    logger.error(f"Google Trends客户端默认配置也失败: {e3}")
                    self.pytrends = None
    
    def _add_delay(self):
        """添加随机延迟以避免被限制"""
        delay = random.uniform(1, 3)
        time.sleep(delay)
    
    def get_trending_searches(self, geo: str = 'CN') -> List[Dict[str, Any]]:
        """获取热门搜索趋势
        
        Args:
            geo: 地理位置代码，默认为中国(CN)
            
        Returns:
            热门搜索列表
        """
        if not self.pytrends:
            self._initialize_client()
            
        if not self.pytrends:
            return []
        
        try:
            self._add_delay()
            
            # 获取每日热门搜索
            trending_searches = self.pytrends.trending_searches(pn=geo)
            
            results = []
            for i, term in enumerate(trending_searches[0].head(20)):
                results.append({
                    'rank': i + 1,
                    'term': term,
                    'geo': geo,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"成功获取{len(results)}个热门搜索趋势")
            return results
            
        except Exception as e:
            logger.error(f"获取热门搜索趋势失败: {e}")
            return []
    
    def get_interest_over_time(
        self, 
        keywords: List[str], 
        timeframe: str = 'today 12-m',
        geo: str = 'CN'
    ) -> Dict[str, Any]:
        """获取关键词的时间趋势数据
        
        Args:
            keywords: 关键词列表（最多5个）
            timeframe: 时间范围，如 'today 12-m', 'today 3-m', 'today 1-m'
            geo: 地理位置代码
            
        Returns:
            时间趋势数据
        """
        # 每次都重新初始化客户端以确保稳定性
        self._initialize_client()
            
        if not self.pytrends:
            return {'error': 'Google Trends客户端未初始化'}
        
        try:
            # 限制关键词数量
            keywords = keywords[:5]
            
            self._add_delay()
            
            # 构建payload
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            # 获取时间趋势数据
            interest_over_time_df = self.pytrends.interest_over_time()
            
            if interest_over_time_df.empty:
                return {
                    'keywords': keywords,
                    'timeframe': timeframe,
                    'geo': geo,
                    'data': [],
                    'message': '没有找到相关数据'
                }
            
            # 转换为JSON格式
            data = []
            for index, row in interest_over_time_df.iterrows():
                data_point = {
                    'date': index.strftime('%Y-%m-%d'),
                    'timestamp': index.isoformat()
                }
                for keyword in keywords:
                    if keyword in row:
                        data_point[keyword] = int(row[keyword])
                data.append(data_point)
            
            result = {
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo,
                'data': data,
                'total_points': len(data)
            }
            
            logger.info(f"成功获取关键词 {keywords} 的时间趋势数据，共{len(data)}个数据点")
            return result
            
        except Exception as e:
            logger.error(f"获取时间趋势数据失败: {e}")
            return {
                'error': str(e),
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo
            }
    
    def get_interest_by_region(
        self, 
        keywords: List[str], 
        timeframe: str = 'today 12-m',
        geo: str = 'CN'
    ) -> Dict[str, Any]:
        """获取关键词的地区分布数据
        
        Args:
            keywords: 关键词列表
            timeframe: 时间范围
            geo: 地理位置代码
            
        Returns:
            地区分布数据
        """
        # 每次都重新初始化客户端以确保稳定性
        self._initialize_client()
            
        if not self.pytrends:
            return {'error': 'Google Trends客户端未初始化'}
        
        try:
            keywords = keywords[:5]
            
            self._add_delay()
            
            # 构建payload
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            # 获取地区数据
            interest_by_region_df = self.pytrends.interest_by_region(
                resolution='REGION',
                inc_low_vol=True,
                inc_geo_code=False
            )
            
            if interest_by_region_df.empty:
                return {
                    'keywords': keywords,
                    'timeframe': timeframe,
                    'geo': geo,
                    'data': [],
                    'message': '没有找到相关地区数据'
                }
            
            # 转换为JSON格式
            data = []
            for region, row in interest_by_region_df.iterrows():
                region_data = {
                    'region': region
                }
                for keyword in keywords:
                    if keyword in row:
                        region_data[keyword] = int(row[keyword])
                data.append(region_data)
            
            # 按第一个关键词的值排序
            if keywords and data:
                data.sort(key=lambda x: x.get(keywords[0], 0), reverse=True)
            
            result = {
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo,
                'data': data[:20],  # 只返回前20个地区
                'total_regions': len(data)
            }
            
            logger.info(f"成功获取关键词 {keywords} 的地区分布数据，共{len(data)}个地区")
            return result
            
        except Exception as e:
            logger.error(f"获取地区分布数据失败: {e}")
            return {
                'error': str(e),
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo
            }
    
    def get_related_queries(
        self, 
        keywords: List[str], 
        timeframe: str = 'today 12-m',
        geo: str = 'CN'
    ) -> Dict[str, Any]:
        """获取相关查询
        
        Args:
            keywords: 关键词列表
            timeframe: 时间范围
            geo: 地理位置代码
            
        Returns:
            相关查询数据
        """
        # 每次都重新初始化客户端以确保稳定性
        self._initialize_client()
            
        if not self.pytrends:
            return {'error': 'Google Trends客户端未初始化'}
        
        try:
            keywords = keywords[:5]
            
            self._add_delay()
            
            # 构建payload
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            # 获取相关查询
            related_queries = self.pytrends.related_queries()
            
            result = {
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo,
                'related_queries': {}
            }
            
            for keyword in keywords:
                if keyword in related_queries:
                    keyword_data = {
                        'top': [],
                        'rising': []
                    }
                    
                    # 处理热门相关查询
                    if related_queries[keyword]['top'] is not None:
                        top_df = related_queries[keyword]['top']
                        keyword_data['top'] = [
                            {
                                'query': row['query'],
                                'value': int(row['value'])
                            }
                            for _, row in top_df.head(10).iterrows()
                        ]
                    
                    # 处理上升相关查询
                    if related_queries[keyword]['rising'] is not None:
                        rising_df = related_queries[keyword]['rising']
                        keyword_data['rising'] = [
                            {
                                'query': row['query'],
                                'value': row['value']
                            }
                            for _, row in rising_df.head(10).iterrows()
                        ]
                    
                    result['related_queries'][keyword] = keyword_data
            
            logger.info(f"成功获取关键词 {keywords} 的相关查询数据")
            return result
            
        except Exception as e:
            logger.error(f"获取相关查询数据失败: {e}")
            return {
                'error': str(e),
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试Google Trends连接
        
        Returns:
            连接测试结果
        """
        try:
            # 每次都重新初始化客户端以确保稳定性
            self._initialize_client()
            
            if not self.pytrends:
                return {
                    'status': 'error',
                    'message': 'Google Trends客户端初始化失败',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 尝试获取简单的热门搜索来测试连接
            test_result = self.get_trending_searches()
            
            if test_result:
                return {
                    'status': 'success',
                    'message': 'Google Trends连接正常',
                    'sample_trends': test_result[:3],  # 返回前3个热门搜索作为示例
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Google Trends连接成功但无法获取数据',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Google Trends连接测试失败: {e}")
            return {
                'status': 'error',
                'message': f'连接测试失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }