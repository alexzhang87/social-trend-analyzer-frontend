import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any
from ..core.config import settings
from ..utils.logger import logger

class CurlTwitterService:
    """
    直接使用 curl 命令调用 twitterapi.io 的服务
    这是为了解决 Python requests 库无法成功调用 API 的问题
    """
    
    def __init__(self):
        self.api_key = settings.TWITTERAPI_IO_KEY
        self.base_url = "https://api.twitterapi.io"
        logger.info("CurlTwitterService 已初始化")

    def _execute_curl(self, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """
        执行 curl 命令并返回 JSON 响应
        """
        # 构建 curl 命令
        cmd = [
            'curl',
            '-H', f'X-API-Key: {self.api_key}',
            '-H', 'User-Agent: curl/8.4.0',
            '-H', 'Accept: */*',
            '--silent',  # 静默模式，不显示进度
            '--show-error',  # 显示错误
            '--fail',  # 在 HTTP 错误时失败
        ]
        
        # 添加参数
        if params:
            for key, value in params.items():
                cmd.extend(['--data-urlencode', f'{key}={value}'])
            cmd.append('--get')  # 使用 GET 方法发送数据
        
        cmd.append(url)
        
        try:
            logger.info(f"执行 curl 命令: {' '.join(cmd[:3])} ... {url}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 成功，解析 JSON
                try:
                    data = json.loads(result.stdout)
                    logger.info("✅ curl 命令执行成功")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}")
                    logger.error(f"原始响应: {result.stdout}")
                    return {}
            else:
                # 失败
                logger.error(f"❌ curl 命令失败，返回码: {result.returncode}")
                logger.error(f"错误输出: {result.stderr}")
                logger.error(f"标准输出: {result.stdout}")
                return {}
                
        except subprocess.TimeoutExpired:
            logger.error("curl 命令超时")
            return {}
        except Exception as e:
            logger.error(f"执行 curl 命令时发生错误: {e}")
            return {}

    def search_users(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        搜索与查询相关的用户
        """
        logger.info(f"通过 curl 搜索用户: {query}")
        
        url = f"{self.base_url}/twitter/user/search"
        params = {'query': query}
        
        data = self._execute_curl(url, params)
        
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
        logger.info("测试 curl 连接...")
        
        url = f"{self.base_url}/twitter/user/search"
        params = {'query': 'test'}
        
        data = self._execute_curl(url, params)
        
        if data:
            logger.info("✅ curl 连接测试成功")
            return True
        else:
            logger.error("❌ curl 连接测试失败")
            return False