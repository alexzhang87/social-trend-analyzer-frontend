from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging
import uuid
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from sqlalchemy.orm import Session

from ..data.models.schemas import AnalysisRequest
from ..data.models.database import User, CreditTransaction, SubscriptionTier, get_db
from ..services.analysis_service import AnalysisService
from ..core.auth import (
    get_current_active_user, 
    require_basic_subscription, 
    require_premium_subscription,
    check_subscription_limit,
    SUBSCRIPTION_LIMITS
)
from ..core.usage_tracker import usage_tracker

logger = logging.getLogger("trend-analyzer")
router = APIRouter()

# 添加综合分析请求模型
from pydantic import BaseModel
from typing import Optional

class ComprehensiveAnalysisRequest(BaseModel):
    keywords: List[str]
    platform_filter: Optional[str] = None
    time_range: Optional[str] = None

# 全局线程池和缓存
thread_pool = ThreadPoolExecutor(max_workers=8)
memory_cache = {}
cache_lock = threading.Lock()

class HighPerformanceAnalyzer:
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.redis_client = None
        try:
            import redis
            self.redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis连接成功 (端口6380)")
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存缓存: {e}")
            self.redis_client = None
    
    # 添加不同订阅等级的分析方法
    async def analyze_tier_free(self, keywords: List[str], platform_filter: str = None, time_range: str = None):
        """FREE版分析"""
        logger.info(f"执行FREE版分析: {keywords}")
        return self.analysis_service.analyze_basic(keywords, platform_filter, time_range)
    
    async def analyze_tier_starter(self, keywords: List[str], platform_filter: str = None, time_range: str = None):
        """STARTER版分析"""
        logger.info(f"执行STARTER版分析: {keywords}")
        return self.analysis_service.analyze_advanced(keywords, platform_filter, time_range)
    
    async def analyze_tier_pro(self, keywords: List[str], platform_filter: str = None, time_range: str = None):
        """PRO版分析"""
        logger.info(f"执行PRO版分析: {keywords}")
        return self.analysis_service.analyze_premium(keywords, platform_filter, time_range)
    
    def get_cache_key(self, keywords: List[str]) -> str:
        """生成缓存键"""
        sorted_keywords = sorted(keywords)
        key_string = json.dumps(sorted_keywords, ensure_ascii=False)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Dict[str, Any]:
        """获取缓存结果"""
        # 先检查内存缓存
        with cache_lock:
            if cache_key in memory_cache:
                cache_data = memory_cache[cache_key]
                if time.time() - cache_data['timestamp'] < 3600:  # 1小时有效
                    logger.info(f"内存缓存命中: {cache_key[:8]}...")
                    result = cache_data['result'].copy()
                    result['cache_info'] = {'source': 'memory', 'hit': True}
                    return result
                else:
                    del memory_cache[cache_key]
        
            try:
                cached = self.redis_client.get(f"analysis:{cache_key}")
                if cached:
                    result = json.loads(str(cached))
                    # 同步到内存缓存
                    with cache_lock:
                        memory_cache[cache_key] = {
                            'result': result,
                            'timestamp': time.time()
                        }
                    logger.info(f"Redis缓存命中: {cache_key[:8]}...")
                    result['cache_info'] = {'source': 'redis', 'hit': True}
                    return result
            except Exception as e:
                logger.warning(f"Redis读取失败: {e}")
        
        return {}
    
    def set_cache(self, cache_key: str, result: Dict[str, Any]):
        """设置缓存"""
        # 设置内存缓存
        with cache_lock:
            memory_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
        
        # 设置Redis缓存
        if self.redis_client:
            try:
                self.redis_client.set(
                    f"analysis:{cache_key}", 
                    json.dumps(result, ensure_ascii=False), 
                    ex=3600
                )
                logger.info(f"结果已缓存: {cache_key[:8]}...")
            except Exception as e:
                logger.warning(f"Redis写入失败: {e}")
    
    def analyze_batch(self, keywords_list: List[List[str]]) -> List[Dict[str, Any]]:
        """批量分析多个关键词组"""
        results = []
        futures = []
        
        logger.info(f"开始批量分析 {len(keywords_list)} 组关键词")
        
        # 提交所有任务到线程池
        for keywords in keywords_list:
            future = thread_pool.submit(self.analyze_single_by_tier, keywords, None)
            futures.append((keywords, future))
        
        # 收集结果
        for keywords, future in futures:
            try:
                result = future.result(timeout=30)  # 30秒超时
                results.append(result)
            except Exception as e:
                logger.error(f"批量分析失败 {keywords}: {e}")
                results.append({
                    "keywords": keywords,
                    "error": str(e),
                    "status": "failed",
                    "cache_info": {'source': 'none', 'hit': False}
                })
        
        return results
    
    def analyze_single_by_tier(self, keywords: List[str], user: User, platform_filter: str = None, time_range: str = None) -> Dict[str, Any]:
        """根据用户订阅等级分析单个关键词组"""
        logger.info(f"analyze_single_by_tier接收到的平台过滤参数: {platform_filter}")
        
        # 为了避免缓存影响平台过滤，将platform_filter包含在缓存键中
        cache_key_base = self.get_cache_key(keywords)
        cache_key = f"{cache_key_base}_{platform_filter or 'all'}"
        tier = user.subscription_tier
        
        # 检查缓存（根据订阅等级添加缓存前缀）
        tier_cache_key = f"{tier.value}_{cache_key}"
        cached_result = self.get_cached_result(tier_cache_key)
        if cached_result:
            logger.info(f"使用缓存结果，平台过滤: {platform_filter}")
            return cached_result
        
        # 执行分析
        start_time = time.time()
        try:
            logger.info(f"开始{tier.value.upper()}级分析: {keywords}")
            
            # 根据订阅等级调用不同的分析方法
            if tier.value == "free":
                result = self.analysis_service.analyze_basic(keywords, platform_filter, time_range)
            elif tier.value == "starter":
                result = self.analysis_service.analyze_standard(keywords, platform_filter, time_range)
            elif tier.value == "pro":
                result = self.analysis_service.analyze_premium(keywords, platform_filter, time_range)
            else:
                # 默认使用基础分析
                result = self.analysis_service.analyze_basic(keywords, platform_filter, time_range)
            
            # 添加性能和层级信息
            analysis_time = round(time.time() - start_time, 2)
            result['performance'] = {
                'analysis_time': analysis_time,
                'processed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'thread_id': threading.get_ident(),
                'tier': tier.value
            }
            result['cache_info'] = {'source': 'none', 'hit': False}
            
            # 缓存结果
            self.set_cache(tier_cache_key, result)
            
            logger.info(f"{tier.value.upper()}级分析完成: {keywords}, 耗时: {analysis_time}秒")
            return result
            
        except Exception as e:
            logger.error(f"{tier.value.upper()}级分析失败 {keywords}: {e}")
            error_result = {
                "keywords": keywords,
                "error": str(e),
                "status": "failed",
                "performance": {
                    "analysis_time": round(time.time() - start_time, 2),
                    "processed_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "thread_id": threading.get_ident(),
                    "tier": tier.value
                },
                "cache_info": {'source': 'none', 'hit': False}
            }
            return error_result

