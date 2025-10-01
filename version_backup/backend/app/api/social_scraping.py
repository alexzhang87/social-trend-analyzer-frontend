from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from ..services.snscrape_service import SNScrapeService
import logging

logger = logging.getLogger(__name__)

# 初始化SNScrape服务
snscrape_service = SNScrapeService()

router = APIRouter(prefix="/api/social-scraping", tags=["Social Media Scraping"])

# 请求模型
class TwitterSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    limit: int = Field(default=100, ge=1, le=500, description="返回结果数量限制")
    since_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    until_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    min_likes: Optional[int] = Field(None, description="最小点赞数")
    min_retweets: Optional[int] = Field(None, description="最小转发数")
    language: Optional[str] = Field(None, description="语言过滤")

class RedditSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="搜索关键词")
    subreddit: Optional[str] = Field(None, description="指定subreddit")
    limit: int = Field(default=100, ge=1, le=500, description="返回结果数量限制")
    sort: str = Field(default="hot", description="排序方式 (hot, new, top, rising, relevance)")

class CrossPlatformSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    platforms: List[str] = Field(default=["twitter", "reddit"], description="搜索平台")
    limit: int = Field(default=50, ge=1, le=200, description="每个平台的结果数量限制")

class UserContentRequest(BaseModel):
    platform: str = Field(..., description="平台名称 (twitter, reddit)")
    username: str = Field(..., description="用户名")
    limit: int = Field(default=50, ge=1, le=200, description="返回结果数量限制")

class InstagramHashtagRequest(BaseModel):
    hashtag: str = Field(..., description="hashtag名称（不包含#）")
    limit: int = Field(default=50, ge=1, le=200, description="返回结果数量限制")

class FacebookSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    limit: int = Field(default=50, ge=1, le=200, description="返回结果数量限制")
    post_type: str = Field(default="posts", description="搜索类型 (posts, groups, pages)")

class FacebookPageRequest(BaseModel):
    page_name: str = Field(..., description="Facebook页面名称或ID")
    limit: int = Field(default=50, ge=1, le=200, description="返回结果数量限制")

# 响应模型
class SocialMediaResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    total_count: int
    platform: str
    query_info: Dict[str, Any]

class CrossPlatformResponse(BaseModel):
    success: bool
    data: Dict[str, List[Dict[str, Any]]]
    total_count: Dict[str, int]
    query_info: Dict[str, Any]

class TrendingResponse(BaseModel):
    success: bool
    data: Dict[str, List[Dict[str, Any]]]
    platforms: List[str]
    timestamp: str

class ConnectionStatusResponse(BaseModel):
    success: bool
    platforms: Dict[str, bool]
    timestamp: str

