from fastapi import APIRouter, HTTPException, Query
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from app.services.google_trends_service import GoogleTrendsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()  # 移除重复的prefix

# Google Trends服务实例（延迟初始化）
google_trends_service = None

def get_google_trends_service():
    """获取Google Trends服务实例，支持延迟初始化"""
    global google_trends_service
    if google_trends_service is None:
        google_trends_service = GoogleTrendsService()
    return google_trends_service

@router.get("/trending-searches")
async def get_trending_searches(
    geo: str = Query(default="CN", description="地理位置代码，如CN(中国)、US(美国)")
) -> Dict[str, Any]:
    """获取热门搜索趋势
    
    Args:
        geo: 地理位置代码
        
    Returns:
        热门搜索列表
    """
    try:
        service = get_google_trends_service()
        result = service.get_trending_searches(geo=geo)
        
        return {
            "status": "success",
            "data": result,
            "total": len(result),
            "geo": geo
        }
        
    except Exception as e:
        logger.error(f"获取热门搜索趋势失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取热门搜索趋势失败: {str(e)}"
        )

@router.get("/interest-over-time")
async def get_interest_over_time(
    keywords: str = Query(..., description="关键词，多个关键词用逗号分隔，最多5个"),
    timeframe: str = Query(default="today 12-m", description="时间范围，如today 12-m, today 3-m, today 1-m"),
    geo: str = Query(default="CN", description="地理位置代码")
) -> Dict[str, Any]:
    """获取关键词的时间趋势数据
    
    Args:
        keywords: 关键词字符串，用逗号分隔
        timeframe: 时间范围
        geo: 地理位置代码
        
    Returns:
        时间趋势数据
    """
    try:
        # 解析关键词
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        if not keyword_list:
            raise HTTPException(
                status_code=400,
                detail="请提供至少一个关键词"
            )
        
        if len(keyword_list) > 5:
            raise HTTPException(
                status_code=400,
                detail="最多支持5个关键词"
            )
        
        service = get_google_trends_service()
        result = service.get_interest_over_time(
            keywords=keyword_list,
            timeframe=timeframe,
            geo=geo
        )
        
        if 'error' in result:
            raise HTTPException(
                status_code=500,
                detail=result['error']
            )
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取时间趋势数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取时间趋势数据失败: {str(e)}"
        )

@router.get("/interest-by-region")
async def get_interest_by_region(
    keywords: str = Query(..., description="关键词，多个关键词用逗号分隔，最多5个"),
    timeframe: str = Query(default="today 12-m", description="时间范围"),
    geo: str = Query(default="CN", description="地理位置代码")
) -> Dict[str, Any]:
    """获取关键词的地区分布数据
    
    Args:
        keywords: 关键词字符串，用逗号分隔
        timeframe: 时间范围
        geo: 地理位置代码
        
    Returns:
        地区分布数据
    """
    try:
        # 解析关键词
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        if not keyword_list:
            raise HTTPException(
                status_code=400,
                detail="请提供至少一个关键词"
            )
        
        if len(keyword_list) > 5:
            raise HTTPException(
                status_code=400,
                detail="最多支持5个关键词"
            )
        
        service = get_google_trends_service()
        result = service.get_interest_by_region(
            keywords=keyword_list,
            timeframe=timeframe,
            geo=geo
        )
        
        if 'error' in result:
            raise HTTPException(
                status_code=500,
                detail=result['error']
            )
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取地区分布数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取地区分布数据失败: {str(e)}"
        )

@router.get("/related-queries")
async def get_related_queries(
    keywords: str = Query(..., description="关键词，多个关键词用逗号分隔，最多5个"),
    timeframe: str = Query(default="today 12-m", description="时间范围"),
    geo: str = Query(default="CN", description="地理位置代码")
) -> Dict[str, Any]:
    """获取相关查询
    
    Args:
        keywords: 关键词字符串，用逗号分隔
        timeframe: 时间范围
        geo: 地理位置代码
        
    Returns:
        相关查询数据
    """
    try:
        # 解析关键词
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        if not keyword_list:
            raise HTTPException(
                status_code=400,
                detail="请提供至少一个关键词"
            )
        
        if len(keyword_list) > 5:
            raise HTTPException(
                status_code=400,
                detail="最多支持5个关键词"
            )
        
        service = get_google_trends_service()
        result = service.get_related_queries(
            keywords=keyword_list,
            timeframe=timeframe,
            geo=geo
        )
        
        if 'error' in result:
            raise HTTPException(
                status_code=500,
                detail=result['error']
            )
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取相关查询数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取相关查询数据失败: {str(e)}"
        )

@router.get("/status")
async def check_status() -> Dict[str, Any]:
    """检查Google Trends服务状态
    
    Returns:
        服务状态信息
    """
    try:
        service = get_google_trends_service()
        result = service.test_connection()
        
        return {
            "service": "Google Trends",
            "status": result['status'],
            "message": result['message'],
            "timestamp": result['timestamp'],
            "sample_data": result.get('sample_trends', [])
        }
        
    except Exception as e:
        logger.error(f"检查Google Trends服务状态失败: {e}")
        return {
            "service": "Google Trends",
            "status": "error",
            "message": f"服务状态检查失败: {str(e)}",
            "timestamp": None
        }

@router.get("/quick-test")
async def quick_test() -> Dict[str, Any]:
    """快速测试Google Trends功能
    
    Returns:
        测试结果
    """
    try:
        # 测试热门搜索
        service = get_google_trends_service()
        trending = service.get_trending_searches()
        
        # 测试时间趋势（使用简单关键词）
        interest_data = service.get_interest_over_time(
            keywords=["人工智能"],
            timeframe="today 3-m"
        )
        
        return {
            "status": "success",
            "message": "Google Trends功能测试完成",
            "tests": {
                "trending_searches": {
                    "status": "success" if trending else "failed",
                    "count": len(trending) if trending else 0,
                    "sample": trending[:3] if trending else []
                },
                "interest_over_time": {
                    "status": "success" if 'data' in interest_data else "failed",
                    "data_points": len(interest_data.get('data', [])),
                    "keywords": interest_data.get('keywords', [])
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Google Trends快速测试失败: {e}")
        return {
            "status": "error",
            "message": f"快速测试失败: {str(e)}",
            "tests": {}
        }