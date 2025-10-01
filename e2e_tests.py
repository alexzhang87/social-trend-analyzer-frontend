#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端自动化测试套件
测试完整的用户流程和前后端集成
"""

import asyncio
import json
import sys
import time
import subprocess
import signal
import os
from typing import Dict, Any, Optional, List
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# 测试配置
CONFIG = {
    'FRONTEND_URL': 'http://localhost:3000',
    'BACKEND_URL': 'http://localhost:8001',
    'TEST_TIMEOUT': 30,
    'SELENIUM_TIMEOUT': 10,
    'SERVER_START_TIMEOUT': 60
}

class E2ETester:
    def __init__(self):
        self.test_results = []
        self.driver = None
        self.frontend_process = None
        self.backend_process = None
        self.start_time = time.time()
    
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
    
    def setup_selenium(self) -> bool:
        """设置Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(CONFIG['SELENIUM_TIMEOUT'])
            
            self.log_test("Selenium设置", True, "WebDriver初始化成功")
            return True
        except Exception as e:
            self.log_test("Selenium设置", False, f"WebDriver初始化失败: {str(e)}")
            return False
    
    def start_backend_server(self) -> bool:
        """启动后端服务器"""
        try:
            print("🚀 启动后端服务器...")
            
            # 检查后端是否已经运行
            try:
                response = requests.get(f"{CONFIG['BACKEND_URL']}/health", timeout=5)
                if response.status_code == 200:
                    self.log_test("后端服务器启动", True, "后端服务器已在运行")
                    return True
            except:
                pass
            
            # 启动后端服务器
            backend_dir = os.path.join(os.getcwd(), 'backend')
            if os.path.exists(backend_dir):
                self.backend_process = subprocess.Popen(
                    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001'],
                    cwd=backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # 等待服务器启动
                for i in range(CONFIG['SERVER_START_TIMEOUT']):
                    try:
                        response = requests.get(f"{CONFIG['BACKEND_URL']}/health", timeout=2)
                        if response.status_code == 200:
                            self.log_test("后端服务器启动", True, f"服务器启动成功 (耗时 {i+1}秒)")
                            return True
                    except:
                        pass
                    time.sleep(1)
                
                self.log_test("后端服务器启动", False, "服务器启动超时")
                return False
            else:
                self.log_test("后端服务器启动", False, "后端目录不存在")
                return False
        except Exception as e:
            self.log_test("后端服务器启动", False, f"启动失败: {str(e)}")
            return False
    
    def start_frontend_server(self) -> bool:
        """启动前端服务器"""
        try:
            print("🚀 启动前端服务器...")
            
            # 检查前端是否已经运行
            try:
                response = requests.get(CONFIG['FRONTEND_URL'], timeout=5)
                if response.status_code == 200:
                    self.log_test("前端服务器启动", True, "前端服务器已在运行")
                    return True
            except:
                pass
            
            # 启动前端服务器
            frontend_dir = os.path.join(os.getcwd(), 'frontend')
            if os.path.exists(frontend_dir):
                # 设置环境变量以避免浏览器自动打开
                env = os.environ.copy()
                env['BROWSER'] = 'none'
                
                self.frontend_process = subprocess.Popen(
                    ['npm', 'start'],
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                # 等待服务器启动
                for i in range(CONFIG['SERVER_START_TIMEOUT']):
                    try:
                        response = requests.get(CONFIG['FRONTEND_URL'], timeout=2)
                        if response.status_code == 200:
                            self.log_test("前端服务器启动", True, f"服务器启动成功 (耗时 {i+1}秒)")
                            return True
                    except:
                        pass
                    time.sleep(1)
                
                self.log_test("前端服务器启动", False, "服务器启动超时")
                return False
            else:
                self.log_test("前端服务器启动", False, "前端目录不存在")
                return False
        except Exception as e:
            self.log_test("前端服务器启动", False, f"启动失败: {str(e)}")
            return False
    
    def test_homepage_load(self) -> bool:
        """测试首页加载"""
        try:
            self.driver.get(CONFIG['FRONTEND_URL'])
            
            # 等待页面加载
            WebDriverWait(self.driver, CONFIG['SELENIUM_TIMEOUT']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查页面标题
            title = self.driver.title
            if title:
                self.log_test("首页加载", True, f"页面加载成功，标题: {title}")
                return True
            else:
                self.log_test("首页加载", False, "页面标题为空")
                return False
        except TimeoutException:
            self.log_test("首页加载", False, "页面加载超时")
            return False
        except Exception as e:
            self.log_test("首页加载", False, f"页面加载失败: {str(e)}")
            return False
    
    def test_navigation(self) -> bool:
        """测试页面导航"""
        try:
            # 查找导航链接
            nav_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            if len(nav_links) > 0:
                self.log_test("页面导航", True, f"找到 {len(nav_links)} 个导航链接")
                
                # 测试第一个内部链接
                for link in nav_links[:3]:  # 只测试前3个链接
                    href = link.get_attribute('href')
                    if href and href.startswith(CONFIG['FRONTEND_URL']):
                        try:
                            link.click()
                            time.sleep(2)  # 等待页面加载
                            current_url = self.driver.current_url
                            self.log_test("导航测试", True, f"成功导航到: {current_url}")
                            break
                        except Exception as e:
                            continue
                
                return True
            else:
                self.log_test("页面导航", False, "未找到导航链接")
                return False
        except Exception as e:
            self.log_test("页面导航", False, f"导航测试失败: {str(e)}")
            return False
    
    def test_user_registration_flow(self) -> bool:
        """测试用户注册流程"""
        try:
            # 查找注册相关元素
            register_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '注册') or contains(text(), 'Register') or contains(text(), 'Sign Up')]")
            
            if register_elements:
                self.log_test("用户注册流程", True, "找到注册相关元素")
                
                # 尝试点击注册按钮
                try:
                    register_elements[0].click()
                    time.sleep(2)
                    
                    # 查找表单元素
                    form_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    if len(form_inputs) >= 2:  # 至少需要用户名和密码字段
                        self.log_test("注册表单", True, f"找到 {len(form_inputs)} 个输入字段")
                        return True
                    else:
                        self.log_test("注册表单", False, "表单字段不足")
                        return False
                except Exception as e:
                    self.log_test("注册流程", False, f"点击注册按钮失败: {str(e)}")
                    return False
            else:
                self.log_test("用户注册流程", False, "未找到注册相关元素")
                return False
        except Exception as e:
            self.log_test("用户注册流程", False, f"测试失败: {str(e)}")
            return False
    
    def test_api_integration(self) -> bool:
        """测试前后端API集成"""
        try:
            # 在浏览器中执行JavaScript来测试API调用
            script = f"""
            return fetch('{CONFIG['BACKEND_URL']}/health')
                .then(response => response.ok)
                .catch(error => false);
            """
            
            result = self.driver.execute_async_script(f"""
            var callback = arguments[arguments.length - 1];
            {script.replace('return ', '')}
                .then(callback)
                .catch(() => callback(false));
            """)
            
            if result:
                self.log_test("API集成测试", True, "前端成功调用后端API")
                return True
            else:
                self.log_test("API集成测试", False, "前端无法调用后端API")
                return False
        except Exception as e:
            self.log_test("API集成测试", False, f"测试失败: {str(e)}")
            return False
    
    def test_responsive_design(self) -> bool:
        """测试响应式设计"""
        try:
            # 测试不同屏幕尺寸
            screen_sizes = [
                (1920, 1080),  # 桌面
                (768, 1024),   # 平板
                (375, 667)     # 手机
            ]
            
            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # 检查页面是否正常显示
                body = self.driver.find_element(By.TAG_NAME, "body")
                if body.is_displayed():
                    self.log_test("响应式设计", True, f"屏幕尺寸 {width}x{height} 显示正常")
                else:
                    self.log_test("响应式设计", False, f"屏幕尺寸 {width}x{height} 显示异常")
                    return False
            
            return True
        except Exception as e:
            self.log_test("响应式设计", False, f"测试失败: {str(e)}")
            return False
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理测试环境...")
        
        # 关闭浏览器
        if self.driver:
            try:
                self.driver.quit()
                print("   ✅ 浏览器已关闭")
            except:
                pass
        
        # 关闭前端服务器
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
                print("   ✅ 前端服务器已关闭")
            except:
                try:
                    self.frontend_process.kill()
                except:
                    pass
        
        # 关闭后端服务器
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                print("   ✅ 后端服务器已关闭")
            except:
                try:
                    self.backend_process.kill()
                except:
                    pass
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有端到端测试"""
        print("🚀 开始运行端到端自动化测试...")
        print("=" * 60)
        
        # 设置阶段
        setup_tests = [
            ("Selenium设置", self.setup_selenium),
            ("后端服务器启动", self.start_backend_server),
            ("前端服务器启动", self.start_frontend_server),
        ]
        
        # 功能测试
        functional_tests = [
            ("首页加载测试", self.test_homepage_load),
            ("页面导航测试", self.test_navigation),
            ("用户注册流程测试", self.test_user_registration_flow),
            ("API集成测试", self.test_api_integration),
            ("响应式设计测试", self.test_responsive_design),
        ]
        
        all_tests = setup_tests + functional_tests
        passed = 0
        total = len(all_tests)
        
        try:
            # 运行设置测试
            setup_success = True
            for test_name, test_func in setup_tests:
                try:
                    if not test_func():
                        setup_success = False
                        break
                    passed += 1
                except Exception as e:
                    self.log_test(test_name, False, f"测试执行异常: {str(e)}")
                    setup_success = False
                    break
            
            # 只有设置成功才运行功能测试
            if setup_success:
                for test_name, test_func in functional_tests:
                    try:
                        if test_func():
                            passed += 1
                    except Exception as e:
                        self.log_test(test_name, False, f"测试执行异常: {str(e)}")
            else:
                print("\n⚠️  设置阶段失败，跳过功能测试")
        
        finally:
            self.cleanup()
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果统计:")
        print(f"   ✅ 通过: {passed}/{total}")
        print(f"   ❌ 失败: {total - passed}/{total}")
        print(f"   📈 成功率: {(passed/total)*100:.1f}%")
        print(f"   ⏱️  总耗时: {(time.time() - self.start_time):.1f}秒")
        
        if passed == total:
            print("\n🎉 所有测试通过！端到端功能正常")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，需要检查")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed/total)*100,
            "duration": time.time() - self.start_time,
            "results": self.test_results
        }

def main():
    """主函数"""
    print("🔍 端到端自动化测试工具")
    print(f"📡 前端服务器: {CONFIG['FRONTEND_URL']}")
    print(f"📡 后端服务器: {CONFIG['BACKEND_URL']}")
    print("⏱️  开始测试...\n")
    
    tester = E2ETester()
    
    # 设置信号处理器以确保清理
    def signal_handler(signum, frame):
        print("\n\n🛑 收到中断信号，正在清理...")
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        results = tester.run_all_tests()
        
        # 保存测试结果
        with open("e2e_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细测试结果已保存到: e2e_test_results.json")
        
        # 返回适当的退出码
        return 0 if results["failed"] == 0 else 1
    
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试执行失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())