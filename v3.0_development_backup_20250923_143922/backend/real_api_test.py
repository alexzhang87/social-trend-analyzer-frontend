import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(dotenv_path='.env.proxy', override=True)

# Get API key
API_KEY = os.getenv("TWITTERAPI_IO_KEY")

print("--- Real API Test (Based on Browser Request) ---")
if not API_KEY:
    print("❌ TWITTERAPI_IO_KEY not found in .env file.")
    exit(1)

print(f"✅ API Key loaded: ...{API_KEY[-4:]}")

# This is the exact request format that works in the browser
url = "https://docs.twitterapi.io/api/request"

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://docs.twitterapi.io',
    'referer': 'https://docs.twitterapi.io/api-reference/endpoint/tweet_advanced_search?playground=open',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

# This is the exact payload format from the browser
payload = {
    "method": "get",
    "url": "https://api.twitterapi.io/twitter/tweet/advanced_search",
    "header": {
        "X-API-Key": API_KEY,
        "content-type": "application/json"
    },
    "cookie": {},
    "query": {
        "queryType": "Latest",
        "query": "AI trend tool"
    }
}

print("🚀 Sending request using browser format...")
print(f"   URL: {url}")
print(f"   Query: {payload['query']['query']}")
print(f"   Method: POST (with API call details in body)")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"\n✅ Request successful! Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("--- Response JSON ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("---------------------")
            
            # Check if we got tweets
            if isinstance(data, dict) and 'tweets' in data:
                tweets = data.get('tweets', [])
                print(f"\n🎉 SUCCESS! Found {len(tweets)} tweets!")
                if tweets:
                    print("First tweet preview:")
                    first_tweet = tweets[0]
                    print(f"  Author: @{first_tweet.get('author', {}).get('userName', 'unknown')}")
                    print(f"  Text: {first_tweet.get('text', '')[:100]}...")
            else:
                print("\n📝 Response received, but format is different than expected.")
                
        except json.JSONDecodeError:
            print("--- Response Text ---")
            print(response.text)
            print("---------------------")
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ Request error: {e}")

print("\n--- Test Complete ---")