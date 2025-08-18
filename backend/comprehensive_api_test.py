import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.utils.logger import logger

class TwitterAPITester:
    def __init__(self):
        self.api_key = settings.TWITTERAPI_IO_KEY
        self.base_url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
        
    def create_session_with_retries(self):
        """创建带重试机制的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def test_method_1_basic_requests(self):
        """方法1: 基础 requests 调用"""
        logger.info("=== 测试方法1: 基础 requests ===")
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {
            'query': 'tesla',
            'queryType': 'Latest'
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法1失败: {e}")
            return False

    def test_method_2_full_browser_headers(self):
        """方法2: 完整浏览器请求头"""
        logger.info("=== 测试方法2: 完整浏览器请求头 ===")
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        params = {
            'query': 'tesla',
            'queryType': 'Latest'
        }
        
        try:
            session = self.create_session_with_retries()
            response = session.get(self.base_url, headers=headers, params=params, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法2失败: {e}")
            return False

    def test_method_3_with_referrer(self):
        """方法3: 添加 Referrer 头"""
        logger.info("=== 测试方法3: 添加 Referrer ===")
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://docs.twitterapi.io/',
            'Origin': 'https://docs.twitterapi.io'
        }
        
        params = {
            'query': 'tesla',
            'queryType': 'Latest'
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法3失败: {e}")
            return False

    def test_method_4_post_request(self):
        """方法4: 尝试 POST 请求"""
        logger.info("=== 测试方法4: POST 请求 ===")
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'query': 'tesla',
            'queryType': 'Latest'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法4失败: {e}")
            return False

    def test_method_5_different_endpoint(self):
        """方法5: 尝试不同的端点"""
        logger.info("=== 测试方法5: 不同端点 ===")
        
        # 尝试基础搜索端点
        alt_url = "https://api.twitterapi.io/twitter/tweet/search"
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {
            'query': 'tesla',
            'count': 10
        }
        
        try:
            response = requests.get(alt_url, headers=headers, params=params, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法5失败: {e}")
            return False

    def test_method_6_with_proxy(self):
        """方法6: 使用代理（如果配置了）"""
        logger.info("=== 测试方法6: 使用代理 ===")
        
        if not settings.USE_PROXY or not settings.HTTP_PROXY:
            logger.info("未配置代理，跳过此测试")
            return False
            
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {
            'query': 'tesla',
            'queryType': 'Latest'
        }
        
        proxies = {
            'http': settings.HTTP_PROXY,
            'https': settings.HTTPS_PROXY or settings.HTTP_PROXY
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, 
                                  proxies=proxies, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"方法6失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试方法"""
        logger.info("开始全面 API 测试...")
        logger.info(f"API Key: {self.api_key[:10]}...")
        
        methods = [
            self.test_method_1_basic_requests,
            self.test_method_2_full_browser_headers,
            self.test_method_3_with_referrer,
            self.test_method_4_post_request,
            self.test_method_5_different_endpoint,
            self.test_method_6_with_proxy
        ]
        
        successful_methods = []
        
        for i, method in enumerate(methods, 1):
            logger.info(f"\n{'='*50}")
            try:
                success = method()
                if success:
                    successful_methods.append(f"方法{i}")
                    logger.info(f"✅ 方法{i} 成功!")
                else:
                    logger.info(f"❌ 方法{i} 失败")
            except Exception as e:
                logger.error(f"❌ 方法{i} 异常: {e}")
            
            # 在测试之间稍作停顿
            time.sleep(2)
        
        logger.info(f"\n{'='*50}")
        logger.info("测试总结:")
        if successful_methods:
            logger.info(f"✅ 成功的方法: {', '.join(successful_methods)}")
        else:
            logger.info("❌ 所有方法都失败了")
            
        return len(successful_methods) > 0

if __name__ == "__main__":
    tester = TwitterAPITester()
    success = tester.run_all_tests()
    
    if not success:
        logger.info("\n🔧 建议的解决方案:")
        logger.info("1. 检查 API Key 是否有效")
        logger.info("2. 尝试使用 VPN 或代理")
        logger.info("3. 联系 twitterapi.io 支持")
        logger.info("4. 考虑部署到海外服务器")