import subprocess
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from ..core.config import settings
from ..utils.logger import logger

class ProxyCurlTwitterService:
    """
    支持代理的 curl Twitter 服务
    专门为中国用户使用 VPN 的情况设计
    """
    
    def __init__(self):
        self.api_key = settings.TWITTERAPI_IO_KEY
        self.base_url = "https://api.twitterapi.io"
        
        # 从环境变量读取代理设置
        self.http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        self.https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        
        logger.info("ProxyCurlTwitterService 已初始化")
        if self.http_proxy or self.https_proxy:
            logger.info(f"检测到代理设置: HTTP={self.http_proxy}, HTTPS={self.https_proxy}")
        else:
            logger.info("未检测到代理设置，将尝试直接连接")

    def _execute_curl_with_proxy(self, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """
        使用代理执行 curl 命令
        """
        # 构建完整的 URL
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_str}"
        else:
            full_url = url
        
        # 构建 curl 命令
        cmd = [
            'curl',
            '-H', f'X-API-Key: {self.api_key}',
            '-H', 'User-Agent: curl/8.4.0',
            '-H', 'Accept: */*',
            '--silent',
            '--show-error',
            '--max-time', '30',  # 30秒超时
        ]
        
        # 添加代理设置
        if self.https_proxy:
            cmd.extend(['--proxy', self.https_proxy])
            logger.info(f"使用 HTTPS 代理: {self.https_proxy}")
        elif self.http_proxy:
            cmd.extend(['--proxy', self.http_proxy])
            logger.info(f"使用 HTTP 代理: {self.http_proxy}")
        
        cmd.append(full_url)
        
        try:
            logger.info(f"执行代理 curl 命令: {full_url}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=35
            )
            
            logger.info(f"curl 返回码: {result.returncode}")
            
            if result.returncode == 0:
                # 成功，解析 JSON
                try:
                    if result.stdout.strip():
                        logger.info(f"curl 原始响应: {result.stdout[:200]}...")
                        data = json.loads(result.stdout)
                        logger.info("✅ 代理 curl 命令执行成功")
                        logger.info(f"响应数据键: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
                        return data
                    else:
                        logger.warning("curl 返回空响应")
                        return {}
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}")
                    logger.error(f"原始响应: {result.stdout[:500]}...")
                    return {}
            else:
                # 失败，但仍然尝试解析响应
                logger.warning(f"curl 返回非零状态码: {result.returncode}")
                logger.warning(f"错误输出: {result.stderr}")
                
                # 有时候即使返回码非零，stdout 中仍有有效数据
                if result.stdout.strip():
                    try:
                        data = json.loads(result.stdout)
                        logger.info("✅ 尽管返回码非零，但成功解析了响应数据")
                        return data
                    except json.JSONDecodeError:
                        pass
                
                logger.error(f"标准输出: {result.stdout}")
                return {}
                
        except subprocess.TimeoutExpired:
            logger.error("curl 命令超时")
            return {}
        except Exception as e:
            logger.error(f"执行 curl 命令时发生错误: {e}")
            return {}

    def _execute_curl_direct(self, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """
        直接执行 curl 命令（不使用代理）
        """
        # 构建完整的 URL
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_str}"
        else:
            full_url = url
        
        # 构建 curl 命令
        cmd = [
            'curl',
            '-H', f'X-API-Key: {self.api_key}',
            full_url
        ]
        
        try:
            logger.info(f"执行直接 curl 命令: {full_url}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    logger.info("✅ 直接 curl 命令执行成功")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}")
                    return {}
            else:
                logger.warning(f"直接 curl 失败: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"执行直接 curl 命令时发生错误: {e}")
            return {}

    def search_users(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        搜索与查询相关的用户
        """
        logger.info(f"搜索用户: {query}")
        
        url = f"{self.base_url}/twitter/user/search"
        params = {'query': query}
        
        # 首先尝试使用代理
        data = self._execute_curl_with_proxy(url, params)
        
        # 如果代理失败，尝试直接连接
        if not data:
            logger.info("代理连接失败，尝试直接连接...")
            data = self._execute_curl_direct(url, params)
        
        if data and 'users' in data:
            users = data['users']
            logger.info(f"✅ 成功找到 {len(users)} 个相关用户")
            return users[:count]
        else:
            logger.warning("❌ 未找到用户数据")
            return []

    def get_trending_content_via_users(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        通过搜索相关用户来获取趋势内容
        """
        logger.info(f"通过用户搜索获取 '{query}' 的趋势内容")
        
        # 1. 搜索相关用户
        users = self.search_users(query, count=10)
        
        if not users:
            logger.warning("未找到相关用户")
            return []
        
        # 2. 为每个用户创建趋势内容
        trending_content = []
        
        for user in users:
            # 创建基于用户信息的内容条目
            content_item = {
                "platform": "twitter",
                "author": user.get("screen_name", user.get("username", "unknown")),
                "text": f"来自 @{user.get('screen_name', 'unknown')} 的内容: {user.get('description', '暂无描述')}",
                "url": f"https://twitter.com/{user.get('screen_name', 'unknown')}",
                "likes": user.get("followers_count", 0) // 100,  # 模拟点赞数
                "created_at": datetime.now().isoformat(),
                "user_info": {
                    "followers": user.get("followers_count", 0),
                    "verified": user.get("verified", False),
                    "blue_verified": user.get("isBlueVerified", False)
                }
            }
            trending_content.append(content_item)
        
        logger.info(f"✅ 生成了 {len(trending_content)} 条基于用户的趋势内容")
        return trending_content[:limit]

    def test_connection(self) -> bool:
        """
        测试与 API 的连接
        """
        logger.info("测试代理连接...")
        
        url = f"{self.base_url}/twitter/user/search"
        params = {'query': 'test'}
        
        # 测试代理连接
        data = self._execute_curl_with_proxy(url, params)
        
        if data:
            logger.info("✅ 代理连接测试成功")
            return True
        
        # 测试直接连接
        logger.info("代理连接失败，测试直接连接...")
        data = self._execute_curl_direct(url, params)
        
        if data:
            logger.info("✅ 直接连接测试成功")
            return True
        else:
            logger.error("❌ 所有连接方式都失败")
            return False

    def detect_proxy_settings(self) -> Dict[str, str]:
        """
        检测当前的代理设置
        """
        proxy_info = {
            'HTTP_PROXY': os.getenv('HTTP_PROXY', '未设置'),
            'HTTPS_PROXY': os.getenv('HTTPS_PROXY', '未设置'),
            'http_proxy': os.getenv('http_proxy', '未设置'),
            'https_proxy': os.getenv('https_proxy', '未设置'),
        }
        
        logger.info("当前代理设置:")
        for key, value in proxy_info.items():
            logger.info(f"  {key}: {value}")
        
        return proxy_info