from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

logger = logging.getLogger(__name__)

class TrendAnalyzerException(Exception):
    """基础异常类"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DataSourceException(TrendAnalyzerException):
    """数据源相关异常"""
    def __init__(self, message: str = "数据源访问失败"):
        super().__init__(message, 503)

class AuthenticationException(TrendAnalyzerException):
    """认证相关异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, 401)

class AuthorizationException(TrendAnalyzerException):
    """授权相关异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)

class RateLimitException(TrendAnalyzerException):
    """限流异常"""
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, 429)

class CacheException(TrendAnalyzerException):
    """缓存相关异常"""
    def __init__(self, message: str = "缓存操作失败"):
        super().__init__(message, 500)

# 全局异常处理器
async def trend_analyzer_exception_handler(request: Request, exc: TrendAnalyzerException):
    """处理自定义异常"""
    logger.error(f"TrendAnalyzer异常: {exc.message} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "type": exc.__class__.__name__,
            "path": str(request.url.path)
        }
    )

async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    """处理HTTP异常"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "type": "HTTPException",
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    logger.warning(f"请求验证失败: {exc.errors()} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "请求参数验证失败",
            "type": "ValidationError",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理异常: {str(exc)} - 路径: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误，请稍后重试",
            "type": "InternalServerError",
            "path": str(request.url.path)
        }
    )

# 错误响应格式化函数
def format_error_response(message: str, status_code: int = 500, details: dict = None):
    """格式化错误响应"""
    response = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    if details:
        response["details"] = details
    return response

# 成功响应格式化函数
def format_success_response(data: any = None, message: str = "操作成功"):
    """格式化成功响应"""
    response = {
        "error": False,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response