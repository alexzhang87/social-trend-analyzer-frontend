from fastapi import APIRouter, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import List, Dict, Any
from ..core.config import settings
from ..utils.logger import logger
from ..services.working_social_media_service import WorkingSocialMediaService
from ..services.llm_service import get_llm_provider
from ..data.models.database import RawPost

router = APIRouter()

# 初始化服务
social_media_service = WorkingSocialMediaService()
logger.info("使用可工作的社交媒体服务 (PowerShell curl)")

# 在应用启动时获取一次 LLM 提供者实例
try:
    llm_provider = get_llm_provider()
    logger.info("LLM 服务提供者已成功初始化。")
except ValueError as e:
    llm_provider = None
    logger.error(f"LLM 服务初始化失败: {e}")

@router.get("/", response_model=List[Dict[str, Any]])
async def get_trends(query: str = Query(..., min_length=1, max_length=50)):
    """
    获取并分析社交媒体趋势，返回一个包含洞察的单一分析结果。
    
    - **query**: 用于搜索的关键词。
    """
    logger.info(f"收到趋势分析请求，查询: '{query}'")
    
    if not llm_provider:
        raise HTTPException(status_code=503, detail="LLM服务未配置或初始化失败，无法处理分析。")

    try:
        # 1. 从不同平台获取原始数据
        twitter_posts = await social_media_service.get_twitter_posts(query)
        reddit_posts = await social_media_service.get_reddit_posts(query)
        
        all_posts = twitter_posts + reddit_posts
        if not all_posts:
            logger.warning(f"查询 '{query}' 未找到任何帖子。")
            return []

        unique_posts_map = {post['url']: post for post in all_posts}
        unique_posts = list(unique_posts_map.values())
        
        # 2. 将字典列表转换为 RawPost 对象列表以供 LLM 服务使用
        raw_posts_for_analysis = [
            RawPost(
                platform=post.get('platform', 'Unknown'),
                author=post.get('author', 'Unknown'),
                text=post.get('title', ''), # 将 'title' 映射到 'text'
                url=post.get('url', ''),
                likes=int(post.get('score', 0)), # 将 'score' 映射到 'likes'
                created_at=post.get('created_at')
            ) for post in unique_posts
        ]

        logger.info(f"为查询 '{query}' 收集了 {len(raw_posts_for_analysis)} 条独特的帖子，正在发送给 LLM 进行分析...")

        # 3. 在线程池中运行 LLM 分析，避免阻塞事件循环
        analysis_result = await run_in_threadpool(
            llm_provider.generate_insights_for_cluster, raw_posts_for_analysis
        )
        
        logger.info(f"已成功为查询 '{query}' 生成分析洞察。")
        
        # 4. API希望返回一个列表，所以我们将单个分析结果包装在列表中
        return [analysis_result]
        
    except Exception as e:
        logger.error(f"处理趋势分析请求时发生严重错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生内部错误: {str(e)}")
