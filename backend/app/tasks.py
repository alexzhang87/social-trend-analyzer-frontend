"""
Celery tasks for trend analysis processing - 完全同步版本
"""
import json
import redis
from typing import List
from .worker import celery_app
from .services.analysis_service import AnalysisService
from .utils.logger import get_logger

logger = get_logger(__name__)

# Redis客户端用于缓存
redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)

@celery_app.task(name="analyze_trends_task", bind=True)
def analyze_trends_task(self, keywords: List[str]):
    """
    同步分析趋势任务 - 完全重写版本
    """
    print(f"---!!! 诊断: analyze_trends_task 已被当前Worker接收，关键词: {keywords} !!!---")
    
    try:
        # 1. 初始化服务
        self.update_state(state='PROGRESS', meta={'status': '分析任务已启动...', 'progress': 5})
        analysis_service = AnalysisService()
        
        # 2. 检查缓存
        cache_key = f"analysis:{json.dumps(sorted(keywords))}"
        logger.info(f"检查缓存键: {cache_key}")
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info("缓存命中，直接返回结果")
            self.update_state(state='PROGRESS', meta={'status': '在缓存中找到结果', 'progress': 100})
            return json.loads(cached_result)

        # 3. 缓存未命中，开始执行分析
        logger.info("缓存未命中，开始执行分析")
        self.update_state(state='PROGRESS', meta={'status': '正在分析数据...', 'progress': 20})
        
        # 4. 直接调用同步的分析方法
        result = analysis_service.analyze(keywords)
        
        # 5. 缓存并返回结果
        self.update_state(state='PROGRESS', meta={'status': '分析完成，正在保存结果...', 'progress': 95})
        redis_client.set(cache_key, json.dumps(result), ex=86400)  # 缓存24小时
        logger.info("分析完成，结果已缓存")
        
        self.update_state(state='SUCCESS', meta={'status': '分析完成', 'progress': 100})
        print(f"---!!! 任务成功完成: {keywords} !!!---")
        return result
        
    except Exception as exc:
        # 增强的错误处理
        import traceback
        error_details = traceback.format_exc()
        print(f"---!!! TASK FAILED: {keywords} !!!---")
        print(f"错误详情: {error_details}")
        print("---!!! END OF EXCEPTION !!!---")
    
        logger.error(f"任务执行失败: {str(exc)}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'status': f'分析失败: {str(exc)}', 'progress': 0, 'error': str(exc)}
        )
        raise exc