@router.post("/twitter/search", response_model=SocialMediaResponse)
async def search_twitter(
    request: TwitterSearchRequest
):
    """搜索Twitter推文"""
    try:
        # 构建过滤器
        filters = {}
        if request.since_date:
            filters['since_date'] = request.since_date
        if request.until_date:
            filters['until_date'] = request.until_date
        if request.min_likes:
            filters['min_likes'] = request.min_likes
        if request.min_retweets:
            filters['min_retweets'] = request.min_retweets
        if request.language:
            filters['language'] = request.language
        
        # 执行搜索
        tweets = await snscrape_service.scrape_twitter_search(
            query=request.query,
            limit=request.limit,
            since_date=request.since_date,
            until_date=request.until_date
        )
        
        return SocialMediaResponse(
            success=True,
            data=tweets,
            total_count=len(tweets),
            platform="twitter",
            query_info={
                "query": request.query,
                "filters": filters,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"Twitter搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Twitter搜索失败: {str(e)}")

@router.get("/twitter/user/{username}", response_model=SocialMediaResponse)
async def get_twitter_user_tweets(
    username: str,
    limit: int = Query(default=50, ge=1, le=200, description="返回结果数量限制")
):
    """获取指定Twitter用户的推文"""
    try:
        tweets = await snscrape_service.scrape_twitter_user(
            username=username,
            limit=limit
        )
        
        return SocialMediaResponse(
            success=True,
            data=tweets,
            total_count=len(tweets),
            platform="twitter",
            query_info={
                "username": username,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"获取Twitter用户推文失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取Twitter用户推文失败: {str(e)}")

@router.post("/reddit/search", response_model=SocialMediaResponse)
async def search_reddit(
    request: RedditSearchRequest
):
    """搜索Reddit帖子"""
    try:
        posts = await snscrape_service.scrape_reddit_search(
            query=request.query,
            subreddit=request.subreddit,
            limit=request.limit,
            sort=request.sort
        )
        
        return SocialMediaResponse(
            success=True,
            data=posts,
            total_count=len(posts),
            platform="reddit",
            query_info={
                "query": request.query,
                "subreddit": request.subreddit,
                "sort": request.sort,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"Reddit搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reddit搜索失败: {str(e)}")

@router.get("/reddit/subreddit/{subreddit}", response_model=SocialMediaResponse)
async def get_subreddit_posts(
    subreddit: str,
    limit: int = Query(default=100, ge=1, le=500, description="返回结果数量限制"),
    sort: str = Query(default="hot", description="排序方式 (hot, new, top, rising)")
):
    """获取指定subreddit的帖子"""
    try:
        posts = await snscrape_service.scrape_reddit_subreddit(
            subreddit=subreddit,
            limit=limit,
            sort=sort
        )
        
        return SocialMediaResponse(
            success=True,
            data=posts,
            total_count=len(posts),
            platform="reddit",
            query_info={
                "subreddit": subreddit,
                "sort": sort,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"获取subreddit帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取subreddit帖子失败: {str(e)}")

@router.post("/search", response_model=CrossPlatformResponse)
async def cross_platform_search(
    request: CrossPlatformSearchRequest
):
    """跨平台社交媒体搜索"""
    try:
        results = await snscrape_service.scrape_cross_platform(
            query=request.query,
            platforms=request.platforms,
            limit_per_platform=request.limit
        )
        
        # 计算总数
        total_count = {}
        for platform in request.platforms:
            total_count[platform] = len(results.get(platform, []))
        
        return CrossPlatformResponse(
            success=True,
            data=results,
            total_count=total_count,
            query_info={
                "query": request.query,
                "platforms": request.platforms,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"跨平台搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"跨平台搜索失败: {str(e)}")

@router.get("/trending", response_model=TrendingResponse)
async def get_trending_topics(
    platform: str = Query(default="both", description="平台选择 (twitter, reddit, both)"),
    limit: int = Query(default=50, ge=1, le=200, description="每个平台的结果数量限制")
):
    """获取热门话题"""
    try:
        trending_data = await enhanced_social_service.get_trending_topics(
            platform=platform,
            limit=limit
        )
        
        platforms = []
        if platform == "both":
            platforms = ["twitter", "reddit"]
        else:
            platforms = [platform]
        
        return TrendingResponse(
            success=True,
            data=trending_data,
            platforms=platforms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"获取热门话题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")

@router.post("/user-content", response_model=SocialMediaResponse)
async def get_user_content(
    request: UserContentRequest
):
    """获取指定用户的内容"""
    try:
        content = await enhanced_social_service.get_user_content(
            platform=request.platform,
            username=request.username,
            count=request.limit
        )
        
        return SocialMediaResponse(
            success=True,
            data=content,
            total_count=len(content),
            platform=request.platform,
            query_info={
                "platform": request.platform,
                "username": request.username,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"获取用户内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户内容失败: {str(e)}")

@router.get("/status", response_model=ConnectionStatusResponse)
async def check_connection_status():
    """检查连接状态"""
    try:
        status = await enhanced_social_service.test_connection()
        
        return ConnectionStatusResponse(
            success=True,
            platforms=status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"检查连接状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查连接状态失败: {str(e)}")

@router.get("/stats")
async def get_platform_stats():
    """获取平台统计信息"""
    try:
        stats = await enhanced_social_service.get_platform_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取平台统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台统计信息失败: {str(e)}")

# 快速测试端点
@router.get("/test")
async def quick_test():
    """快速测试snscrape功能"""
    try:
        # 测试Twitter搜索
        twitter_test = await enhanced_social_service.get_tweets(
            query="python",
            count=5
        )
        
        # 测试Reddit搜索
        reddit_test = await enhanced_social_service.get_reddit_posts(
            query="python",
            count=5
        )
        
        return {
            "success": True,
            "message": "snscrape功能测试完成",
            "results": {
                "twitter": {
                    "count": len(twitter_test),
                    "sample": twitter_test[:2] if twitter_test else []
                },
                "reddit": {
                    "count": len(reddit_test),
                    "sample": reddit_test[:2] if reddit_test else []
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"快速测试失败: {str(e)}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.post("/instagram/hashtag", response_model=SocialMediaResponse)
async def search_instagram_hashtag(
    request: InstagramHashtagRequest
):
    """搜索Instagram hashtag相关内容"""
    try:
        posts = await snscrape_service.scrape_instagram_hashtag(
            hashtag=request.hashtag,
            limit=request.limit
        )
        
        return SocialMediaResponse(
            success=True,
            data=posts,
            total_count=len(posts),
            platform="instagram",
            query_info={
                "hashtag": request.hashtag,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"Instagram hashtag搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Instagram hashtag搜索失败: {str(e)}")

@router.post("/facebook/search", response_model=SocialMediaResponse)
async def search_facebook(
    request: FacebookSearchRequest
):
    """搜索Facebook帖子"""
    try:
        posts = await snscrape_service.scrape_facebook_search(
            query=request.query,
            limit=request.limit,
            post_type=request.post_type
        )
        
        return SocialMediaResponse(
            success=True,
            data=posts,
            total_count=len(posts),
            platform="facebook",
            query_info={
                "query": request.query,
                "post_type": request.post_type,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"Facebook搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Facebook搜索失败: {str(e)}")

@router.post("/facebook/page", response_model=SocialMediaResponse)
async def get_facebook_page_posts(
    request: FacebookPageRequest
):
    """获取指定Facebook页面的帖子"""
    try:
        posts = await snscrape_service.scrape_facebook_page(
            page_name=request.page_name,
            limit=request.limit
        )
        
        return SocialMediaResponse(
            success=True,
            data=posts,
            total_count=len(posts),
            platform="facebook_page",
            query_info={
                "page_name": request.page_name,
                "limit": request.limit
            }
        )
        
    except Exception as e:
        logger.error(f"获取Facebook页面帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取Facebook页面帖子失败: {str(e)}")
