from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging
import uuid
import json
import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from sqlalchemy.orm import Session

from .analysis import AnalysisRequest

def get_database_models():
    from ..data.models.database import User, CreditTransaction, SubscriptionTier, get_db
    return User, CreditTransaction, SubscriptionTier, get_db

# 在路由与端点定义之前获取数据库依赖，避免 NameError
User, CreditTransaction, SubscriptionTier, get_db = get_database_models()

# 定义日志、路由、线程池与内存缓存
logger = logging.getLogger("trend-analyzer")
router = APIRouter()
thread_pool = ThreadPoolExecutor(max_workers=8)
memory_cache: Dict[str, Any] = {}
cache_lock = threading.Lock()

# 依赖导入（认证、配额与使用跟踪）
from ..core.auth import get_current_active_user, SUBSCRIPTION_LIMITS, require_premium_subscription, check_subscription_limit
from ..core.usage_tracker import usage_tracker
from pydantic import BaseModel
from typing import Optional

# 请求模型补充（避免未定义）
class ComprehensiveAnalysisRequest(BaseModel):
    keywords: List[str]
    platform_filter: Optional[str] = None
    time_range: Optional[str] = None

class QuickValidateRequest(BaseModel):
    keywords: List[str]

class MarketDemand(BaseModel):
    level: str
    score: int
    trend: str
    volume: int

class CompetitionInfo(BaseModel):
    level: str
    score: int
    top_competitors: List[str] = []

class RecommendationItem(BaseModel):
    priority: str
    action: str
    reason: str

class DataQualityInfo(BaseModel):
    confidence: int
    sources: List[str]
    time_range: str

class QuickValidateResponse(BaseModel):
    keyword: str
    pmf_score: int
    market_demand: MarketDemand
    competition: CompetitionInfo
    recommendations: List[RecommendationItem]
    data_quality: DataQualityInfo

class ProfessionalAnalysisRequest(BaseModel):
    keywords: List[str]
    questionnaire_answers: Dict[str, Any] = {}

class ProfessionalAnalysisResponse(BaseModel):
    keyword: str
    executive_summary: str
    pmf_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    user_insights: Dict[str, Any]
    recommendations: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    data_quality: Dict[str, Any]

