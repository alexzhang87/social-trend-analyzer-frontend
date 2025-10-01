import requests
import json

def test_trends_api():
    """测试趋势分析API - 使用端口8001"""
    url = "http://localhost:8001/api/v1/trends/"
    headers = {"Content-Type": "application/json"}
    data = {"keywords": ["Vision Pro"]}
    
    print(f"发送请求到: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(data)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 202:
            print("\n✅ 请求成功！")
            task_data = response.json()
            task_id = task_data['task_id']
            print(f"任务ID: {task_id}")
            
            # 查询任务状态
            print("\n正在查询任务状态...")
            status_url = f"http://localhost:8001/api/v1/tasks/{task_id}"
            status_response = requests.get(status_url)
            print(f"状态码: {status_response.status_code}")
            print(f"响应体: {status_response.text}")
        else:
            print("\n❌ 请求失败！")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_trends_api()