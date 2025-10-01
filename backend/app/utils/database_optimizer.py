from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import time
import logging
from functools import wraps
from collections import defaultdict
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryCache:
    """查询结果缓存管理器"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl  # 缓存生存时间（秒）
    
    def _generate_key(self, query: str, params: Dict = None) -> str:
        """生成缓存键"""
        key_data = {"query": query, "params": params or {}}
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def get(self, query: str, params: Dict = None) -> Optional[Any]:
        """获取缓存结果"""
        key = self._generate_key(query, params)
        
        if key in self.cache:
            cached_data = self.cache[key]
            # 检查是否过期
            if time.time() - cached_data['timestamp'] < self.ttl:
                self.access_times[key] = time.time()
                return cached_data['result']
            else:
                # 过期删除
                del self.cache[key]
                del self.access_times[key]
        
        return None
    
    def set(self, query: str, result: Any, params: Dict = None) -> None:
        """设置缓存结果"""
        key = self._generate_key(query, params)
        
        # 如果缓存已满，删除最久未访问的条目
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), 
                           key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = {
            'result': result,
            'timestamp': time.time()
        }
        self.access_times[key] = time.time()
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        current_time = time.time()
        valid_entries = sum(1 for data in self.cache.values() 
                          if current_time - data['timestamp'] < self.ttl)
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'max_size': self.max_size,
            'ttl': self.ttl
        }

class QueryPerformanceMonitor:
    """查询性能监控器"""
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）
    
    def record_query(self, query: str, execution_time: float, 
                    result_count: int = 0) -> None:
        """记录查询性能"""
        self.query_stats[query].append({
            'execution_time': execution_time,
            'result_count': result_count,
            'timestamp': datetime.now()
        })
        
        # 记录慢查询
        if execution_time > self.slow_query_threshold:
            logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            'total_queries': sum(len(stats) for stats in self.query_stats.values()),
            'unique_queries': len(self.query_stats),
            'slow_queries': [],
            'top_queries_by_frequency': [],
            'top_queries_by_avg_time': []
        }
        
        query_summary = []
        for query, stats in self.query_stats.items():
            avg_time = sum(s['execution_time'] for s in stats) / len(stats)
            total_time = sum(s['execution_time'] for s in stats)
            frequency = len(stats)
            
            query_info = {
                'query': query[:100] + '...' if len(query) > 100 else query,
                'frequency': frequency,
                'avg_time': avg_time,
                'total_time': total_time,
                'max_time': max(s['execution_time'] for s in stats)
            }
            
            query_summary.append(query_info)
            
            # 收集慢查询
            slow_executions = [s for s in stats if s['execution_time'] > self.slow_query_threshold]
            if slow_executions:
                report['slow_queries'].extend([
                    {
                        'query': query[:100] + '...' if len(query) > 100 else query,
                        'execution_time': s['execution_time'],
                        'timestamp': s['timestamp'].isoformat()
                    } for s in slow_executions
                ])
        
        # 按频率排序
        report['top_queries_by_frequency'] = sorted(
            query_summary, key=lambda x: x['frequency'], reverse=True
        )[:10]
        
        # 按平均时间排序
        report['top_queries_by_avg_time'] = sorted(
            query_summary, key=lambda x: x['avg_time'], reverse=True
        )[:10]
        
        return report

class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.query_cache = QueryCache()
        self.performance_monitor = QueryPerformanceMonitor()
    
    def execute_with_cache(self, query: str, params: Dict = None) -> Any:
        """执行带缓存的查询"""
        # 尝试从缓存获取
        cached_result = self.query_cache.get(query, params)
        if cached_result is not None:
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return cached_result
        
        # 执行查询并记录性能
        start_time = time.time()
        try:
            if params:
                result = self.db.execute(text(query), params).fetchall()
            else:
                result = self.db.execute(text(query)).fetchall()
            
            execution_time = time.time() - start_time
            result_count = len(result) if hasattr(result, '__len__') else 0
            
            # 记录性能
            self.performance_monitor.record_query(query, execution_time, result_count)
            
            # 缓存结果（仅缓存小结果集）
            if result_count < 1000:  # 避免缓存大结果集
                self.query_cache.set(query, result, params)
            
            logger.debug(f"Query executed in {execution_time:.2f}s: {query[:50]}...")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.performance_monitor.record_query(query, execution_time, 0)
            logger.error(f"Query failed after {execution_time:.2f}s: {e}")
            raise
    
    def batch_insert(self, table_name: str, data: List[Dict], 
                    batch_size: int = 1000) -> None:
        """批量插入数据"""
        if not data:
            return
        
        # 获取列名
        columns = list(data[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # 分批插入
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            start_time = time.time()
            
            try:
                self.db.execute(text(query), batch)
                self.db.commit()
                
                execution_time = time.time() - start_time
                logger.info(f"Batch insert completed: {len(batch)} records in {execution_time:.2f}s")
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Batch insert failed: {e}")
                raise
    
    def analyze_table_performance(self, table_name: str) -> Dict[str, Any]:
        """分析表性能"""
        try:
            # 获取表统计信息
            stats_query = f"""
            SELECT 
                COUNT(*) as row_count,
                pg_size_pretty(pg_total_relation_size('{table_name}')) as table_size,
                pg_size_pretty(pg_relation_size('{table_name}')) as data_size,
                pg_size_pretty(pg_total_relation_size('{table_name}') - pg_relation_size('{table_name}')) as index_size
            FROM {table_name}
            """
            
            result = self.execute_with_cache(stats_query)
            
            # 获取索引信息
            index_query = f"""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = '{table_name}'
            """
            
            indexes = self.execute_with_cache(index_query)
            
            return {
                'table_name': table_name,
                'statistics': dict(result[0]) if result else {},
                'indexes': [dict(idx) for idx in indexes],
                'recommendations': self._generate_optimization_recommendations(table_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")
            return {'error': str(e)}
    
    def _generate_optimization_recommendations(self, table_name: str) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        try:
            # 检查是否有主键
            pk_query = f"""
            SELECT COUNT(*) as pk_count
            FROM information_schema.table_constraints 
            WHERE table_name = '{table_name}' AND constraint_type = 'PRIMARY KEY'
            """
            
            pk_result = self.execute_with_cache(pk_query)
            if pk_result and pk_result[0][0] == 0:
                recommendations.append(f"建议为表 {table_name} 添加主键")
            
            # 检查外键约束
            fk_query = f"""
            SELECT COUNT(*) as fk_count
            FROM information_schema.table_constraints 
            WHERE table_name = '{table_name}' AND constraint_type = 'FOREIGN KEY'
            """
            
            fk_result = self.execute_with_cache(fk_query)
            if fk_result and fk_result[0][0] == 0:
                recommendations.append(f"考虑为表 {table_name} 添加适当的外键约束")
            
            # 检查索引覆盖率
            col_query = f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            """
            
            columns = self.execute_with_cache(col_query)
            if len(columns) > 5:
                recommendations.append(f"表 {table_name} 列数较多，建议检查是否需要垂直分割")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {table_name}: {e}")
            recommendations.append("无法生成优化建议，请检查数据库连接")
        
        return recommendations
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取完整的优化报告"""
        return {
            'cache_stats': self.query_cache.get_stats(),
            'performance_stats': self.performance_monitor.get_performance_report(),
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self) -> None:
        """清空查询缓存"""
        self.query_cache.clear()
        logger.info("Query cache cleared")

def query_performance_decorator(optimizer: DatabaseOptimizer):
    """查询性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录函数执行性能
                optimizer.performance_monitor.record_query(
                    f"Function: {func.__name__}", 
                    execution_time
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                optimizer.performance_monitor.record_query(
                    f"Function: {func.__name__} (FAILED)", 
                    execution_time
                )
                raise
        return wrapper
    return decorator

# 全局优化器实例（在应用启动时初始化）
_global_optimizer = None

def get_database_optimizer(db: Session) -> DatabaseOptimizer:
    """获取数据库优化器实例"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = DatabaseOptimizer(db)
    return _global_optimizer

def reset_global_optimizer():
    """重置全局优化器（用于测试）"""
    global _global_optimizer
    _global_optimizer = None