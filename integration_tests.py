#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本
测试前后端交互、数据流和完整用户流程
"""

import asyncio
import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import traceback
from concurrent.futures import ThreadPoolExecutor

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3001"
        self.api_base = f"{self.backend_url}/api/v1"
        self.test_results = []
        self.bugs_found = []
        self.test_user_token = None
        self.test_user_email = None
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if not success:
            self.bugs_found.append({
                "test_name": test_name,
                "error": error,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   错误: {error}")
    
    def check_services_availability(self) -> Tuple[bool, bool]:
        """检查前后端服务可用性"""
        print("\n🔍 检查服务可用性...")
        
        # 检查后端服务
        backend_available = False
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                backend_available = True
                self.log_test_result("后端服务可用性", True, "后端服务正常运行")
            else:
                self.log_test_result("后端服务可用性", False, f"后端服务状态码: {response.status_code}")
        except Exception as e:
            self.log_test_result("后端服务可用性", False, error=str(e))
        
        # 检查前端服务
        frontend_available = False
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                frontend_available = True
                self.log_test_result("前端服务可用性", True, "前端服务正常运行")
            else:
                self.log_test_result("前端服务可用性", False, f"前端服务状态码: {response.status_code}")
        except Exception as e:
            self.log_test_result("前端服务可用性", False, error=str(e))
        
        return backend_available, frontend_available
    
    def test_user_registration_flow(self) -> bool:
        """测试用户注册流程"""
        print("\n👤 测试用户注册流程...")
        try:
            # 生成唯一的测试用户
            timestamp = int(time.time())
            self.test_user_email = f"integration_test_{timestamp}@example.com"
            
            register_data = {
                "email": self.test_user_email,
                "username": f"integration_user_{timestamp}",
                "password": "testpassword123",
                "full_name": "Integration Test User"
            }
            
            # 发送注册请求
            response = requests.post(f"{self.api_base}/auth/register", json=register_data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.log_test_result("用户注册", True, f"用户注册成功: {self.test_user_email}")
                return True
            else:
                self.log_test_result("用户注册", False, f"注册失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("用户注册流程", False, error=str(e))
            return False
    
    def test_user_login_flow(self) -> bool:
        """测试用户登录流程"""
        print("\n🔐 测试用户登录流程...")
        try:
            if not self.test_user_email:
                self.log_test_result("用户登录", False, "没有可用的测试用户")
                return False
            
            login_data = {
                "username": self.test_user_email,
                "password": "testpassword123"
            }
            
            # 发送登录请求
            response = requests.post(f"{self.api_base}/auth/login", data=login_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.test_user_token = result.get("access_token")
                
                if self.test_user_token:
                    self.log_test_result("用户登录", True, "登录成功，获取到访问令牌")
                    return True
                else:
                    self.log_test_result("用户登录", False, "登录响应中缺少访问令牌")
                    return False
            else:
                self.log_test_result("用户登录", False, f"登录失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("用户登录流程", False, error=str(e))
            return False
    
    def test_authenticated_api_access(self) -> bool:
        """测试认证后的API访问"""
        print("\n🔑 测试认证后的API访问...")
        try:
            if not self.test_user_token:
                self.log_test_result("认证API访问", False, "没有可用的访问令牌")
                return False
            
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # 测试获取用户信息
            response = requests.get(f"{self.api_base}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                if user_info.get("email") == self.test_user_email:
                    self.log_test_result("获取用户信息", True, "成功获取用户信息")
                    return True
                else:
                    self.log_test_result("获取用户信息", False, "用户信息不匹配")
                    return False
            else:
                self.log_test_result("获取用户信息", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("认证API访问", False, error=str(e))
            return False
    
    def test_comprehensive_analysis_flow(self) -> bool:
        """测试综合分析完整流程"""
        print("\n📊 测试综合分析流程...")
        try:
            headers = {}
            if self.test_user_token:
                headers["Authorization"] = f"Bearer {self.test_user_token}"
            
            # 准备分析请求数据
            analysis_data = {
                "keywords": ["人工智能", "AI", "机器学习"],
                "user_id": "integration_test_user"
            }
            
            # 发送综合分析请求
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/trends/comprehensive-analysis",
                json=analysis_data,
                headers=headers,
                timeout=60  # 增加超时时间，因为分析可能需要较长时间
            )
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查返回数据结构
                required_fields = ["status", "data"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if not missing_fields:
                    data = result["data"]
                    
                    # 检查分析结果的完整性
                    analysis_sections = [
                        "title", "summary", "trends", "sentiment", 
                        "keywords", "recommendations", "sources"
                    ]
                    
                    available_sections = [section for section in analysis_sections if section in data]
                    
                    self.log_test_result(
                        "综合分析流程", 
                        True, 
                        f"分析成功，耗时 {analysis_time:.2f}秒，包含 {len(available_sections)} 个分析模块"
                    )
                    
                    # 详细检查每个分析模块
                    self.validate_analysis_sections(data)
                    
                    return True
                else:
                    self.log_test_result(
                        "综合分析流程", 
                        False, 
                        f"返回数据缺少必要字段: {missing_fields}"
                    )
                    return False
            else:
                self.log_test_result(
                    "综合分析流程", 
                    False, 
                    f"分析失败，状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("综合分析流程", False, error=str(e))
            return False
    
    def validate_analysis_sections(self, data: Dict[str, Any]):
        """验证分析结果各个模块"""
        print("\n🔍 验证分析结果模块...")
        
        # 验证标题和摘要
        if "title" in data and data["title"]:
            self.log_test_result("分析标题", True, f"标题: {data['title'][:50]}...")
        else:
            self.log_test_result("分析标题", False, "缺少分析标题")
        
        if "summary" in data and data["summary"]:
            self.log_test_result("分析摘要", True, f"摘要长度: {len(data['summary'])} 字符")
        else:
            self.log_test_result("分析摘要", False, "缺少分析摘要")
        
        # 验证趋势数据
        if "trends" in data and isinstance(data["trends"], list):
            self.log_test_result("趋势数据", True, f"包含 {len(data['trends'])} 个趋势项")
        else:
            self.log_test_result("趋势数据", False, "趋势数据格式不正确")
        
        # 验证情感分析
        if "sentiment" in data and isinstance(data["sentiment"], dict):
            sentiment_keys = ["positive", "negative", "neutral"]
            has_sentiment_data = any(key in data["sentiment"] for key in sentiment_keys)
            if has_sentiment_data:
                self.log_test_result("情感分析", True, "包含情感分析数据")
            else:
                self.log_test_result("情感分析", False, "情感分析数据不完整")
        else:
            self.log_test_result("情感分析", False, "缺少情感分析数据")
        
        # 验证关键词
        if "keywords" in data and isinstance(data["keywords"], list):
            self.log_test_result("关键词提取", True, f"提取到 {len(data['keywords'])} 个关键词")
        else:
            self.log_test_result("关键词提取", False, "关键词数据格式不正确")
        
        # 验证推荐
        if "recommendations" in data and isinstance(data["recommendations"], list):
            self.log_test_result("推荐建议", True, f"包含 {len(data['recommendations'])} 条推荐")
        else:
            self.log_test_result("推荐建议", False, "缺少推荐建议")
    
    def test_data_source_integration(self) -> bool:
        """测试数据源集成"""
        print("\n🌐 测试数据源集成...")
        try:
            headers = {}
            if self.test_user_token:
                headers["Authorization"] = f"Bearer {self.test_user_token}"
            
            # 测试Google Trends集成
            try:
                response = requests.get(
                    f"{self.api_base}/google-trends/search?keywords=AI",
                    headers=headers,
                    timeout=15
                )
                if response.status_code == 200:
                    self.log_test_result("Google Trends集成", True, "Google Trends数据获取成功")
                else:
                    self.log_test_result("Google Trends集成", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test_result("Google Trends集成", False, error=str(e))
            
            # 测试MonkeyLearn集成
            try:
                test_data = {"texts": ["This is a test message for sentiment analysis."]}
                response = requests.post(
                    f"{self.api_base}/monkeylearn/comprehensive-analysis",
                    json=test_data,
                    headers=headers,
                    timeout=15
                )
                if response.status_code == 200:
                    self.log_test_result("MonkeyLearn集成", True, "MonkeyLearn分析成功")
                else:
                    self.log_test_result("MonkeyLearn集成", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test_result("MonkeyLearn集成", False, error=str(e))
            
            return True
            
        except Exception as e:
            self.log_test_result("数据源集成", False, error=str(e))
            return False
    
    def test_concurrent_requests(self) -> bool:
        """测试并发请求处理"""
        print("\n⚡ 测试并发请求处理...")
        try:
            headers = {}
            if self.test_user_token:
                headers["Authorization"] = f"Bearer {self.test_user_token}"
            
            def make_health_request():
                try:
                    response = requests.get(f"{self.api_base}/health", headers=headers, timeout=10)
                    return response.status_code == 200
                except:
                    return False
            
            # 并发发送10个请求
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_health_request) for _ in range(10)]
                results = [future.result() for future in futures]
            
            success_count = sum(results)
            if success_count >= 8:  # 允许少量失败
                self.log_test_result("并发请求处理", True, f"{success_count}/10 请求成功")
                return True
            else:
                self.log_test_result("并发请求处理", False, f"只有 {success_count}/10 请求成功")
                return False
                
        except Exception as e:
            self.log_test_result("并发请求处理", False, error=str(e))
            return False
    
    def test_error_scenarios(self) -> bool:
        """测试错误场景处理"""
        print("\n⚠️ 测试错误场景处理...")
        try:
            # 测试无效的API端点
            response = requests.get(f"{self.api_base}/invalid-endpoint", timeout=5)
            if response.status_code == 404:
                self.log_test_result("无效端点处理", True, "正确返回404错误")
            else:
                self.log_test_result("无效端点处理", False, f"意外状态码: {response.status_code}")
            
            # 测试无效的认证令牌
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{self.api_base}/auth/me", headers=invalid_headers, timeout=5)
            if response.status_code == 401:
                self.log_test_result("无效令牌处理", True, "正确返回401错误")
            else:
                self.log_test_result("无效令牌处理", False, f"意外状态码: {response.status_code}")
            
            # 测试无效的请求数据
            invalid_data = {"invalid_field": "invalid_value"}
            response = requests.post(f"{self.api_base}/auth/register", json=invalid_data, timeout=5)
            if response.status_code in [400, 422]:  # 400 Bad Request 或 422 Unprocessable Entity
                self.log_test_result("无效数据处理", True, "正确返回客户端错误")
            else:
                self.log_test_result("无效数据处理", False, f"意外状态码: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test_result("错误场景处理", False, error=str(e))
            return False
    
    def test_data_persistence(self) -> bool:
        """测试数据持久化"""
        print("\n💾 测试数据持久化...")
        try:
            if not self.test_user_token:
                self.log_test_result("数据持久化", False, "没有可用的访问令牌")
                return False
            
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # 执行一次分析以创建数据
            analysis_data = {
                "keywords": ["数据持久化测试"],
                "user_id": "persistence_test"
            }
            
            response = requests.post(
                f"{self.api_base}/trends/comprehensive-analysis",
                json=analysis_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # 等待一段时间，然后检查数据是否仍然存在
                time.sleep(2)
                
                # 再次获取用户信息，验证数据持久化
                user_response = requests.get(f"{self.api_base}/auth/me", headers=headers, timeout=10)
                
                if user_response.status_code == 200:
                    self.log_test_result("数据持久化", True, "用户数据持久化正常")
                    return True
                else:
                    self.log_test_result("数据持久化", False, "用户数据获取失败")
                    return False
            else:
                self.log_test_result("数据持久化", False, "分析请求失败")
                return False
                
        except Exception as e:
            self.log_test_result("数据持久化", False, error=str(e))
            return False
    
    async def run_all_integration_tests(self):
        """运行所有集成测试"""
        print("🚀 开始集成测试套件")
        print("=" * 80)
        
        # 检查服务可用性
        backend_ok, frontend_ok = self.check_services_availability()
        
        if not backend_ok:
            print("❌ 后端服务不可用，无法继续集成测试")
            return
        
        # 用户认证流程测试
        print("\n👤 用户认证流程测试")
        print("-" * 40)
        registration_ok = self.test_user_registration_flow()
        login_ok = self.test_user_login_flow()
        auth_access_ok = self.test_authenticated_api_access()
        
        # 核心功能集成测试
        print("\n📊 核心功能集成测试")
        print("-" * 40)
        analysis_ok = self.test_comprehensive_analysis_flow()
        data_source_ok = self.test_data_source_integration()
        
        # 系统稳定性测试
        print("\n⚡ 系统稳定性测试")
        print("-" * 40)
        concurrent_ok = self.test_concurrent_requests()
        error_handling_ok = self.test_error_scenarios()
        persistence_ok = self.test_data_persistence()
        
        # 生成集成测试报告
        self.generate_integration_report()
    
    def generate_integration_report(self):
        """生成集成测试报告"""
        print("\n" + "=" * 80)
        print("📋 集成测试报告")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 集成测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests} ✅")
        print(f"   失败: {failed_tests} ❌")
        print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if self.bugs_found:
            print(f"\n🐛 集成测试发现的Bug ({len(self.bugs_found)}个):")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"   {i}. {bug['test_name']}")
                print(f"      错误: {bug['error']}")
                print(f"      详情: {bug['details']}")
                print(f"      时间: {bug['timestamp']}")
                print()
        
        # 保存详细报告到文件
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": passed_tests/total_tests*100 if total_tests > 0 else 0
                },
                "test_results": self.test_results,
                "bugs_found": self.bugs_found
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 集成测试报告已保存到: {report_file}")
        
        # 关键问题总结
        if self.bugs_found:
            critical_issues = []
            auth_issues = [bug for bug in self.bugs_found if "认证" in bug['test_name'] or "登录" in bug['test_name']]
            api_issues = [bug for bug in self.bugs_found if "API" in bug['test_name'] or "端点" in bug['test_name']]
            analysis_issues = [bug for bug in self.bugs_found if "分析" in bug['test_name']]
            
            if auth_issues:
                critical_issues.append("🔐 用户认证系统存在问题")
            if api_issues:
                critical_issues.append("📡 API接口存在问题")
            if analysis_issues:
                critical_issues.append("📊 分析功能存在问题")
            
            if critical_issues:
                print("\n🚨 关键问题总结:")
                for issue in critical_issues:
                    print(f"   {issue}")

async def main():
    """主函数"""
    integration_tests = IntegrationTestSuite()
    await integration_tests.run_all_integration_tests()

if __name__ == "__main__":
    asyncio.run(main())