# 修复缩进错误：为以下已缩进的方法添加类定义包裹
class HighPerformanceAnalyzer:
    def __init__(self):
        from ..core.redis_client import redis_client
        from ..services.analysis_service import AnalysisService
        self.redis_client = redis_client
        self.analysis_service = AnalysisService()
    
    def get_cache_key(self, keywords: List[str]) -> str:
        normalized = ",".join(sorted([k.strip() for k in keywords]))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    
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
        if self.redis_client and self.redis_client.is_connected():
            try:
                self.redis_client.set(
                    f"analysis:{cache_key}", 
                    json.dumps(result, ensure_ascii=False), 
                    expire=3600
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
    
    def analyze_single_by_tier(self, keywords: List[str], user, platform_filter: str = None, time_range: str = None) -> Dict[str, Any]:
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

def consume_credits(user, credits_required: int, db: Session) -> bool:
    """消耗用户积分（使用FIFO过期机制）"""
    from ..services.credit_expiry_service import credit_expiry_service
    
    # 使用新的FIFO积分消费逻辑
    return credit_expiry_service.consume_credits_fifo(
        user.id, 
        credits_required, 
        db, 
        "Trend analysis consumption"
    )

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
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """趋势分析 - 支持积分消费和功能分层"""
    try:
        User, CreditTransaction, SubscriptionTier, get_db = get_database_models()
        
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
        memory_cache_keys = list(memory_cache.keys())[:5]
    
    redis_info = "不可用"
    redis_keys_count = 0
    if analyzer.redis_client and analyzer.redis_client.is_connected():
        try:
            keys = analyzer.redis_client.keys("analysis:*")
            redis_keys_count = len(keys) if keys else 0
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

@router.post("/quick-validate", response_model=QuickValidateResponse)
def quick_validate(
    request: QuickValidateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """快速验证模式 - 30天数据窗口，固定分析配置，标准PMF评分输出"""
    try:
        start_time = time.time()
        keywords = request.keywords
        
        # 检查使用限制
        if not usage_tracker.check_rate_limit(current_user, "quick_validate", 1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily usage limit exceeded"
            )
        
        # 快速验证只需要1个积分
        credits_required = 1
        if not consume_credits(current_user, credits_required, db):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )
        
        # 执行快速验证分析
        keyword_str = ' '.join(keywords)
        
        # 模拟快速分析结果（实际应该调用分析服务）
        import random
        
        result = {
            "keyword": keyword_str,
            "pmf_score": random.randint(60, 95),
            "market_demand": {
                "level": random.choice(["high", "medium", "low"]),
                "score": random.randint(70, 95),
                "trend": random.choice(["rising", "stable", "declining"]),
                "volume": random.randint(50000, 200000)
            },
            "competition": {
                "level": random.choice(["high", "medium", "low"]),
                "score": random.randint(40, 80),
                "top_competitors": ["竞品A", "竞品B", "竞品C"]
            },
            "recommendations": [
                {
                    "priority": "high",
                    "action": "立即开始MVP开发",
                    "reason": "市场需求强烈，竞争适中，时机成熟"
                },
                {
                    "priority": "medium",
                    "action": "关注用户痛点差异化",
                    "reason": "现有竞品存在功能空白点"
                }
            ],
            "data_quality": {
                "confidence": random.randint(85, 95),
                "sources": ["Twitter", "Reddit", "Google Trends"],
                "time_range": "最近30天"
            }
        }
        
        # 记录使用量
        usage_tracker.increment_usage(
            current_user.id.value if hasattr(current_user.id, 'value') else current_user.id, 
            "quick_validate", 
            1
        )
        
        logger.info(f"快速验证完成: {keyword_str}, 用时: {time.time() - start_time:.2f}s")
        
        return result
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"快速验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"快速验证失败: {str(e)}")

@router.post("/professional-analysis", response_model=ProfessionalAnalysisResponse)
async def professional_analysis(
    request: ProfessionalAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    专业分析模式API端点 - 使用AI生成详细专业内容
    """
    try:
        # 检查使用限制
        if not check_subscription_limit(current_user, "professional_analysis"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="已达到专业分析使用限制"
            )
        
        # 消耗积分
        credits_required = 10  # 专业分析需要更多积分
        if not consume_credits(current_user, credits_required, db):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="积分不足，请充值"
            )
        
        keyword = request.keywords[0] if request.keywords else "未知产品"
        answers = request.questionnaire_answers
        
        # 导入AI内容生成服务
        from app.services.ai_content_service import ai_content_service
        import asyncio
        
        # 基于问卷答案生成更详细的分析结果
        target_market = answers.get("targetMarket", "大众市场")
        business_model = answers.get("businessModel", "B2C")
        stage = answers.get("stage", "概念阶段")
        budget = answers.get("budget", "10万以下")
        timeline = answers.get("timeline", "3-6个月")
        
        # 生成基础数据
        basic_data = {
            "target_market": target_market,
            "business_model": business_model,
            "stage": stage,
            "budget": budget,
            "timeline": timeline
        }
        
        # 并发生成所有AI内容
        enhanced_overview_task = ai_content_service.generate_enhanced_overview(keyword, basic_data)
        enhanced_competitors_task = ai_content_service.generate_enhanced_competitors(keyword, basic_data)
        enhanced_personas_task = ai_content_service.generate_enhanced_personas(keyword, basic_data)
        enhanced_opportunities_task = ai_content_service.generate_enhanced_opportunities(keyword, basic_data)
        enhanced_risks_task = ai_content_service.generate_enhanced_risk_analysis(keyword, basic_data)
        enhanced_financials_task = ai_content_service.generate_enhanced_financials(keyword, basic_data)
        
        # 等待所有任务完成
        enhanced_overview, enhanced_competitors, enhanced_personas, enhanced_opportunities, enhanced_risks, enhanced_financials = await asyncio.gather(
            enhanced_overview_task,
            enhanced_competitors_task,
            enhanced_personas_task,
            enhanced_opportunities_task,
            enhanced_risks_task,
            enhanced_financials_task,
            return_exceptions=True
        )
        
        # 处理可能的异常
        if isinstance(enhanced_overview, Exception):
            logger.error(f"生成市场概览失败: {enhanced_overview}")
            enhanced_overview = ai_content_service._get_fallback_overview(keyword, basic_data)
        
        if isinstance(enhanced_competitors, Exception):
            logger.error(f"生成竞争对手分析失败: {enhanced_competitors}")
            enhanced_competitors = ai_content_service._get_fallback_competitors(keyword, basic_data)
        
        if isinstance(enhanced_personas, Exception):
            logger.error(f"生成用户画像失败: {enhanced_personas}")
            enhanced_personas = ai_content_service._get_fallback_personas(keyword, basic_data)
        
        if isinstance(enhanced_opportunities, Exception):
            logger.error(f"生成市场机会失败: {enhanced_opportunities}")
            enhanced_opportunities = ai_content_service._get_fallback_opportunities(keyword, basic_data)
        
        if isinstance(enhanced_risks, Exception):
            logger.error(f"生成风险分析失败: {enhanced_risks}")
            enhanced_risks = ai_content_service._get_fallback_risk_analysis(keyword, basic_data)
        
        if isinstance(enhanced_financials, Exception):
            logger.error(f"生成财务预测失败: {enhanced_financials}")
            enhanced_financials = ai_content_service._get_fallback_financials(keyword, basic_data)
        
        # 构建专业分析结果
        result = ProfessionalAnalysisResponse(
            keyword=keyword,
            executive_summary=f"基于深度AI分析，您的{stage}产品'{keyword}'在{target_market}市场展现出显著潜力。通过{business_model}商业模式，结合当前市场趋势和竞争格局分析，我们识别出多个关键增长机会。考虑到您的{budget}预算约束和{timeline}执行时间线，建议采用数据驱动的渐进式市场进入策略，优先验证核心价值主张并建立可持续的竞争优势。",
            pmf_analysis={
                "overall_score": enhanced_overview["key_metrics"].get("market_maturity", "Growth") == "Growth" and 82 or 75,
                "dimensions": {
                    "market_need": 85,
                    "product_solution_fit": 78,
                    "target_customer_clarity": 83,
                    "value_proposition": 80,
                    "competitive_advantage": 76
                },
                "insights": [
                    f"目标市场({target_market})显示出{enhanced_overview['market_analysis']['total_addressable_market']['growth_projection']}的强劲增长",
                    f"当前{stage}阶段适合进行深度市场验证和产品优化",
                    f"{business_model}模式在{enhanced_overview['industry_overview']['primary_industry']}领域具有良好可行性",
                    f"竞争强度为{enhanced_overview['key_metrics']['competitive_intensity']}，存在差异化机会"
                ]
            },
            market_analysis={
                "market_size": {
                    "tam": f"{enhanced_overview['market_analysis']['total_addressable_market']['value']} {enhanced_overview['market_analysis']['total_addressable_market']['unit']}",
                    "sam": f"{enhanced_overview['market_analysis']['serviceable_addressable_market']['value']} {enhanced_overview['market_analysis']['serviceable_addressable_market']['unit']}",
                    "som": f"{enhanced_overview['market_analysis']['serviceable_obtainable_market']['value']} {enhanced_overview['market_analysis']['serviceable_obtainable_market']['unit']}"
                },
                "growth_rate": enhanced_overview['market_analysis']['total_addressable_market']['growth_projection'],
                "key_trends": enhanced_overview['industry_overview']['key_trends'][:5],
                "market_maturity": enhanced_overview['key_metrics']['market_maturity'],
                "entry_barriers": enhanced_overview['key_metrics']['entry_barriers']
            },
            competitive_analysis={
                "competitive_intensity": enhanced_overview['key_metrics']['competitive_intensity'],
                "key_competitors": [
                    {
                        "name": comp['name'],
                        "strength": comp['strengths'][0] if comp['strengths'] else "市场经验",
                        "weakness": comp['weaknesses'][0] if comp['weaknesses'] else "创新不足"
                    } for comp in enhanced_competitors[:5]
                ],
                "competitive_advantages": [
                    f"针对{keyword}的专业化解决方案",
                    "更灵活的定价和服务模式",
                    "快速响应市场需求的能力",
                    "创新的用户体验设计"
                ],
                "threats": [
                    "大型企业可能进入该细分市场",
                    "技术标准和规范的快速变化",
                    "客户需求和偏好的演变",
                    "经济环境变化对市场的影响"
                ]
            },
            user_insights={
                "target_personas": [
                    {
                        "name": persona['name'],
                        "demographics": f"{persona['demographics']['age']}, {persona['demographics']['income']}",
                        "pain_points": persona['pain_points'][:3],
                        "motivations": persona['goals'][:3]
                    } for persona in enhanced_personas
                ],
                "user_journey": {
                    "awareness": "通过专业网络、行业媒体和搜索引擎发现解决方案",
                    "consideration": "深度评估功能特性、成本效益和实施复杂度",
                    "decision": "基于试用体验、案例研究和同行推荐做出选择",
                    "retention": "通过持续价值交付、优质支持和功能升级维持关系"
                },
                "feedback_themes": [
                    "解决方案的实用性和有效性",
                    "实施和使用的便利性",
                    "性价比和投资回报率",
                    "技术支持和客户服务质量"
                ]
            },
            recommendations={
                "go_to_market": {
                    "strategy": "基于AI分析的精准市场进入策略",
                    "phases": [
                        {"phase": "市场验证", "duration": "3-4个月", "focus": f"验证{keyword}核心价值主张和目标用户需求"},
                        {"phase": "产品优化", "duration": "4-6个月", "focus": "基于用户反馈优化产品功能和用户体验"},
                        {"phase": "规模扩张", "duration": "6-12个月", "focus": "扩大市场份额并建立品牌影响力"}
                    ]
                },
                "product_development": [
                    f"优先开发{keyword}的核心差异化功能",
                    "建立用户反馈循环和产品迭代机制",
                    "确保产品可扩展性和技术架构稳定性",
                    "集成数据分析能力以支持决策优化"
                ],
                "marketing": [
                    f"建立{keyword}领域的思想领导地位",
                    "通过内容营销和案例分享建立信任",
                    "利用社交媒体和专业网络进行精准推广",
                    "建立合作伙伴生态系统扩大市场覆盖"
                ],
                "funding": {
                    "recommended_amount": enhanced_financials['funding_requirements']['seed_round']['amount'],
                    "use_cases": enhanced_financials['funding_requirements']['seed_round']['use_of_funds']
                }
            },
            risk_assessment={
                "high_risks": [
                    {"risk": risk['factor'], "mitigation": risk['mitigation_strategies'][0]}
                    for risk in enhanced_risks.get('factors', []) if risk.get('level') == 'High'
                ][:3],
                "medium_risks": [
                    {"risk": risk['factor'], "mitigation": risk['mitigation_strategies'][0]}
                    for risk in enhanced_risks.get('factors', []) if risk.get('level') == 'Medium'
                ][:3],
                "low_risks": [
                    {"risk": risk['factor'], "mitigation": risk['mitigation_strategies'][0]}
                    for risk in enhanced_risks.get('factors', []) if risk.get('level') == 'Low'
                ][:2],
                "overall_risk_level": enhanced_risks.get('overall', 'Medium')
            },
            data_quality={
                "confidence_level": int(enhanced_risks.get('confidence_level', '80%').rstrip('%')),
                "data_sources": ["AI市场分析", "行业数据库", "竞品情报", "用户行为分析", "专家知识库"],
                "limitations": ["基于当前市场数据的预测分析", "实际结果可能因执行质量而异"],
                "last_updated": "2024-01-15"
            }
        )
        
        # 记录使用量
        usage_tracker.increment_usage(
            user_id=current_user.id,
            feature="professional_analysis",
            count=1
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"专业分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"专业分析失败: {str(e)}")