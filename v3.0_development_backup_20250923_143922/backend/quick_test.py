#!/usr/bin/env python3
"""
快速测试脚本 - 验证趋势分析功能
"""
import requests
import json
import time
import sys

def test_analysis():
    print("🔍 测试趋势分析功能...")
    
    try:
        # 1. 发起分析请求
        print("\n1️⃣ 发起分析请求...")
        url = 'http://localhost:8001/api/v1/trends/'
        data = {'keywords': ['Vision Pro']}
        
        print(f"请求URL: {url}")
        print(f"请求数据: {data}")
        
        response = requests.post(url, json=data, timeout=10, allow_redirects=True)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code != 202:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
        
        task_data = response.json()
        task_id = task_data['task_id']
        print(f"✅ 任务创建成功")
        print(f"📋 任务ID: {task_id}")
        
        # 2. 查询任务状态
        print("\n2️⃣ 查询任务状态...")
        max_attempts = 60  # 延长查询次数到60次 (等待2分钟)
        
        for attempt in range(max_attempts):
            print(f"🔄 第 {attempt + 1}/{max_attempts} 次查询...")
            
            try:
                status_url = f'http://localhost:8001/api/v1/tasks/{task_id}'
                print(f"状态查询URL: {status_url}")
                
                status_response = requests.get(status_url, timeout=5)
                
                print(f"状态响应码: {status_response.status_code}")
                
                if status_response.status_code != 200:
                    print(f"❌ 状态查询失败: {status_response.status_code}")
                    print(f"响应: {status_response.text}")
                    continue
                
                status_data = status_response.json()
                status = status_data.get('status', 'UNKNOWN')
                progress = status_data.get('progress', 0)
                
                print(f"📊 状态: {status}, 进度: {progress}%")
                
                if status == 'SUCCESS':
                    print("\n🎉 分析完成！")
                    result = status_data.get('result', {})
                    
                    # 显示结果摘要
                    print("📈 结果摘要:")
                    print(f"   热度指数: {result.get('hotness_index', 'N/A')}")
                    print(f"   核心主题: {len(result.get('key_themes', []))} 个")
                    print(f"   商业机会: {len(result.get('business_opportunities', []))} 个")
                    print(f"   热门帖子: {len(result.get('top_posts', []))} 条")
                    
                    return True
                    
                elif status == 'FAILURE':
                    error = status_data.get('error', '未知错误')
                    print(f"\n❌ 分析失败: {error}")
                    return False
                    
                elif status == 'PENDING':
                    print("⏳ 任务等待中...")
                    
                else:
                    print(f"🔄 任务进行中: {status}")
                
                # 等待2秒后继续查询
                time.sleep(2)
                
            except requests.exceptions.Timeout:
                print("⏰ 查询超时，继续尝试...")
                continue
            except Exception as e:
                print(f"❌ 查询异常: {e}")
                continue
        
        print(f"\n⏰ 查询超时 ({max_attempts * 2} 秒)")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://localhost:8001)")
        print("请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 社交媒体趋势分析 - 快速测试")
    print("=" * 50)
    
    success = test_analysis()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过！系统工作正常")
        print("💡 你现在可以在前端界面正常使用分析功能了")
    else:
        print("❌ 测试失败！需要检查系统状态")
        print("🔧 建议重启后端服务:")
        print("   cd backend")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())