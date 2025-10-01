"""
API安全中间件
提供速率限制、安全头设置、请求验证等安全功能
"""

import time
import logging
import json
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import re
import ipaddress
from urllib.parse import urlparse

from ..services.rate_limiter import rate_limiter
from ..core.auth import get_current_user_optional
from ..data.models.database import get_db

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # 安全配置
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        # 可疑模式
        self.suspicious_patterns = [
            r"<script[^>]*>.*?</script>",  # XSS
            r"javascript:",                # JavaScript协议
            r"on\w+\s*=",                 # 事件处理器
            r"union\s+select",            # SQL注入
            r"drop\s+table",              # SQL注入
            r"insert\s+into",             # SQL注入
            r"delete\s+from",             # SQL注入
            r"\.\./",                     # 路径遍历
            r"\.\.\\",                    # 路径遍历
            r"eval\s*\(",                 # 代码执行
            r"exec\s*\(",                 # 代码执行
        ]
        
        # 编译正则表达式
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        
        # 受保护的端点
        self.protected_endpoints = {
            "/api/auth/login": {"rate_limit": "auth"},
            "/api/auth/register": {"rate_limit": "auth"},
            "/api/upload": {"rate_limit": "upload"},
            "/api/analysis": {"rate_limit": "analysis"},
        }
        
        # 白名单IP（如果需要）
        self.whitelist_ips = set()
        
        # 黑名单IP
        self.blacklist_ips = set()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        start_time = time.time()
        
        try:
            # 获取客户端IP
            client_ip = self._get_client_ip(request)
            
            # 检查黑名单
            if client_ip in self.blacklist_ips:
                logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied"}
                )
            
            # 检查请求大小
            if not self._check_request_size(request):
                logger.warning(f"Request too large from {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request entity too large"}
                )
            
            # 检查可疑内容
            if await self._check_suspicious_content(request):
                logger.warning(f"Suspicious content detected from {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request content"}
                )
            
            # 速率限制检查
            rate_limit_result = await self._check_rate_limit(request, client_ip)
            if not rate_limit_result.allowed:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": rate_limit_result.retry_after
                    },
                    headers={
                        "Retry-After": str(rate_limit_result.retry_after),
                        "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                        "X-RateLimit-Reset": str(int(rate_limit_result.reset_time.timestamp()))
                    }
                )
            
            # 处理请求
            response = await call_next(request)
            
            # 添加安全头
            self._add_security_headers(response)
            
            # 添加速率限制头
            if rate_limit_result:
                response.headers["X-RateLimit-Remaining"] = str(rate_limit_result.remaining)
                response.headers["X-RateLimit-Reset"] = str(int(rate_limit_result.reset_time.timestamp()))
            
            # 记录请求
            process_time = time.time() - start_time
            logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s - {client_ip}")
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # 出错时返回通用错误，不暴露具体信息
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP（最原始的客户端IP）
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 回退到连接IP
        return request.client.host if request.client else "unknown"
    
    def _check_request_size(self, request: Request) -> bool:
        """检查请求大小"""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                # 限制请求大小为10MB
                return size <= 10 * 1024 * 1024
            except ValueError:
                return False
        return True
    
    async def _check_suspicious_content(self, request: Request) -> bool:
        """检查可疑内容"""
        try:
            # 检查URL路径
            path = str(request.url.path)
            for pattern in self.compiled_patterns:
                if pattern.search(path):
                    return True
            
            # 检查查询参数
            query = str(request.url.query)
            for pattern in self.compiled_patterns:
                if pattern.search(query):
                    return True
            
            # 检查请求头
            for header_name, header_value in request.headers.items():
                if header_name.lower() in ["user-agent", "referer", "x-forwarded-for"]:
                    for pattern in self.compiled_patterns:
                        if pattern.search(header_value):
                            return True
            
            # 检查请求体（仅对POST/PUT请求）
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    try:
                        body = await request.body()
                        if body:
                            body_str = body.decode("utf-8")
                            for pattern in self.compiled_patterns:
                                if pattern.search(body_str):
                                    return True
                    except Exception:
                        # 如果无法解析请求体，认为可疑
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking suspicious content: {e}")
            return True  # 出错时认为可疑
    
    async def _check_rate_limit(self, request: Request, client_ip: str):
        """检查速率限制"""
        try:
            # 跳过白名单IP
            if client_ip in self.whitelist_ips:
                return type('obj', (object,), {
                    'allowed': True, 
                    'remaining': 999, 
                    'reset_time': time.time() + 3600
                })()
            
            # 获取用户信息（如果已登录）
            user = None
            subscription_tier = "free"
            identifier = client_ip
            
            try:
                # 尝试获取当前用户
                from fastapi.security import HTTPAuthorizationCredentials
                auth_header = request.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    credentials = HTTPAuthorizationCredentials(
                        scheme="Bearer",
                        credentials=auth_header.split(" ")[1]
                    )
                    db = next(get_db())
                    user = await get_current_user_optional(credentials, db)
                    if user:
                        identifier = f"user_{user.id}"
                        subscription_tier = getattr(user, 'subscription_tier', 'free')
            except Exception:
                # 未登录用户使用IP作为标识
                pass
            
            # 确定端点类型
            endpoint_type = "global"
            path = request.url.path
            
            for protected_path, config in self.protected_endpoints.items():
                if path.startswith(protected_path):
                    endpoint_type = config.get("rate_limit", "global")
                    break
            
            # 检查速率限制
            return rate_limiter.check_rate_limit(
                identifier=identifier,
                endpoint=endpoint_type,
                subscription_tier=subscription_tier
            )
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # 出错时允许请求
            return type('obj', (object,), {
                'allowed': True, 
                'remaining': 0, 
                'reset_time': time.time() + 60
            })()
    
    def _add_security_headers(self, response: Response):
        """添加安全头"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # 添加CSP头
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
    
    def add_to_blacklist(self, ip: str):
        """添加IP到黑名单"""
        try:
            # 验证IP地址格式
            ipaddress.ip_address(ip)
            self.blacklist_ips.add(ip)
            logger.info(f"Added {ip} to blacklist")
        except ValueError:
            logger.error(f"Invalid IP address: {ip}")
    
    def remove_from_blacklist(self, ip: str):
        """从黑名单移除IP"""
        if ip in self.blacklist_ips:
            self.blacklist_ips.remove(ip)
            logger.info(f"Removed {ip} from blacklist")
    
    def add_to_whitelist(self, ip: str):
        """添加IP到白名单"""
        try:
            # 验证IP地址格式
            ipaddress.ip_address(ip)
            self.whitelist_ips.add(ip)
            logger.info(f"Added {ip} to whitelist")
        except ValueError:
            logger.error(f"Invalid IP address: {ip}")
    
    def get_security_stats(self) -> dict:
        """获取安全统计"""
        return {
            "blacklisted_ips": len(self.blacklist_ips),
            "whitelisted_ips": len(self.whitelist_ips),
            "protected_endpoints": len(self.protected_endpoints),
            "security_headers": len(self.security_headers)
        }

# 全局实例
security_middleware = SecurityMiddleware