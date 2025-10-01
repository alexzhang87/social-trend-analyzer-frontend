import requests
import json
import time

def test_analysis():
    print("=== 测试趋势分析功能 ===")
    
    # 1. 发起分析请求
    print("1. 发起分析请求...")
    response = requests.post('http://localhost:8000/api/v1/trends/', 
                           json={'keywords': ['Vision Pro']})
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 202:
        print(f"请求失败: {response.text}")
        return
    
    task_data = response.json()
    task_id = task_data['task_id']
    print(f"任务ID: {task_id}")
    print(f"响应: {task_data}")
    
    # 2. 等待并查询任务状态
    print("\n2. 查询任务状态...")
    for i in range(10):  # 最多查询10次
        print(f"第 {i+1} 次查询...")
        status_response = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
        
        if status_response.status_code != 200:
            print(f"状态查询失败: {status_response.text}")
            break
            
        status_data = status_response.json()
        print(f"任务状态: {status_data}")
        
        if status_data['status'] == 'SUCCESS':
            print("\n✅ 分析完成！")
            result = status_data.get('result', {})
            print(f"结果概览:")
            print(f"- 热度指数: {result.get('hotness_index', 'N/A')}")
            print(f"- 核心主题数量: {len(result.get('key_themes', []))}")
            print(f"- 商业机会数量: {len(result.get('business_opportunities', []))}")
            return True
        elif status_data['status'] == 'FAILURE':
            print(f"\n❌ 分析失败: {status_data.get('error', '未知错误')}")
            return False
        else:
            print(f"状态: {status_data['status']}, 进度: {status_data.get('progress', 0)}%")
            time.sleep(2)  # 等待2秒后再查询
    
    print("\n⏰ 查询超时")
    return False

if __name__ == "__main__":
    test_analysis()