# 全局分析器实例
analyzer = HighPerformanceAnalyzer()

def consume_credits(user: User, credits_required: int, db: Session) -> bool:
    """消耗用户积分"""
    if user.credits_balance < credits_required:
        return False
    
    # 扣除积分
    user.credits_balance = user.credits_balance - credits_required
    
    # 记录积分交易
    transaction = CreditTransaction(
        user_id=user.id,
        amount=-credits_required,
        description=f"Trend analysis consumption",
        transaction_type="consumption"
    )
    
    db.add(transaction)
    db.commit()
    return True

def get_required_credits(subscription_tier: str) -> int:
    """根据订阅等级获取所需积分"""
    credits_map = {
        "free": 1,
        "starter": 2,
        "pro": 3
    }
    return credits_map.get(subscription_tier, 1)

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    request: ComprehensiveAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    综合分析端点 - 根据用户订阅等级提供不同深度的分析
    """
    logger.info(f"开始综合分析: {request.keywords} (用户: {current_user.email}, 订阅: {current_user.subscription_tier})")
    
    # 检查用户订阅限制
    if not check_subscription_limit(current_user, "basic_analysis"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="基础分析功能在您的订阅计划中不可用"
        )
    
    # 检查积分余额
    credits_per_analysis = SUBSCRIPTION_LIMITS[current_user.subscription_tier]["credits_per_analysis"]
    if current_user.credits_balance < credits_per_analysis:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"积分不足，本次分析需要 {credits_per_analysis} 积分"
        )
    
    try:
        analyzer = HighPerformanceAnalyzer()
        
        # 根据用户订阅等级执行不同级别的分析
        if current_user.subscription_tier == SubscriptionTier.FREE:
            result = await analyzer.analyze_tier_free(request.keywords, request.platform_filter, request.time_range)
        elif current_user.subscription_tier == SubscriptionTier.STARTER:
            result = await analyzer.analyze_tier_starter(request.keywords, request.platform_filter, request.time_range)
        elif current_user.subscription_tier == SubscriptionTier.PRO:
            result = await analyzer.analyze_tier_pro(request.keywords, request.platform_filter, request.time_range)
        else:
            result = await analyzer.analyze_tier_free(request.keywords, request.platform_filter, request.time_range)
        
        # 消耗积分
        current_user.credits_balance -= credits_per_analysis
        transaction = CreditTransaction(
            user_id=current_user.id,
            amount=-credits_per_analysis,
            description=f"综合分析: {', '.join(request.keywords)}",
            transaction_type="consumption"
        )
        db.add(transaction)
        db.commit()
        
        logger.info(f"综合分析完成: {request.keywords}")
        
        # 包装返回结果以匹配前端期望的格式
        return {
            "status": "success",
            "data": result,
            "processing_time": result.get("processing_time", 0),
            "user_tier": current_user.subscription_tier.value,
            "remaining_requests": usage_tracker.get_remaining_requests(current_user)
        }
        
    except Exception as e:
        logger.error(f"综合分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )

@router.post("/", status_code=200)
def analyze_keywords_sync(
    request: AnalysisRequest, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """趋势分析 - 支持积分消费和功能分层"""
    try:
        # 获取所需积分
        credits_required = get_required_credits(current_user.subscription_tier.value)
        
        # 检查并消耗积分
        if not consume_credits(current_user, credits_required, db):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {credits_required}, Available: {current_user.credits_balance}"
            )
        
        # 检查使用限制
        if not usage_tracker.check_rate_limit(current_user, "basic_analysis", 1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily usage limit exceeded"
            )
        
        # 检查批量大小限制
        if not check_subscription_limit(current_user, "basic_analysis", len(request.keywords)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Batch size exceeds subscription limit"
            )
        
        start_time = time.time()
        # 使用分层分析方法，传递平台过滤参数和时间范围参数
        platform_filter = getattr(request, 'platform', None)
        time_range = getattr(request, 'timeRange', None)
        logger.info(f"API接收到的平台过滤参数: {platform_filter}")
        logger.info(f"请求的完整参数: keywords={request.keywords}, platform={platform_filter}, timeRange={time_range}, category={getattr(request, 'category', None)}")
        result = analyzer.analyze_single_by_tier(request.keywords, current_user, platform_filter, time_range)
        
        # 记录使用量
        usage_tracker.increment_usage(current_user.id.value if hasattr(current_user.id, 'value') else current_user.id, "basic_analysis", 1)
        
        return {
            "status": "success",
            "data": result,
            "processing_time": round(time.time() - start_time, 2),
            "user_tier": current_user.subscription_tier.value,
            "credits_consumed": credits_required,
            "credits_remaining": current_user.credits_balance,
            "remaining_requests": usage_tracker.get_remaining_requests(current_user)
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.post("/batch", status_code=200)
def analyze_batch_keywords(
    request: Dict[str, List[List[str]]], 
    current_user: User = Depends(require_premium_subscription)
):
    """批量分析 - 需要高级订阅"""
    try:
        keywords_list = request.get("keywords_list", [])
        
        # 检查使用限制
        if not usage_tracker.check_rate_limit(current_user, "batch_analysis", len(keywords_list)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily usage limit exceeded"
            )
        
        # 检查批量大小限制
        if not check_subscription_limit(current_user, "batch_analysis", len(keywords_list)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Batch size exceeds subscription limit"
            )
        
        start_time = time.time()
        results = analyzer.analyze_batch(keywords_list)
        
        # 记录使用量
        usage_tracker.increment_usage(current_user.id.value if hasattr(current_user.id, 'value') else current_user.id, "batch_analysis", len(keywords_list))
        
        return {
            "status": "success",
            "data": results,
            "processing_time": round(time.time() - start_time, 2),
            "user_tier": current_user.subscription_tier.value,
            "remaining_requests": usage_tracker.get_remaining_requests(current_user)
        }
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

@router.get("/cache/stats")
def get_cache_stats(current_user: User = Depends(get_current_active_user)):
    """缓存统计 - 所有用户可访问"""
    with cache_lock:
        memory_cache_size = len(memory_cache)
        memory_cache_keys = list(memory_cache.keys())[:5]  # 显示前5个键
    
    redis_info = "不可用"
    redis_keys_count = 0
    if analyzer.redis_client:
        try:
            redis_keys_count = analyzer.redis_client.dbsize()
            redis_info = "可用"
        except Exception as e:
            redis_info = f"连接失败: {e}"
    
    return {
        "memory_cache": {
            "size": memory_cache_size,
            "sample_keys": [key[:8] + "..." for key in memory_cache_keys],
            "max_size": "无限制"
        },
        "redis_cache": {
            "status": redis_info,
            "keys_count": redis_keys_count
        },
        "thread_pool": {
            "max_workers": thread_pool._max_workers,
            "active_threads": threading.active_count()
        },
        "system": {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "uptime": "运行中"
        }
    }

@router.delete("/cache")
def clear_cache(current_user: User = Depends(require_premium_subscription)):
    """清空缓存 - 需要高级订阅"""
    try:
        # 清空内存缓存
        with cache_lock:
            memory_cache.clear()
        
        # 清空Redis缓存
        redis_cleared = 0
        if analyzer.redis_client:
            try:
                # 只删除分析相关的键
                keys = analyzer.redis_client.keys("analysis:*")
                if keys:
                    redis_cleared = analyzer.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis缓存清理失败: {e}")
        
        return {
            "status": "SUCCESS",
            "message": f"缓存已清空，Redis删除了 {redis_cleared} 个键",
            "cleared": {
                "memory_cache": True,
                "redis_cache": redis_cleared > 0
            }
        }
        
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

@router.post("/cache/clear", status_code=200)
def clear_cache_post(
    current_user: User = Depends(get_current_active_user)
):
    """清除分析缓存 - 所有用户都可以使用"""
    try:
        # 清除Redis缓存
        if analyzer.redis_client:
            analyzer.redis_client.flushdb()
            logger.info("Redis缓存已清除")
        
        # 清除内存缓存
        with cache_lock:
            memory_cache.clear()
            logger.info("内存缓存已清除")
        
        return {
            "status": "success",
            "message": "All caches cleared successfully"
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")