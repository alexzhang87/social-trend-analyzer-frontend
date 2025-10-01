import requests
import time

print("🚀 开始调试后台任务功能...")

try:
    # 调用我们新的调试端点
    response = requests.post('http://localhost:8000/api/v1/debug/test-bg-task', timeout=5)
    
    print(f"✅ 请求成功，状态码: {response.status_code}")
    print(f"✅ 响应内容: {response.json()}")
    
    if response.status_code == 200:
        print("\n🎉 调试成功！这意味着 FastAPI 的 BackgroundTasks 功能本身是正常的。")
        print("服务器能够立即返回响应，而不会被后台任务阻塞。")
        print("问题很可能出在 'trends' 接口的依赖服务中（如数据获取或分析服务）。")
    else:
        print("\n❌ 调试失败。")

except requests.exceptions.Timeout:
    print("\n❌ 请求超时！")
    print("这表明问题非常严重，即使是极简的后台任务也会导致服务器阻塞。")
    print("问题可能出在 FastAPI、Uvicorn 或某些中间件的配置上。")
except Exception as e:
    print(f"\n❌ 发生未知错误: {e}")