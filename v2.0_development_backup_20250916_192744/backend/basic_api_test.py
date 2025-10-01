import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(dotenv_path='.env.proxy', override=True)

API_KEY = os.getenv("TWITTERAPI_IO_KEY")

print("--- Basic API Test ---")
if not API_KEY:
    print("❌ TWITTERAPI_IO_KEY not found in .env file.")
    exit(1)

print(f"✅ API Key loaded: ...{API_KEY[-4:]}")

# Try the simplest endpoint first - user info
url = "https://api.twitterapi.io/twitter/user/info"
params = {"userName": "elonmusk"}
headers = {"X-API-Key": API_KEY}

print("🚀 Testing basic user info endpoint...")
print(f"   URL: {url}")
print(f"   User: {params['userName']}")

try:
    response = requests.get(url, params=params, headers=headers, timeout=20)
    
    print(f"\n✅ Request completed! Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("🎉 SUCCESS! API is working!")
        data = response.json()
        if 'userName' in data:
            print(f"User: @{data['userName']}")
            print(f"Followers: {data.get('followers', 'N/A')}")
        print("--- Full Response ---")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ Request error: {e}")

print("\n--- Test Complete ---")