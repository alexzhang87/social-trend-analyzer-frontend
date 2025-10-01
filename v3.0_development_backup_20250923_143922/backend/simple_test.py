import requests
import json
import time

print("=" * 50)
print("🚀 简单API测试")
print("=" * 50)

# 测试端口8001上的API
url = "http://localhost:8001/api/v1/trends/"
data = {"keywords": ["Vision Pro"]}

print(f"请求URL: {url}")
print(f"请求数据: {json.dumps(data)}")

try:
    response = requests.post(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 202:
        print("\n✅ 请求成功！")
        task_id = response.json().get('task_id')
        print(f"任务ID: {task_id}")
        
        # 等待几秒钟，让后台任务有时间执行
        print("\n等待5秒钟...")
        time.sleep(5)
        
        # 查询任务状态
        status_url = f"http://localhost:8001/api/v1/tasks/{task_id}"
        print(f"\n查询任务状态: {status_url}")
        status_response = requests.get(status_url)
        print(f"状态码: {status_response.status_code}")
        print(f"响应内容: {status_response.text}")
    else:
        print("\n❌ 请求失败！")
except Exception as e:
    print(f"\n❌ 发生错误: {e}")

print("=" * 50)