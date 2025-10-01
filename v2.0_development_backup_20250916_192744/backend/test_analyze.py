import requests
import json

def test_analyze_endpoint():
    """测试分析端点"""
    url = "http://localhost:8000/api/v1/trends/analyze"
    headers = {"Content-Type": "application/json"}
    data = {"keywords": ["Vision Pro"], "platforms": ["twitter", "reddit"]}
    
    print(f"发送请求到: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(data)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应体: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_analyze_endpoint()