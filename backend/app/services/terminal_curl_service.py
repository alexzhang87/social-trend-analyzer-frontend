import subprocess
import json
import shlex
from datetime import datetime
from typing import List, Dict, Any
from ..core.config import settings
from ..utils.logger import logger

class TerminalCurlService:
    """
    完全模拟终端环境的 curl 服务
    解决 Python subprocess 与直接终端调用的差异
    """
    
    def __init__(self):
        self.api_key = settings.TWITTERAPI_IO_KEY
        self.base_url = "https://api.twitterapi.io"
        logger.info("TerminalCurlService 已初始化")

    def _execute_terminal_curl(self, url: str) -> Dict[str, Any]:
        """
        完全模拟终端环境执行 curl
        """
        # 构建完全相同的 curl 命令
        cmd_str = f'curl -H "X-API-Key: {self.api_key}" "{url}"'
        
        try:
            logger.info(f"执行终端 curl 命令: {cmd_str}")
            
            # 使用 shell=True 来完全模拟终端环境
            result = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            logger.info(f"curl 返回码: {result.returncode}")
            logger.info(f"curl 原始响应: {result.stdout[:200]}...")
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    logger.info("✅ 终端 curl 命令执行成功")
                    logger.info(f"响应数据键: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}")
                    logger.error(f"原始响应: {result.stdout}")
                    return {}
            else:
                logger.error(f"curl 命令失败，返回码: {result.returncode}")
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
        logger.info(f"搜索用户: {query}")
        
        # 构建完整的 URL
        url = f"{self.base_url}/twitter/user/search?query={query}"
        
        data = self._execute_terminal_curl(url)
        
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
        logger.info("测试终端 curl 连接...")
        
        url = f"{self.base_url}/twitter/user/search?query=test"
        data = self._execute_terminal_curl(url)
        
        if data and 'users' in data:
            logger.info("✅ 终端 curl 连接测试成功")
            return True
        else:
            logger.error("❌ 终端 curl 连接测试失败")
            return False