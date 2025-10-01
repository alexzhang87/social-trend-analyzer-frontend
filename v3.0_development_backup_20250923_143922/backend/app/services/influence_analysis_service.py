from typing import List, Dict, Any, Optional
import logging
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
from ..services.large_dataset_service import LargeDatasetService
from ..data.models.advanced_analytics import InfluenceAnalysis
from ..data.models.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger("trend-analyzer")

class InfluenceAnalysisService:
    """影响力分析服务"""
    
    def __init__(self):
        self.dataset_service = LargeDatasetService()
        logger.info("InfluenceAnalysisService 已初始化")
    
    def analyze_influencer_impact(self, keywords: List[str], user_id: int) -> dict:
        """分析关键意见领袖(KOL)影响力"""
        logger.info(f"开始影响力分析: {keywords}")
        
        try:
            # 获取相关数据
            posts = self.dataset_service.search_posts(keywords, limit=1000)
            if not posts:
                return self._get_empty_influence_result(keywords)
            
            # 识别影响力用户
            influencers = self._identify_influencers(posts)
            
            # 分析影响力网络
            influence_network = self._analyze_influence_network(posts, influencers)
            
            # 计算影响力指标
            influence_metrics = self._calculate_influence_metrics(influencers, posts)
            
            # 分析传播路径
            propagation_paths = self._analyze_propagation_paths(posts, influencers)
            
            # 影响力趋势分析
            influence_trends = self._analyze_influence_trends(posts, influencers)
            
            # 生成分析结果
            result = {
                "keywords": keywords,
                "influencers": influencers,
                "influence_network": influence_network,
                "influence_metrics": influence_metrics,
                "propagation_paths": propagation_paths,
                "influence_trends": influence_trends,
                "total_posts": len(posts),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "insights": self._generate_influence_insights(influencers, influence_metrics)
            }
            
            # 保存到数据库
            self._save_influence_analysis(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"影响力分析失败: {e}")
            return self._get_empty_influence_result(keywords, str(e))
    
    def analyze_viral_content(self, keywords: List[str], user_id: int) -> dict:
        """分析病毒式传播内容"""
        logger.info(f"开始病毒式传播分析: {keywords}")
        
        try:
            # 获取相关数据
            posts = self.dataset_service.search_posts(keywords, limit=1000)
            if not posts:
                return self._get_empty_viral_result(keywords)
            
            # 识别病毒式传播内容
            viral_content = self._identify_viral_content(posts)
            
            # 分析传播特征
            viral_characteristics = self._analyze_viral_characteristics(viral_content)
            
            # 传播速度分析
            propagation_speed = self._analyze_propagation_speed(viral_content)
            
            # 内容特征分析
            content_features = self._analyze_content_features(viral_content)
            
            # 生成分析结果
            result = {
                "keywords": keywords,
                "viral_content": viral_content,
                "viral_characteristics": viral_characteristics,
                "propagation_speed": propagation_speed,
                "content_features": content_features,
                "total_viral_posts": len(viral_content),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "insights": self._generate_viral_insights(viral_content, viral_characteristics)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"病毒式传播分析失败: {e}")
            return self._get_empty_viral_result(keywords, str(e))
    
    def _identify_influencers(self, posts: List[Dict]) -> List[Dict]:
        """识别影响力用户"""
        user_stats = defaultdict(lambda: {
            'posts_count': 0,
            'total_engagement': 0,
            'avg_engagement': 0,
            'followers_estimate': 0,
            'influence_score': 0
        })
        
        # 统计用户数据
        for post in posts:
            author = post.get('author', 'unknown')
            engagement = post.get('engagement_score', 0)
            
            user_stats[author]['posts_count'] += 1
            user_stats[author]['total_engagement'] += engagement
        
        # 计算影响力指标
        influencers = []
        for author, stats in user_stats.items():
            if stats['posts_count'] > 0:
                stats['avg_engagement'] = stats['total_engagement'] / stats['posts_count']
                
                # 估算粉丝数（基于平均互动数）
                stats['followers_estimate'] = int(stats['avg_engagement'] * 50)  # 简化估算
                
                # 计算影响力评分
                stats['influence_score'] = self._calculate_influence_score(
                    stats['posts_count'],
                    stats['avg_engagement'],
                    stats['followers_estimate']
                )
                
                if stats['influence_score'] > 0.3:  # 影响力阈值
                    influencers.append({
                        'author': author,
                        'posts_count': stats['posts_count'],
                        'avg_engagement': round(stats['avg_engagement'], 2),
                        'followers_estimate': stats['followers_estimate'],
                        'influence_score': round(stats['influence_score'], 3),
                        'tier': self._classify_influencer_tier(stats['influence_score'])
                    })
        
        # 按影响力评分排序
        influencers.sort(key=lambda x: x['influence_score'], reverse=True)
        return influencers[:20]  # 返回前20名影响者
    
    def _analyze_influence_network(self, posts: List[Dict], influencers: List[Dict]) -> Dict:
        """分析影响力网络"""
        influencer_names = {inf['author'] for inf in influencers}
        
        # 分析互动关系
        interactions = defaultdict(int)
        for post in posts:
            author = post.get('author', 'unknown')
            if author in influencer_names:
                # 模拟互动关系（实际应用中需要真实的转发、回复数据）
                for other_inf in influencer_names:
                    if other_inf != author and np.random.random() < 0.1:  # 10%概率有互动
                        interactions[(author, other_inf)] += 1
        
        # 构建网络结构
        network_nodes = []
        network_edges = []
        
        for influencer in influencers:
            network_nodes.append({
                'id': influencer['author'],
                'influence_score': influencer['influence_score'],
                'tier': influencer['tier'],
                'followers': influencer['followers_estimate']
            })
        
        for (source, target), weight in interactions.items():
            if weight > 0:
                network_edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight,
                    'interaction_strength': min(1.0, weight / 10)
                })
        
        return {
            'nodes': network_nodes,
            'edges': network_edges,
            'network_density': len(network_edges) / max(1, len(network_nodes) * (len(network_nodes) - 1) / 2),
            'total_interactions': sum(interactions.values())
        }
    
    def _calculate_influence_metrics(self, influencers: List[Dict], posts: List[Dict]) -> Dict:
        """计算影响力指标"""
        if not influencers:
            return {
                'total_influencers': 0,
                'avg_influence_score': 0,
                'top_tier_count': 0,
                'reach_estimate': 0,
                'engagement_rate': 0
            }
        
        # 基础统计
        total_influencers = len(influencers)
        avg_influence_score = sum(inf['influence_score'] for inf in influencers) / total_influencers
        
        # 分层统计
        tier_counts = defaultdict(int)
        for inf in influencers:
            tier_counts[inf['tier']] += 1
        
        # 估算总覆盖范围
        total_reach = sum(inf['followers_estimate'] for inf in influencers)
        
        # 计算平均互动率
        total_engagement = sum(inf['avg_engagement'] for inf in influencers)
        avg_engagement_rate = total_engagement / max(1, total_reach) * 100
        
        return {
            'total_influencers': total_influencers,
            'avg_influence_score': round(avg_influence_score, 3),
            'tier_distribution': dict(tier_counts),
            'top_tier_count': tier_counts.get('top', 0),
            'reach_estimate': total_reach,
            'engagement_rate': round(avg_engagement_rate, 2)
        }
    
    def _analyze_propagation_paths(self, posts: List[Dict], influencers: List[Dict]) -> List[Dict]:
        """分析传播路径"""
        influencer_names = {inf['author'] for inf in influencers}
        
        # 模拟传播路径（实际应用中需要真实的转发链数据）
        propagation_paths = []
        
        for i, influencer in enumerate(influencers[:5]):  # 分析前5名影响者的传播路径
            # 模拟传播路径
            path_length = np.random.randint(2, 6)  # 传播路径长度2-5
            path = [influencer['author']]
            
            current_reach = influencer['followers_estimate']
            for step in range(path_length - 1):
                # 模拟下一级传播者
                next_user = f"user_{np.random.randint(1000, 9999)}"
                path.append(next_user)
                current_reach = int(current_reach * np.random.uniform(0.1, 0.3))  # 传播衰减
            
            propagation_paths.append({
                'path_id': f"path_{i+1}",
                'origin_influencer': influencer['author'],
                'path': path,
                'path_length': len(path),
                'estimated_reach': current_reach,
                'propagation_speed': np.random.uniform(0.5, 2.0)  # 小时
            })
        
        return propagation_paths
    
    def _analyze_influence_trends(self, posts: List[Dict], influencers: List[Dict]) -> Dict:
        """分析影响力趋势"""
        # 模拟时间序列数据
        days = 30
        influence_timeline = []
        
        for day in range(days):
            date = (datetime.utcnow() - timedelta(days=days-day-1)).strftime('%Y-%m-%d')
            
            # 模拟每日影响力指标
            daily_influence = {
                'date': date,
                'active_influencers': np.random.randint(len(influencers)//2, len(influencers)),
                'total_reach': np.random.randint(10000, 100000),
                'engagement_volume': np.random.randint(1000, 10000),
                'viral_coefficient': np.random.uniform(1.0, 3.0)
            }
            influence_timeline.append(daily_influence)
        
        # 计算趋势
        recent_week = influence_timeline[-7:]
        previous_week = influence_timeline[-14:-7]
        
        recent_avg_reach = sum(day['total_reach'] for day in recent_week) / 7
        previous_avg_reach = sum(day['total_reach'] for day in previous_week) / 7
        
        trend_direction = "increasing" if recent_avg_reach > previous_avg_reach else "decreasing"
        trend_magnitude = abs(recent_avg_reach - previous_avg_reach) / previous_avg_reach * 100
        
        return {
            'timeline': influence_timeline,
            'trend_direction': trend_direction,
            'trend_magnitude': round(trend_magnitude, 1),
            'peak_influence_date': max(influence_timeline, key=lambda x: x['total_reach'])['date'],
            'avg_daily_reach': round(sum(day['total_reach'] for day in influence_timeline) / len(influence_timeline))
        }
    
    def _identify_viral_content(self, posts: List[Dict]) -> List[Dict]:
        """识别病毒式传播内容"""
        # 按互动数排序，选择高互动内容
        sorted_posts = sorted(posts, key=lambda x: x.get('engagement_score', 0), reverse=True)
        
        # 设定病毒式传播阈值（前10%的高互动内容）
        viral_threshold = max(1, len(posts) // 10)
        viral_posts = sorted_posts[:viral_threshold]
        
        viral_content = []
        for i, post in enumerate(viral_posts):
            viral_content.append({
                'rank': i + 1,
                'content_id': post.get('id', f"viral_{i+1}"),
                'text': post.get('text', '')[:200] + '...' if len(post.get('text', '')) > 200 else post.get('text', ''),
                'author': post.get('author', 'unknown'),
                'platform': post.get('platform', 'unknown'),
                'engagement_score': post.get('engagement_score', 0),
                'sentiment': post.get('sentiment', 'neutral'),
                'viral_score': self._calculate_viral_score(post),
                'estimated_reach': post.get('engagement_score', 0) * 20  # 简化估算
            })
        
        return viral_content
    
    def _calculate_influence_score(self, posts_count: int, avg_engagement: float, followers: int) -> float:
        """计算影响力评分"""
        # 综合考虑发帖频率、平均互动和粉丝数
        activity_score = min(1.0, posts_count / 10)  # 发帖活跃度
        engagement_score = min(1.0, avg_engagement / 100)  # 互动质量
        reach_score = min(1.0, followers / 10000)  # 覆盖范围
        
        # 加权计算
        influence_score = (activity_score * 0.3 + engagement_score * 0.4 + reach_score * 0.3)
        return influence_score
    
    def _classify_influencer_tier(self, influence_score: float) -> str:
        """分类影响者等级"""
        if influence_score >= 0.8:
            return "top"
        elif influence_score >= 0.6:
            return "high"
        elif influence_score >= 0.4:
            return "medium"
        else:
            return "emerging"
    
    def _calculate_viral_score(self, post: Dict) -> float:
        """计算病毒式传播评分"""
        engagement = post.get('engagement_score', 0)
        
        # 基于互动数的病毒式评分
        viral_score = min(1.0, engagement / 1000)
        
        # 考虑情感因素（极端情感更容易传播）
        sentiment = post.get('sentiment', 'neutral')
        if sentiment in ['positive', 'negative']:
            viral_score *= 1.2
        
        return round(viral_score, 3)
    
    def _analyze_viral_characteristics(self, viral_content: List[Dict]) -> Dict:
        """分析病毒式传播特征"""
        if not viral_content:
            return {}
        
        # 平台分布
        platform_dist = defaultdict(int)
        sentiment_dist = defaultdict(int)
        
        for content in viral_content:
            platform_dist[content['platform']] += 1
            sentiment_dist[content['sentiment']] += 1
        
        # 计算平均指标
        avg_engagement = sum(content['engagement_score'] for content in viral_content) / len(viral_content)
        avg_viral_score = sum(content['viral_score'] for content in viral_content) / len(viral_content)
        total_reach = sum(content['estimated_reach'] for content in viral_content)
        
        return {
            'platform_distribution': dict(platform_dist),
            'sentiment_distribution': dict(sentiment_dist),
            'avg_engagement': round(avg_engagement, 2),
            'avg_viral_score': round(avg_viral_score, 3),
            'total_estimated_reach': total_reach,
            'content_count': len(viral_content)
        }
    
    def _analyze_propagation_speed(self, viral_content: List[Dict]) -> Dict:
        """分析传播速度"""
        # 模拟传播速度数据
        speed_data = []
        
        for content in viral_content[:5]:  # 分析前5个病毒内容
            # 模拟传播时间线（小时）
            timeline = []
            cumulative_reach = 0
            
            for hour in range(24):  # 24小时传播
                # 模拟每小时增长
                if hour < 6:  # 前6小时快速增长
                    growth = content['estimated_reach'] * 0.4 * np.random.uniform(0.8, 1.2)
                elif hour < 12:  # 6-12小时中等增长
                    growth = content['estimated_reach'] * 0.2 * np.random.uniform(0.8, 1.2)
                else:  # 12小时后缓慢增长
                    growth = content['estimated_reach'] * 0.05 * np.random.uniform(0.8, 1.2)
                
                cumulative_reach += growth
                timeline.append({
                    'hour': hour,
                    'cumulative_reach': int(cumulative_reach),
                    'hourly_growth': int(growth)
                })
            
            speed_data.append({
                'content_id': content['content_id'],
                'timeline': timeline,
                'peak_hour': 3,  # 模拟峰值时间
                'total_24h_reach': int(cumulative_reach)
            })
        
        return {
            'speed_analysis': speed_data,
            'avg_peak_time': 3.5,  # 平均峰值时间（小时）
            'avg_24h_reach': sum(data['total_24h_reach'] for data in speed_data) / len(speed_data) if speed_data else 0
        }
    
    def _analyze_content_features(self, viral_content: List[Dict]) -> Dict:
        """分析内容特征"""
        if not viral_content:
            return {}
        
        # 文本长度分析
        text_lengths = [len(content.get('text', '')) for content in viral_content]
        avg_length = sum(text_lengths) / len(text_lengths)
        
        # 关键词提取（简化版）
        all_text = ' '.join(content.get('text', '') for content in viral_content)
        words = all_text.lower().split()
        word_freq = defaultdict(int)
        
        for word in words:
            if len(word) > 3:  # 过滤短词
                word_freq[word] += 1
        
        # 获取高频词
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'avg_text_length': round(avg_length, 1),
            'length_distribution': {
                'short': len([l for l in text_lengths if l < 50]),
                'medium': len([l for l in text_lengths if 50 <= l < 200]),
                'long': len([l for l in text_lengths if l >= 200])
            },
            'top_keywords': [{'word': word, 'frequency': freq} for word, freq in top_keywords],
            'content_themes': self._extract_content_themes(viral_content)
        }
    
    def _extract_content_themes(self, viral_content: List[Dict]) -> List[str]:
        """提取内容主题"""
        # 简化的主题提取
        themes = []
        
        for content in viral_content:
            text = content.get('text', '').lower()
            
            # 基于关键词匹配主题
            if any(word in text for word in ['科技', 'tech', 'ai', '人工智能']):
                themes.append('科技')
            elif any(word in text for word in ['娱乐', 'entertainment', '明星']):
                themes.append('娱乐')
            elif any(word in text for word in ['新闻', 'news', '时事']):
                themes.append('新闻')
            elif any(word in text for word in ['生活', 'lifestyle', '日常']):
                themes.append('生活')
            else:
                themes.append('其他')
        
        # 统计主题分布
        theme_counts = defaultdict(int)
        for theme in themes:
            theme_counts[theme] += 1
        
        return [{'theme': theme, 'count': count} for theme, count in theme_counts.items()]
    
    def _generate_influence_insights(self, influencers: List[Dict], metrics: Dict) -> List[str]:
        """生成影响力洞察"""
        insights = []
        
        if influencers:
            top_influencer = influencers[0]
            insights.append(f"顶级影响者 {top_influencer['author']} 的影响力评分为 {top_influencer['influence_score']:.3f}")
            
            if metrics['total_influencers'] > 0:
                insights.append(f"共识别出 {metrics['total_influencers']} 位影响者，平均影响力评分 {metrics['avg_influence_score']:.3f}")
                
            if metrics.get('top_tier_count', 0) > 0:
                insights.append(f"其中 {metrics['top_tier_count']} 位为顶级影响者")
                
            if metrics.get('reach_estimate', 0) > 0:
                insights.append(f"总覆盖范围估计达到 {metrics['reach_estimate']:,} 人")
        
        return insights
    
    def _generate_viral_insights(self, viral_content: List[Dict], characteristics: Dict) -> List[str]:
        """生成病毒式传播洞察"""
        insights = []
        
        if viral_content:
            insights.append(f"识别出 {len(viral_content)} 个病毒式传播内容")
            
            top_content = viral_content[0]
            insights.append(f"最高互动内容的病毒式评分为 {top_content['viral_score']:.3f}")
            
            if characteristics.get('total_estimated_reach'):
                insights.append(f"病毒内容总覆盖范围估计 {characteristics['total_estimated_reach']:,} 人次")
                
            # 平台分布洞察
            platform_dist = characteristics.get('platform_distribution', {})
            if platform_dist:
                dominant_platform = max(platform_dist.items(), key=lambda x: x[1])
                insights.append(f"{dominant_platform[0]} 平台的病毒传播最为活跃")
        
        return insights
    
    def _save_influence_analysis(self, user_id: int, result: Dict):
        """保存影响力分析结果到数据库"""
        try:
            db = next(get_db())
            
            analysis = InfluenceAnalysis(
                user_id=user_id,
                keywords=result['keywords'],
                influencer_data=result.get('influencers', []),
                network_metrics=result.get('influence_metrics', {}),
                viral_content=result.get('viral_content', []),
                status="completed"
            )
            
            db.add(analysis)
            db.commit()
            logger.info(f"影响力分析结果已保存到数据库")
            
        except Exception as e:
            logger.error(f"保存影响力分析结果失败: {e}")
    
    def get_user_influence_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取用户影响力分析历史"""
        try:
            db = next(get_db())
            
            analyses = db.query(InfluenceAnalysis).filter(
                InfluenceAnalysis.user_id == user_id
            ).order_by(InfluenceAnalysis.created_at.desc()).limit(limit).all()
            
            return [{
                "id": analysis.id,
                "keywords": analysis.keywords,
                "influencer_count": len(analysis.influencer_data) if analysis.influencer_data else 0,
                "viral_content_count": len(analysis.viral_content) if analysis.viral_content else 0,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat()
            } for analysis in analyses]
            
        except Exception as e:
            logger.error(f"获取影响力分析历史失败: {e}")
            return []
    
    def _get_empty_influence_result(self, keywords: List[str], error: str = None) -> Dict:
        """获取空的影响力分析结果"""
        return {
            "keywords": keywords,
            "influencers": [],
            "influence_network": {'nodes': [], 'edges': [], 'network_density': 0, 'total_interactions': 0},
            "influence_metrics": {
                'total_influencers': 0,
                'avg_influence_score': 0,
                'top_tier_count': 0,
                'reach_estimate': 0,
                'engagement_rate': 0
            },
            "propagation_paths": [],
            "influence_trends": {},
            "total_posts": 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "insights": ["数据不足，无法进行影响力分析"],
            "error": error
        }
    
    def _get_empty_viral_result(self, keywords: List[str], error: str = None) -> Dict:
        """获取空的病毒式传播分析结果"""
        return {
            "keywords": keywords,
            "viral_content": [],
            "viral_characteristics": {},
            "propagation_speed": {},
            "content_features": {},
            "total_viral_posts": 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "insights": ["数据不足，无法进行病毒式传播分析"],
            "error": error
        }