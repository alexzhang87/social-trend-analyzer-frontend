#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试套件运行器
自动化前后端功能测试
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_prerequisites():
    """检查先决条件"""
    print("[STEP 1] Checking prerequisites...")
    
    # 检查Python
    code, stdout, stderr = run_command("python --version")
    if code == 0:
        print(f"[OK] Python is available: {stdout.strip()}")
    else:
        print("[ERROR] Python is not installed or not in PATH")
        return False
    
    # 检查Node.js
    code, stdout, stderr = run_command("node --version")
    if code == 0:
        print(f"[OK] Node.js is available: {stdout.strip()}")
    else:
        print("[ERROR] Node.js is not installed or not in PATH")
        return False
    
    print()
    return True

def install_test_dependencies():
    """安装测试依赖"""
    print("[STEP 2] Installing test dependencies...")
    
    # 安装requests
    code, stdout, stderr = run_command("pip install requests")
    if code == 0:
        print("[OK] requests installed")
    else:
        print("[WARNING] Failed to install requests")
    
    print()

def run_backend_tests(script_dir, results_dir, timestamp):
    """运行后端API测试"""
    print("[STEP 3] Running backend API tests...")
    
    backend_dir = os.path.join(script_dir, "backend")
    test_script = os.path.join(backend_dir, "automated_api_tests.py")
    
    if os.path.exists(test_script):
        print("[INFO] Starting backend API tests...")
        code, stdout, stderr = run_command(f"python {test_script}")
        
        # 移动结果文件
        result_file = "api_test_results.json"
        if os.path.exists(result_file):
            new_path = os.path.join(results_dir, f"api_test_results_{timestamp}.json")
            os.rename(result_file, new_path)
            print("[OK] Backend test results saved")
        
        if code == 0:
            print("[OK] Backend API tests passed")
            return True
        else:
            print("[WARNING] Backend API tests failed")
            if stdout:
                print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
            return False
    else:
        print("[WARNING] Backend API test script not found")
        return False

def run_frontend_tests(script_dir, results_dir, timestamp):
    """运行前端测试"""
    print("[STEP 4] Running frontend tests...")
    
    frontend_dir = os.path.join(script_dir, "frontend")
    test_script = os.path.join(frontend_dir, "automated_frontend_tests.js")
    
    if os.path.exists(test_script):
        print("[INFO] Starting frontend tests...")
        code, stdout, stderr = run_command("node automated_frontend_tests.js", cwd=frontend_dir)
        
        # 移动结果文件
        result_file = os.path.join(frontend_dir, "frontend_test_results.json")
        if os.path.exists(result_file):
            new_path = os.path.join(results_dir, f"frontend_test_results_{timestamp}.json")
            os.rename(result_file, new_path)
            print("[OK] Frontend test results saved")
        
        if code == 0:
            print("[OK] Frontend tests passed")
            return True
        else:
            print("[WARNING] Frontend tests failed")
            if stdout:
                print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
            return False
    else:
        print("[WARNING] Frontend test script not found")
        return False

def generate_summary_report(results_dir, timestamp, backend_passed, frontend_passed):
    """生成摘要报告"""
    print("[STEP 5] Generating summary report...")
    
    summary_file = os.path.join(results_dir, f"test_summary_{timestamp}.txt")
    
    total_tests = 2
    passed_tests = sum([backend_passed, frontend_passed])
    failed_tests = total_tests - passed_tests
    success_rate = round((passed_tests / total_tests) * 100, 1)
    
    summary = f"""========================================
   Comprehensive Test Suite Summary
========================================

Timestamp: {timestamp}
Test Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Test Results:

{"[PASS]" if backend_passed else "[FAIL]"} Backend API Tests
{"[PASS]" if frontend_passed else "[FAIL]"} Frontend Tests

Overall Statistics:
  Total Test Suites: {total_tests}
  Passed: {passed_tests}
  Failed: {failed_tests}
  Success Rate: {success_rate}%

{"Status: ALL TESTS PASSED" if passed_tests == total_tests else "Status: SOME TESTS FAILED"}
{"The application is ready for deployment." if passed_tests == total_tests else "Please review the failed tests before deployment."}

Detailed results can be found in:
  - {results_dir}\\api_test_results_{timestamp}.json
  - {results_dir}\\frontend_test_results_{timestamp}.json
"""
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"[OK] Summary report generated: {summary_file}")
    print()
    
    return passed_tests, total_tests, success_rate

def show_final_results(backend_passed, frontend_passed, passed_tests, total_tests, success_rate, results_dir):
    """显示最终结果"""
    print("========================================")
    print("           FINAL TEST RESULTS")
    print("========================================")
    print()
    
    backend_status = "PASS" if backend_passed else "FAIL"
    frontend_status = "PASS" if frontend_passed else "FAIL"
    
    print(f"Backend API Tests:     {backend_status}")
    print(f"Frontend Tests:        {frontend_status}")
    print()
    print(f"Overall Success Rate:  {success_rate}% ({passed_tests}/{total_tests})")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("   Your application is ready for deployment.")
        exit_code = 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Please review the failed tests before deployment.")
        print(f"   Check the detailed results in: {results_dir}")
        exit_code = 1
    
    print()
    print(f"Test results saved to: {results_dir}")
    print()
    print("[INFO] Test suite completed.")
    
    return exit_code

def main():
    """主函数"""
    # 配置
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "test_results")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建结果目录
    os.makedirs(results_dir, exist_ok=True)
    
    print("========================================")
    print("   Comprehensive Test Suite Runner")
    print("========================================")
    print()
    print("[INFO] Starting comprehensive test suite...")
    print(f"[INFO] Timestamp: {timestamp}")
    print(f"[INFO] Results will be saved to: {results_dir}")
    print()
    
    # 检查先决条件
    if not check_prerequisites():
        print("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    # 安装测试依赖
    install_test_dependencies()
    
    # 运行测试
    backend_passed = run_backend_tests(script_dir, results_dir, timestamp)
    print()
    
    frontend_passed = run_frontend_tests(script_dir, results_dir, timestamp)
    print()
    
    # 生成报告
    passed_tests, total_tests, success_rate = generate_summary_report(
        results_dir, timestamp, backend_passed, frontend_passed
    )
    
    # 显示最终结果
    exit_code = show_final_results(
        backend_passed, frontend_passed, passed_tests, total_tests, success_rate, results_dir
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()