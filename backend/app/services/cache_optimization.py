import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from ..core.redis_client import redis_client
from .cache_service import cache_service
from ..data.models.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class CacheOptimizer:
    """缓存优化器 - 提供缓存预热、批量操作等高级功能"""
    
    def __init__(self):
        self.prewarmed_keys = set()
        self.batch_size = 100
        
    async def prewarm_user_cache(self, user_id: int) -> Dict[str, Any]:
        """预热用户相关缓存"""
        try:
            db = next(get_db())
            results = {}
            
            # 预热用户基本信息
            user_key = f"user:{user_id}:profile"
            if not cache_service.get(user_key):
                user_query = "SELECT * FROM users WHERE id = :user_id"
                user_data = db.execute(text(user_query), {"user_id": user_id}).fetchone()
                if user_data:
                    user_dict = dict(user_data._mapping)
                    cache_service.set(user_key, user_dict, 1800)  # 30分钟
                    results['user_profile'] = 'prewarmed'
                    self.prewarmed_keys.add(user_key)
            
            # 预热用户积分信息
            credits_key = f"user:{user_id}:credits"
            if not cache_service.get(credits_key):
                credits_query = "SELECT credits_balance FROM users WHERE id = :user_id"
                credits_data = db.execute(text(credits_query), {"user_id": user_id}).fetchone()
                if credits_data:
                    cache_service.set(credits_key, credits_data[0], 900)  # 15分钟
                    results['user_credits'] = 'prewarmed'
                    self.prewarmed_keys.add(credits_key)
            
            # 预热用户最近的分析历史
            history_key = f"user:{user_id}:recent_analysis"
            if not cache_service.get(history_key):
                # 这里可以添加分析历史的查询逻辑
                # 暂时使用占位符
                recent_analysis = []
                cache_service.set(history_key, recent_analysis, 600)  # 10分钟
                results['analysis_history'] = 'prewarmed'
                self.prewarmed_keys.add(history_key)
            
            logger.info(f"用户 {user_id} 缓存预热完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"用户缓存预热失败: {e}")
            return {'error': str(e)}
        finally:
            db.close()
    
    async def prewarm_popular_trends(self) -> Dict[str, Any]:
        """预热热门趋势缓存"""
        try:
            popular_keywords = [
                ['AI', '人工智能'],
                ['区块链', 'blockchain'],
                ['元宇宙', 'metaverse'],
                ['新能源', '电动车'],
                ['短视频', 'TikTok']
            ]
            
            results = {}
            for keywords in popular_keywords:
                cache_key = f"trends:popular:{':'.join(sorted(keywords))}"
                if not cache_service.get(cache_key):
                    # 生成模拟的热门趋势数据
                    trend_data = {
                        'keywords': keywords,
                        'popularity_score': 85,
                        'trend_direction': 'up',
                        'last_updated': datetime.now().isoformat(),
                        'source': 'prewarmed'
                    }
                    cache_service.set(cache_key, trend_data, 3600)  # 1小时
                    results[':'.join(keywords)] = 'prewarmed'
                    self.prewarmed_keys.add(cache_key)
            
            logger.info(f"热门趋势缓存预热完成: {len(results)} 个趋势")
            return results
            
        except Exception as e:
            logger.error(f"热门趋势缓存预热失败: {e}")
            return {'error': str(e)}
    
    def batch_set_cache(self, cache_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量设置缓存"""
        try:
            success_count = 0
            failed_count = 0
            
            for item in cache_items:
                key = item.get('key')
                value = item.get('value')
                ttl = item.get('ttl', 3600)
                
                if key and value is not None:
                    if cache_service.set(key, value, ttl):
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            
            result = {
                'total': len(cache_items),
                'success': success_count,
                'failed': failed_count
            }
            
            logger.info(f"批量缓存设置完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"批量缓存设置失败: {e}")
            return {'error': str(e)}
    
    def batch_get_cache(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        try:
            results = {}
            hit_count = 0
            miss_count = 0
            
            for key in keys:
                value = cache_service.get(key)
                if value is not None:
                    results[key] = value
                    hit_count += 1
                else:
                    miss_count += 1
            
            stats = {
                'total_keys': len(keys),
                'hits': hit_count,
                'misses': miss_count,
                'hit_rate': hit_count / len(keys) if keys else 0
            }
            
            logger.info(f"批量缓存获取完成: {stats}")
            return {'data': results, 'stats': stats}
            
        except Exception as e:
            logger.error(f"批量缓存获取失败: {e}")
            return {'error': str(e)}
    
    def intelligent_cache_cleanup(self) -> Dict[str, Any]:
        """智能缓存清理 - 清理过期和低价值缓存"""
        try:
            cleanup_stats = {
                'expired_keys_cleaned': 0,
                'low_value_keys_cleaned': 0,
                'total_cleaned': 0
            }
            
            # 清理Redis中的过期键（Redis会自动处理，这里主要是统计）
            if redis_client.is_connected():
                try:
                    # 获取所有键的TTL信息
                    all_keys = redis_client.keys('cache:*')
                    expired_count = 0
                    
                    for key in all_keys[:100]:  # 限制检查数量避免性能问题
                        ttl = redis_client.ttl(key)
                        if ttl == -2:  # 键已过期
                            expired_count += 1
                    
                    cleanup_stats['expired_keys_cleaned'] = expired_count
                except Exception as e:
                    logger.warning(f"Redis清理检查失败: {e}")
            
            # 清理内存缓存中的过期项
            memory_cache = cache_service.memory_cache
            keys_to_remove = []
            
            for key in list(memory_cache.keys()):
                # 这里可以添加更复杂的清理逻辑
                # 比如基于访问频率、数据大小等
                if len(keys_to_remove) < 10:  # 限制清理数量
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                if key in memory_cache:
                    del memory_cache[key]
                    cleanup_stats['low_value_keys_cleaned'] += 1
            
            cleanup_stats['total_cleaned'] = (
                cleanup_stats['expired_keys_cleaned'] + 
                cleanup_stats['low_value_keys_cleaned']
            )
            
            logger.info(f"智能缓存清理完成: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"智能缓存清理失败: {e}")
            return {'error': str(e)}
    
    def get_cache_health_report(self) -> Dict[str, Any]:
        """获取缓存健康报告"""
        try:
            # 获取基础统计
            basic_stats = cache_service.get_stats()
            
            # 计算缓存效率指标
            redis_stats = basic_stats.get('redis', {})
            memory_stats = basic_stats.get('memory_cache', {})
            
            # 计算命中率
            hits = redis_stats.get('keyspace_hits', 0)
            misses = redis_stats.get('keyspace_misses', 0)
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            
            # 评估缓存健康状态
            health_score = 100
            health_issues = []
            
            if not redis_stats.get('connected', False):
                health_score -= 30
                health_issues.append('Redis连接断开')
            
            if hit_rate < 50:
                health_score -= 20
                health_issues.append(f'缓存命中率过低: {hit_rate:.1f}%')
            
            if memory_stats.get('keys_count', 0) > 1000:
                health_score -= 10
                health_issues.append('内存缓存键数量过多')
            
            health_status = 'excellent' if health_score >= 90 else \
                          'good' if health_score >= 70 else \
                          'warning' if health_score >= 50 else 'critical'
            
            report = {
                'health_score': health_score,
                'health_status': health_status,
                'health_issues': health_issues,
                'cache_stats': basic_stats,
                'performance_metrics': {
                    'hit_rate': hit_rate,
                    'total_requests': total_requests,
                    'prewarmed_keys_count': len(self.prewarmed_keys)
                },
                'recommendations': self._get_optimization_recommendations(health_score, hit_rate)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"缓存健康报告生成失败: {e}")
            return {'error': str(e)}
    
    def _get_optimization_recommendations(self, health_score: float, hit_rate: float) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        if health_score < 70:
            recommendations.append('考虑增加缓存预热策略')
        
        if hit_rate < 60:
            recommendations.append('优化缓存键设计，提高命中率')
            recommendations.append('考虑调整缓存TTL设置')
        
        if not redis_client.is_connected():
            recommendations.append('检查Redis服务状态')
            recommendations.append('配置Redis连接池')
        
        recommendations.append('定期执行缓存清理')
        recommendations.append('监控缓存性能指标')
        
        return recommendations

# 全局缓存优化器实例
cache_optimizer = CacheOptimizer()