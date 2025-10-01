#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端组件测试脚本
使用Selenium测试前端React组件的功能和交互
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FrontendComponentTests:
    """前端组件测试类"""
    
    def __init__(self):
        self.frontend_url = "http://localhost:3001"
        self.driver = None
        self.test_results = []
        self.bugs_found = []
        
    def setup_driver(self):
        """设置Chrome驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ 无法启动Chrome驱动: {e}")
            print("💡 提示: 请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
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
    
    def test_page_load(self) -> bool:
        """测试页面加载"""
        print("\n🌐 测试页面加载...")
        try:
            self.driver.get(self.frontend_url)
            
            # 等待页面标题加载
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.title != ""
            )
            
            title = self.driver.title
            if title:
                self.log_test_result("页面加载", True, f"页面标题: {title}")
                return True
            else:
                self.log_test_result("页面加载", False, "页面标题为空")
                return False
                
        except TimeoutException:
            self.log_test_result("页面加载", False, error="页面加载超时")
            return False
        except Exception as e:
            self.log_test_result("页面加载", False, error=str(e))
            return False
    
    def test_navigation_components(self) -> bool:
        """测试导航组件"""
        print("\n🧭 测试导航组件...")
        try:
            # 查找导航栏
            nav_elements = self.driver.find_elements(By.TAG_NAME, "nav")
            if not nav_elements:
                nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='navigation']")
            
            if nav_elements:
                self.log_test_result("导航栏存在", True, f"找到 {len(nav_elements)} 个导航元素")
            else:
                self.log_test_result("导航栏存在", False, "未找到导航元素")
                return False
            
            # 查找导航链接
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a, [role='navigation'] a")
            if nav_links:
                self.log_test_result("导航链接", True, f"找到 {len(nav_links)} 个导航链接")
                
                # 测试第一个链接点击
                if len(nav_links) > 0:
                    first_link = nav_links[0]
                    link_text = first_link.text
                    first_link.click()
                    time.sleep(2)
                    self.log_test_result("导航链接点击", True, f"成功点击链接: {link_text}")
                
                return True
            else:
                self.log_test_result("导航链接", False, "未找到导航链接")
                return False
                
        except Exception as e:
            self.log_test_result("导航组件", False, error=str(e))
            return False
    
    def test_dashboard_components(self) -> bool:
        """测试仪表板组件"""
        print("\n📊 测试仪表板组件...")
        try:
            # 查找仪表板容器
            dashboard_selectors = [
                "[data-testid='dashboard']",
                ".dashboard",
                "#dashboard",
                "[class*='dashboard']"
            ]
            
            dashboard_element = None
            for selector in dashboard_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    dashboard_element = elements[0]
                    break
            
            if dashboard_element:
                self.log_test_result("仪表板容器", True, "找到仪表板容器")
            else:
                self.log_test_result("仪表板容器", False, "未找到仪表板容器")
                return False
            
            # 查找图表组件
            chart_selectors = [
                "canvas",
                "svg",
                "[class*='chart']",
                "[data-testid*='chart']"
            ]
            
            charts_found = 0
            for selector in chart_selectors:
                charts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                charts_found += len(charts)
            
            if charts_found > 0:
                self.log_test_result("图表组件", True, f"找到 {charts_found} 个图表元素")
            else:
                self.log_test_result("图表组件", False, "未找到图表元素")
            
            # 查找数据卡片
            card_selectors = [
                "[class*='card']",
                "[data-testid*='card']",
                ".metric-card",
                ".stat-card"
            ]
            
            cards_found = 0
            for selector in card_selectors:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                cards_found += len(cards)
            
            if cards_found > 0:
                self.log_test_result("数据卡片", True, f"找到 {cards_found} 个数据卡片")
                return True
            else:
                self.log_test_result("数据卡片", False, "未找到数据卡片")
                return False
                
        except Exception as e:
            self.log_test_result("仪表板组件", False, error=str(e))
            return False
    
    def test_search_functionality(self) -> bool:
        """测试搜索功能"""
        print("\n🔍 测试搜索功能...")
        try:
            # 查找搜索输入框
            search_selectors = [
                "input[type='search']",
                "input[placeholder*='搜索']",
                "input[placeholder*='search']",
                "[data-testid='search-input']",
                "[class*='search'] input"
            ]
            
            search_input = None
            for selector in search_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_input = elements[0]
                    break
            
            if search_input:
                self.log_test_result("搜索输入框", True, "找到搜索输入框")
                
                # 测试输入
                test_keyword = "AI人工智能"
                search_input.clear()
                search_input.send_keys(test_keyword)
                
                # 等待输入完成
                time.sleep(1)
                
                # 检查输入值
                input_value = search_input.get_attribute("value")
                if input_value == test_keyword:
                    self.log_test_result("搜索输入", True, f"成功输入关键词: {test_keyword}")
                else:
                    self.log_test_result("搜索输入", False, f"输入值不匹配: {input_value}")
                
                # 查找搜索按钮
                search_button_selectors = [
                    "button[type='submit']",
                    "[data-testid='search-button']",
                    "[class*='search'] button",
                    "button[class*='search']"
                ]
                
                search_button = None
                for selector in search_button_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_button = elements[0]
                        break
                
                if search_button:
                    search_button.click()
                    time.sleep(3)  # 等待搜索结果
                    self.log_test_result("搜索按钮点击", True, "成功点击搜索按钮")
                else:
                    # 尝试按回车键
                    from selenium.webdriver.common.keys import Keys
                    search_input.send_keys(Keys.RETURN)
                    time.sleep(3)
                    self.log_test_result("搜索提交", True, "通过回车键提交搜索")
                
                return True
            else:
                self.log_test_result("搜索输入框", False, "未找到搜索输入框")
                return False
                
        except Exception as e:
            self.log_test_result("搜索功能", False, error=str(e))
            return False
    
    def test_responsive_design(self) -> bool:
        """测试响应式设计"""
        print("\n📱 测试响应式设计...")
        try:
            # 测试不同屏幕尺寸
            screen_sizes = [
                (1920, 1080, "桌面"),
                (768, 1024, "平板"),
                (375, 667, "手机")
            ]
            
            responsive_results = []
            
            for width, height, device_type in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(2)
                
                # 检查页面是否正常显示
                body = self.driver.find_element(By.TAG_NAME, "body")
                if body.is_displayed():
                    responsive_results.append(f"{device_type}({width}x{height}): ✅")
                else:
                    responsive_results.append(f"{device_type}({width}x{height}): ❌")
            
            success_count = sum(1 for result in responsive_results if "✅" in result)
            if success_count == len(screen_sizes):
                self.log_test_result("响应式设计", True, "; ".join(responsive_results))
                return True
            else:
                self.log_test_result("响应式设计", False, "; ".join(responsive_results))
                return False
                
        except Exception as e:
            self.log_test_result("响应式设计", False, error=str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n⚠️ 测试错误处理...")
        try:
            # 检查控制台错误
            logs = self.driver.get_log('browser')
            error_logs = [log for log in logs if log['level'] == 'SEVERE']
            
            if error_logs:
                error_messages = [log['message'] for log in error_logs]
                self.log_test_result("控制台错误", False, f"发现 {len(error_logs)} 个严重错误", "; ".join(error_messages[:3]))
                return False
            else:
                self.log_test_result("控制台错误", True, "无严重控制台错误")
            
            # 检查是否有错误边界组件
            error_boundary_selectors = [
                "[data-testid='error-boundary']",
                "[class*='error-boundary']",
                "[class*='error-fallback']"
            ]
            
            error_boundaries = []
            for selector in error_boundary_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                error_boundaries.extend(elements)
            
            if error_boundaries:
                self.log_test_result("错误边界", False, f"发现 {len(error_boundaries)} 个错误边界被触发")
                return False
            else:
                self.log_test_result("错误边界", True, "无错误边界被触发")
                return True
                
        except Exception as e:
            self.log_test_result("错误处理", False, error=str(e))
            return False
    
    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        print("\n⚡ 测试前端性能...")
        try:
            # 测试页面加载时间
            start_time = time.time()
            self.driver.get(self.frontend_url)
            
            # 等待页面完全加载
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            load_time = time.time() - start_time
            
            if load_time < 5.0:
                self.log_test_result("页面加载时间", True, f"加载时间: {load_time:.2f}秒")
            else:
                self.log_test_result("页面加载时间", False, f"加载时间过长: {load_time:.2f}秒")
            
            # 检查资源加载
            performance_logs = self.driver.get_log('performance')
            network_events = [log for log in performance_logs if 'Network' in log['message']]
            
            if network_events:
                self.log_test_result("网络请求", True, f"检测到 {len(network_events)} 个网络事件")
            else:
                self.log_test_result("网络请求", False, "未检测到网络事件")
            
            return True
            
        except Exception as e:
            self.log_test_result("前端性能", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """运行所有前端测试"""
        print("🚀 开始前端组件测试")
        print("=" * 60)
        
        if not self.setup_driver():
            print("❌ 无法设置浏览器驱动，跳过前端测试")
            return
        
        try:
            # 基础功能测试
            print("\n🌐 基础功能测试")
            print("-" * 30)
            page_load_ok = self.test_page_load()
            navigation_ok = self.test_navigation_components()
            dashboard_ok = self.test_dashboard_components()
            
            # 交互功能测试
            print("\n🔍 交互功能测试")
            print("-" * 30)
            search_ok = self.test_search_functionality()
            
            # 设计和性能测试
            print("\n📱 设计和性能测试")
            print("-" * 30)
            responsive_ok = self.test_responsive_design()
            error_handling_ok = self.test_error_handling()
            performance_ok = self.test_performance_metrics()
            
            # 生成报告
            self.generate_frontend_report()
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_frontend_report(self):
        """生成前端测试报告"""
        print("\n" + "=" * 60)
        print("📋 前端测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 前端测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests} ✅")
        print(f"   失败: {failed_tests} ❌")
        print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if self.bugs_found:
            print(f"\n🐛 前端Bug ({len(self.bugs_found)}个):")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"   {i}. {bug['test_name']}")
                print(f"      错误: {bug['error']}")
                print(f"      详情: {bug['details']}")
                print()
        
        # 保存报告
        report_file = f"frontend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        
        print(f"\n📄 前端测试报告已保存到: {report_file}")

def main():
    """主函数"""
    frontend_tests = FrontendComponentTests()
    frontend_tests.run_all_tests()

if __name__ == "__main__":
    main()