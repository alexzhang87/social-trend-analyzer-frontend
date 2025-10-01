#!/usr/bin/env python3
"""
Reddit 连接测试脚本
诊断Reddit API的网络连接问题
"""

import asyncio
import aiohttp
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RedditConnectionTester:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = "trend-analyzer:v1.0.0 (by /u/test_user)"
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'overall_status': 'unknown',
            'recommendations': []
        }
    
    def log_test(self, test_name: str, status: str, details: str = "", error: str = ""):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results['tests'].append(result)
        
        status_icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        if error:
            print(f"   错误: {error}")
    
    async def test_basic_connectivity(self):
        """测试基本网络连接"""
        print("\n=== 测试基本网络连接 ===")
        
        # 测试Reddit主站连接
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.reddit.com', timeout=10) as response:
                    if response.status == 200:
                        self.log_test("Reddit主站连接", "pass", f"状态码: {response.status}")
                    else:
                        self.log_test("Reddit主站连接", "fail", f"状态码: {response.status}")
        except Exception as e:
            self.log_test("Reddit主站连接", "fail", "", str(e))
        
        # 测试Reddit API端点连接
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.reddit.com/api/v1/me', timeout=10) as response:
                    self.log_test("Reddit API端点连接", "pass", f"状态码: {response.status}")
        except Exception as e:
            self.log_test("Reddit API端点连接", "fail", "", str(e))
    
    async def test_environment_variables(self):
        """测试环境变量配置"""
        print("\n=== 测试环境变量配置 ===")
        
        required_vars = {
            'REDDIT_CLIENT_ID': self.client_id,
            'REDDIT_CLIENT_SECRET': self.client_secret,
            'REDDIT_USERNAME': self.username,
            'REDDIT_PASSWORD': self.password
        }
        
        for var_name, var_value in required_vars.items():
            if var_value:
                # 隐藏敏感信息
                display_value = f"{var_value[:4]}***{var_value[-4:]}" if len(var_value) > 8 else "***"
                self.log_test(f"环境变量 {var_name}", "pass", f"已配置: {display_value}")
            else:
                self.log_test(f"环境变量 {var_name}", "fail", "未配置")
    
    async def test_reddit_authentication(self):
        """测试Reddit认证"""
        print("\n=== 测试Reddit认证 ===")
        
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            self.log_test("Reddit认证", "fail", "认证信息不完整")
            return
        
        import base64
        
        # 构建认证
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://www.reddit.com/api/v1/access_token', 
                                      headers=headers, data=data, timeout=15) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        if 'access_token' in token_data:
                            self.log_test("Reddit认证", "pass", f"获取到访问令牌，类型: {token_data.get('token_type', 'unknown')}")
                            return token_data['access_token']
                        else:
                            self.log_test("Reddit认证", "fail", "响应中没有访问令牌")
                    else:
                        error_text = await response.text()
                        self.log_test("Reddit认证", "fail", f"状态码: {response.status}", error_text)
        except Exception as e:
            self.log_test("Reddit认证", "fail", "", str(e))
        
        return None
    
    async def test_public_api_access(self):
        """测试公开API访问"""
        print("\n=== 测试公开API访问 ===")
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        # 测试获取热门帖子
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.reddit.com/r/popular.json?limit=5', 
                                     headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts_count = len(data.get('data', {}).get('children', []))
                        self.log_test("公开API访问", "pass", f"获取到 {posts_count} 条热门帖子")
                    else:
                        self.log_test("公开API访问", "fail", f"状态码: {response.status}")
        except Exception as e:
            self.log_test("公开API访问", "fail", "", str(e))
    
    async def test_search_functionality(self, access_token=None):
        """测试搜索功能"""
        print("\n=== 测试搜索功能 ===")
        
        # 测试公开搜索
        headers = {
            'User-Agent': self.user_agent
        }
        
        params = {
            'q': 'technology',
            'limit': 5,
            't': 'week',
            'sort': 'relevance'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.reddit.com/search.json', 
                                     headers=headers, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        results_count = len(data.get('data', {}).get('children', []))
                        self.log_test("公开搜索功能", "pass", f"搜索到 {results_count} 条结果")
                    else:
                        self.log_test("公开搜索功能", "fail", f"状态码: {response.status}")
        except Exception as e:
            self.log_test("公开搜索功能", "fail", "", str(e))
        
        # 如果有访问令牌，测试OAuth搜索
        if access_token:
            headers['Authorization'] = f'bearer {access_token}'
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://oauth.reddit.com/search', 
                                         headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            results_count = len(data.get('data', {}).get('children', []))
                            self.log_test("OAuth搜索功能", "pass", f"搜索到 {results_count} 条结果")
                        else:
                            self.log_test("OAuth搜索功能", "fail", f"状态码: {response.status}")
            except Exception as e:
                self.log_test("OAuth搜索功能", "fail", "", str(e))
    
    async def test_rate_limiting(self):
        """测试速率限制"""
        print("\n=== 测试速率限制 ===")
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        # 快速发送多个请求测试速率限制
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(3):  # 发送3个快速请求
                    task = session.get('https://www.reddit.com/r/popular.json?limit=1', 
                                     headers=headers, timeout=10)
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = 0
                rate_limited = False
                
                for i, response in enumerate(responses):
                    if isinstance(response, Exception):
                        continue
                    
                    async with response:
                        if response.status == 200:
                            success_count += 1
                        elif response.status == 429:
                            rate_limited = True
                
                if rate_limited:
                    self.log_test("速率限制检测", "pass", "检测到速率限制保护")
                else:
                    self.log_test("速率限制检测", "pass", f"成功请求: {success_count}/3")
                    
        except Exception as e:
            self.log_test("速率限制检测", "fail", "", str(e))
    
    def generate_recommendations(self):
        """生成修复建议"""
        print("\n=== 修复建议 ===")
        
        failed_tests = [test for test in self.test_results['tests'] if test['status'] == 'fail']
        
        if not failed_tests:
            self.test_results['overall_status'] = 'excellent'
            self.test_results['recommendations'].append("所有测试通过，Reddit连接正常")
            print("✅ 所有测试通过，Reddit连接正常")
            return
        
        self.test_results['overall_status'] = 'needs_attention'
        
        # 分析失败的测试并提供建议
        for test in failed_tests:
            if "环境变量" in test['test_name']:
                rec = f"请在.env文件中配置 {test['test_name'].split()[-1]}"
                self.test_results['recommendations'].append(rec)
                print(f"💡 {rec}")
            
            elif "网络连接" in test['test_name'] or "连接" in test['test_name']:
                rec = "检查网络连接和防火墙设置，确保可以访问Reddit"
                if rec not in self.test_results['recommendations']:
                    self.test_results['recommendations'].append(rec)
                    print(f"💡 {rec}")
            
            elif "认证" in test['test_name']:
                rec = "检查Reddit API凭证是否正确，确保用户名密码有效"
                self.test_results['recommendations'].append(rec)
                print(f"💡 {rec}")
        
        # 通用建议
        if len(failed_tests) > 2:
            rec = "考虑使用公开API作为备用方案，无需认证"
            self.test_results['recommendations'].append(rec)
            print(f"💡 {rec}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=== Reddit 连接诊断开始 ===")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行测试
        await self.test_environment_variables()
        await self.test_basic_connectivity()
        access_token = await self.test_reddit_authentication()
        await self.test_public_api_access()
        await self.test_search_functionality(access_token)
        await self.test_rate_limiting()
        
        # 生成建议
        self.generate_recommendations()
        
        # 保存测试报告
        report_path = f"reddit_connection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 测试完成 ===")
        print(f"总体状态: {self.test_results['overall_status']}")
        print(f"测试报告已保存: {report_path}")
        
        return self.test_results

async def main():
    tester = RedditConnectionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())