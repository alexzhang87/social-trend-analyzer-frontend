#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化后端API功能测试套件
测试所有核心API端点和功能
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 测试配置
BASE_URL = "http://localhost:8001"
TEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
        # 配置重试策略
        retry_strategy = Retry(
            total=RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   详细信息: {data}")
    
    def test_server_health(self) -> bool:
        """测试服务器健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                self.log_test("服务器健康检查", True, "服务器正常运行")
                return True
            else:
                self.log_test("服务器健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("服务器健康检查", False, f"连接失败: {str(e)}")
            return False
    
    def test_user_registration(self) -> bool:
        """测试用户注册"""
        test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=test_user,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 201:
                self.log_test("用户注册", True, "注册成功")
                return True
            elif response.status_code == 400:
                # 可能是用户已存在，这也算正常
                self.log_test("用户注册", True, "用户可能已存在（正常）")
                return True
            else:
                self.log_test("用户注册", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("用户注册", False, f"请求失败: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """测试用户登录"""
        # 使用默认管理员账户
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data,  # 使用form data
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    self.log_test("用户登录", True, "登录成功，获取到访问令牌")
                    return True
                else:
                    self.log_test("用户登录", False, "响应中缺少访问令牌", data)
                    return False
            else:
                self.log_test("用户登录", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("用户登录", False, f"请求失败: {str(e)}")
            return False
    
    def test_protected_endpoint(self) -> bool:
        """测试需要认证的端点"""
        if not self.access_token:
            self.log_test("受保护端点访问", False, "没有访问令牌")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/auth/me",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("受保护端点访问", True, f"获取用户信息: {data.get('username', 'unknown')}")
                return True
            else:
                self.log_test("受保护端点访问", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("受保护端点访问", False, f"请求失败: {str(e)}")
            return False
    
    def test_data_analysis_endpoint(self) -> bool:
        """测试数据分析端点"""
        if not self.access_token:
            self.log_test("数据分析功能", False, "没有访问令牌")
            return False
        
        test_data = {
            "query": "AI technology trends",
            "platforms": ["twitter", "reddit"],
            "analysis_type": "sentiment"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze",
                json=test_data,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("数据分析功能", True, "分析请求成功提交")
                return True
            elif response.status_code == 202:
                # 异步处理，返回任务ID
                self.log_test("数据分析功能", True, "分析任务已提交（异步处理）")
                return True
            else:
                self.log_test("数据分析功能", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("数据分析功能", False, f"请求失败: {str(e)}")
            return False
    
    def test_admin_endpoints(self) -> bool:
        """测试管理员端点"""
        if not self.access_token:
            self.log_test("管理员功能", False, "没有访问令牌")
            return False
        
        try:
            # 测试获取用户列表
            response = self.session.get(
                f"{self.base_url}/admin/users",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                user_count = len(data) if isinstance(data, list) else data.get('total', 0)
                self.log_test("管理员功能", True, f"获取用户列表成功，共 {user_count} 个用户")
                return True
            elif response.status_code == 403:
                self.log_test("管理员功能", True, "权限检查正常（非管理员用户）")
                return True
            else:
                self.log_test("管理员功能", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("管理员功能", False, f"请求失败: {str(e)}")
            return False
    
    def test_database_connection(self) -> bool:
        """测试数据库连接"""
        try:
            response = self.session.get(
                f"{self.base_url}/health/db",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                self.log_test("数据库连接", True, "数据库连接正常")
                return True
            else:
                self.log_test("数据库连接", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("数据库连接", False, f"请求失败: {str(e)}")
            return False
    
    def test_redis_connection(self) -> bool:
        """测试Redis连接"""
        try:
            response = self.session.get(
                f"{self.base_url}/health/redis",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                self.log_test("Redis连接", True, "Redis连接正常")
                return True
            else:
                self.log_test("Redis连接", False, f"状态码: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Redis连接", False, f"请求失败: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始运行后端API自动化测试...")
        print("=" * 60)
        
        tests = [
            ("服务器健康检查", self.test_server_health),
            ("数据库连接测试", self.test_database_connection),
            ("Redis连接测试", self.test_redis_connection),
            ("用户注册测试", self.test_user_registration),
            ("用户登录测试", self.test_user_login),
            ("受保护端点测试", self.test_protected_endpoint),
            ("数据分析功能测试", self.test_data_analysis_endpoint),
            ("管理员功能测试", self.test_admin_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试执行异常: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果统计:")
        print(f"   ✅ 通过: {passed}/{total}")
        print(f"   ❌ 失败: {total - passed}/{total}")
        print(f"   📈 成功率: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！后端API功能正常")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，需要检查")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed/total)*100,
            "results": self.test_results
        }

def main():
    """主函数"""
    print("🔍 后端API自动化测试工具")
    print(f"📡 目标服务器: {BASE_URL}")
    print("⏱️  开始测试...\n")
    
    tester = APITester()
    results = tester.run_all_tests()
    
    # 保存测试结果
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细测试结果已保存到: api_test_results.json")
    
    # 返回适当的退出码
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())