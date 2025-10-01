#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交媒体趋势分析工具 - 全面测试套件
测试所有核心功能模块，包括前端组件、后端API、数据库操作等
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

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

class ComprehensiveTestSuite:
    """全面测试套件"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_base = f"{self.base_url}/api/v1"
        self.frontend_url = "http://localhost:3001"
        self.test_results = []
        self.bugs_found = []
        
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
    
    # ==================== 后端API测试 ====================
    
    def test_health_endpoints(self) -> bool:
        """测试健康检查端点"""
        print("\n🏥 测试健康检查端点...")
        try:
            # 测试基础健康检查
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                self.log_test_result("健康检查端点", True, "API服务正常运行")
                return True
            else:
                self.log_test_result("健康检查端点", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("健康检查端点", False, error=str(e))
            return False
    
    def test_auth_endpoints(self) -> Tuple[bool, str]:
        """测试认证相关端点"""
        print("\n🔐 测试认证端点...")
        try:
            # 测试用户注册
            register_data = {
                "email": f"test_{int(time.time())}@example.com",
                "username": f"testuser_{int(time.time())}",
                "password": "testpassword123",
                "full_name": "Test User"
            }
            
            response = requests.post(f"{self.api_base}/auth/register", json=register_data, timeout=10)
            if response.status_code in [200, 201]:
                self.log_test_result("用户注册", True, "注册成功")
                
                # 测试用户登录
                login_data = {
                    "username": register_data["email"],
                    "password": register_data["password"]
                }
                
                response = requests.post(f"{self.api_base}/auth/login", data=login_data, timeout=10)
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    self.log_test_result("用户登录", True, "登录成功，获取到token")
                    return True, access_token
                else:
                    self.log_test_result("用户登录", False, f"登录失败，状态码: {response.status_code}")
                    return False, ""
            else:
                self.log_test_result("用户注册", False, f"注册失败，状态码: {response.status_code}")
                return False, ""
                
        except Exception as e:
            self.log_test_result("认证端点", False, error=str(e))
            return False, ""
    
    def test_trends_analysis_endpoint(self, token: str = "") -> bool:
        """测试趋势分析端点"""
        print("\n📊 测试趋势分析端点...")
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            # 测试综合分析端点
            analysis_data = {
                "keywords": ["AI", "人工智能"],
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{self.api_base}/trends/comprehensive-analysis",
                json=analysis_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "status" in result and "data" in result:
                    self.log_test_result("综合分析端点", True, "分析成功，返回完整数据结构")
                    return True
                else:
                    self.log_test_result("综合分析端点", False, "返回数据结构不完整")
                    return False
            else:
                self.log_test_result("综合分析端点", False, f"状态码: {response.status_code}, 响应: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("趋势分析端点", False, error=str(e))
            return False
    
    def test_google_trends_endpoint(self, token: str = "") -> bool:
        """测试Google Trends端点"""
        print("\n🔍 测试Google Trends端点...")
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            response = requests.get(
                f"{self.api_base}/google-trends/trending-searches?geo=CN",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result("Google Trends端点", True, "Google Trends数据获取成功")
                return True
            else:
                self.log_test_result("Google Trends端点", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Google Trends端点", False, error=str(e))
            return False
    
    def test_monkeylearn_endpoint(self, token: str = "") -> bool:
        """测试MonkeyLearn端点"""
        print("\n🐒 测试MonkeyLearn端点...")
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            test_data = {
                "texts": ["This is a great product!", "I love this innovation."]
            }
            
            response = requests.get(
                f"{self.api_base}/monkeylearn/status",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result("MonkeyLearn端点", True, "文本分析成功")
                return True
            else:
                self.log_test_result("MonkeyLearn端点", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("MonkeyLearn端点", False, error=str(e))
            return False
    
    def test_admin_endpoints(self, token: str = "") -> bool:
        """测试管理员端点"""
        print("\n👑 测试管理员端点...")
        try:
            # 测试管理员登录
            admin_data = {
                "username": "admin@example.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{self.api_base}/auth/login", data=admin_data, timeout=10)
            if response.status_code == 200:
                admin_token = response.json().get("access_token")
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                # 测试用户统计
                response = requests.get(f"{self.api_base}/admin/stats", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_test_result("管理员端点", True, "管理员功能正常")
                    return True
                else:
                    self.log_test_result("管理员端点", False, f"用户统计失败，状态码: {response.status_code}")
                    return False
            else:
                self.log_test_result("管理员端点", False, "管理员登录失败")
                return False
                
        except Exception as e:
            self.log_test_result("管理员端点", False, error=str(e))
            return False
    
    # ==================== 前端测试 ====================
    
    def test_frontend_accessibility(self) -> bool:
        """测试前端可访问性"""
        print("\n🌐 测试前端可访问性...")
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_test_result("前端可访问性", True, "前端服务正常运行")
                return True
            else:
                self.log_test_result("前端可访问性", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("前端可访问性", False, error=str(e))
            return False
    
    # ==================== 数据库测试 ====================
    
    async def test_database_operations(self) -> bool:
        """测试数据库操作（通过API）"""
        print("\n🗄️ 测试数据库操作...")
        try:
            # 通过健康检查端点测试数据库连接
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get("database", "unknown")
                self.log_test_result("数据库连接", True, f"数据库状态: {db_status}")
                
                # 通过用户注册测试数据库写入操作
                test_user_data = {
                    "email": f"dbtest_{int(time.time())}@example.com",
                    "username": f"dbtest_{int(time.time())}",
                    "password": "testpass123",
                    "full_name": "Database Test User"
                }
                
                reg_response = requests.post(f"{self.api_base}/auth/register", json=test_user_data, timeout=10)
                if reg_response.status_code == 200:
                    self.log_test_result("数据库写入", True, "用户注册成功，数据库写入正常")
                    return True
                else:
                    self.log_test_result("数据库写入", False, f"用户注册失败，状态码: {reg_response.status_code}")
                    return False
            else:
                self.log_test_result("数据库连接", False, f"健康检查失败，状态码: {response.status_code}")
                return False
            
        except Exception as e:
            self.log_test_result("数据库操作", False, error=str(e))
            return False
    
    # ==================== 服务层测试 ====================
    
    async def test_analysis_services(self) -> bool:
        """测试分析服务"""
        print("\n🔬 测试分析服务...")
        try:
            from app.services.analysis_service import AnalysisService
            from app.services.comprehensive_analysis_service import comprehensive_analysis_service
            
            # 测试基础分析服务
            analysis_service = AnalysisService()
            result = analysis_service.analyze_basic(["AI", "人工智能"])
            
            if result and "title" in result:
                self.log_test_result("基础分析服务", True, "分析服务正常工作")
            else:
                self.log_test_result("基础分析服务", False, "分析结果格式不正确")
                return False
            
            # 测试综合分析服务
            mock_data = {
                'twitter': [{'content': 'AI is amazing', 'score': 10}],
                'reddit': [{'content': 'Machine learning trends', 'score': 15}]
            }
            
            sentiment = comprehensive_analysis_service._analyze_cross_platform_sentiment(mock_data)
            keywords = comprehensive_analysis_service._analyze_cross_platform_keywords(mock_data)
            
            if sentiment and keywords:
                self.log_test_result("综合分析服务", True, "综合分析服务正常工作")
                return True
            else:
                self.log_test_result("综合分析服务", False, "综合分析结果不完整")
                return False
                
        except Exception as e:
            self.log_test_result("分析服务", False, error=str(e))
            return False
    
    # ==================== 集成测试 ====================
    
    def test_end_to_end_workflow(self, token: str = "") -> bool:
        """测试端到端工作流程"""
        print("\n🔄 测试端到端工作流程...")
        try:
            # 1. 用户注册登录
            auth_success, user_token = self.test_auth_endpoints()
            if not auth_success:
                self.log_test_result("端到端工作流程", False, "用户认证失败")
                return False
            
            # 2. 执行趋势分析
            analysis_success = self.test_trends_analysis_endpoint(user_token)
            if not analysis_success:
                self.log_test_result("端到端工作流程", False, "趋势分析失败")
                return False
            
            # 3. 测试数据获取
            trends_success = self.test_google_trends_endpoint(user_token)
            
            self.log_test_result("端到端工作流程", True, "完整工作流程测试成功")
            return True
            
        except Exception as e:
            self.log_test_result("端到端工作流程", False, error=str(e))
            return False
    
    # ==================== 性能测试 ====================
    
    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        print("\n⚡ 测试性能指标...")
        try:
            # 测试API响应时间
            start_time = time.time()
            response = requests.get(f"{self.api_base}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 2.0:
                self.log_test_result("API响应时间", True, f"响应时间: {response_time:.2f}秒")
            else:
                self.log_test_result("API响应时间", False, f"响应时间过长: {response_time:.2f}秒")
            
            # 测试并发请求
            import concurrent.futures
            
            def make_request():
                return requests.get(f"{self.api_base}/health", timeout=5)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in results if r.status_code == 200)
            if success_count >= 4:
                self.log_test_result("并发请求测试", True, f"{success_count}/5 请求成功")
                return True
            else:
                self.log_test_result("并发请求测试", False, f"只有 {success_count}/5 请求成功")
                return False
                
        except Exception as e:
            self.log_test_result("性能测试", False, error=str(e))
            return False
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始全面测试套件")
        print("=" * 80)
        
        # 后端API测试
        print("\n📡 后端API测试")
        print("-" * 40)
        health_ok = self.test_health_endpoints()
        auth_ok, token = self.test_auth_endpoints()
        trends_ok = self.test_trends_analysis_endpoint(token)
        google_trends_ok = self.test_google_trends_endpoint(token)
        monkeylearn_ok = self.test_monkeylearn_endpoint(token)
        admin_ok = self.test_admin_endpoints()
        
        # 前端测试
        print("\n🌐 前端测试")
        print("-" * 40)
        frontend_ok = self.test_frontend_accessibility()
        
        # 数据库测试
        print("\n🗄️ 数据库测试")
        print("-" * 40)
        db_ok = await self.test_database_operations()
        
        # 服务层测试
        print("\n🔬 服务层测试")
        print("-" * 40)
        services_ok = await self.test_analysis_services()
        
        # 集成测试
        print("\n🔄 集成测试")
        print("-" * 40)
        e2e_ok = self.test_end_to_end_workflow()
        
        # 性能测试
        print("\n⚡ 性能测试")
        print("-" * 40)
        performance_ok = self.test_performance_metrics()
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📋 测试报告")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests} ✅")
        print(f"   失败: {failed_tests} ❌")
        print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if self.bugs_found:
            print(f"\n🐛 发现的Bug ({len(self.bugs_found)}个):")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"   {i}. {bug['test_name']}")
                print(f"      错误: {bug['error']}")
                print(f"      详情: {bug['details']}")
                print(f"      时间: {bug['timestamp']}")
                print()
        
        # 保存详细报告到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": passed_tests/total_tests*100
                },
                "test_results": self.test_results,
                "bugs_found": self.bugs_found
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 推荐修复优先级
        if self.bugs_found:
            print("\n🔧 修复建议:")
            critical_bugs = [bug for bug in self.bugs_found if "端点" in bug['test_name'] or "数据库" in bug['test_name']]
            if critical_bugs:
                print("   🚨 高优先级 (核心功能):")
                for bug in critical_bugs:
                    print(f"     • {bug['test_name']}")
            
            other_bugs = [bug for bug in self.bugs_found if bug not in critical_bugs]
            if other_bugs:
                print("   ⚠️ 中优先级 (辅助功能):")
                for bug in other_bugs:
                    print(f"     • {bug['test_name']}")


async def main():
    """主函数"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())