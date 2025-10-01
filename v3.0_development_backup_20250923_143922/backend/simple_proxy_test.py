import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env and .env.proxy in the current directory
load_dotenv()
load_dotenv(dotenv_path='.env.proxy', override=True)

# Get settings from environment
API_KEY = os.getenv("TWITTERAPI_IO_KEY")
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

# --- Basic Sanity Checks ---
print("--- Configuration ---")
if not API_KEY:
    print("❌ TWITTERAPI_IO_KEY not found in .env file.")
else:
    # Print only last 4 chars for security
    print(f"✅ API Key loaded: ...{API_KEY[-4:]}")

if USE_PROXY:
    if not HTTP_PROXY:
        print("❌ USE_PROXY is true, but HTTP_PROXY is not found in .env.proxy file.")
    else:
        print(f"✅ HTTP Proxy loaded: {HTTP_PROXY}")
    if not HTTPS_PROXY:
        print("ℹ️ HTTPS_PROXY not specified, will use HTTP_PROXY for HTTPS traffic.")
        HTTPS_PROXY = HTTP_PROXY
    else:
        print(f"✅ HTTPS Proxy loaded: {HTTPS_PROXY}")
else:
    print("ℹ️ Proxy is disabled (USE_PROXY=false).")

print("---------------------\\n")


# --- Test Execution ---
if not API_KEY:
    print("🔴 Test cannot run due to missing API key. Please check your .env file.")
else:
    # Setup proxies if available, otherwise use direct connection
    proxies = None
    if USE_PROXY and HTTP_PROXY:
        proxies = {
            "http": HTTP_PROXY,
            "https": HTTPS_PROXY,
        }
        print("🚀 Sending request to Twitter API via proxy...")
        print(f"   Proxies: {proxies}")
    else:
        print("🚀 Sending request to Twitter API directly (no proxy)...")

    # Use the correct endpoint and query format from the documentation
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    params = {
        "query": "AI",
        "queryType": "Latest"
    }
    headers = {
        "X-API-Key": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    print(f"   URL: {url}")
    print(f"   Query: {params['query']}")
    print(f"   Headers: {{'X-API-Key': '...{API_KEY[-4:]}', 'User-Agent': 'Mozilla/5.0 ...'}}")


    try:
        # Set a timeout for the request, e.g., 20 seconds
        response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=20)
        
        print(f"\\n✅ Request successful! Status Code: {response.status_code}")
        
        # Try to print JSON response, handle case where it's not valid JSON
        try:
            print("--- Response JSON ---")
            print(response.json())
            print("---------------------")
        except requests.exceptions.JSONDecodeError:
            print("--- Response Text ---")
            print(response.text)
            print("---------------------")

    except requests.exceptions.ProxyError as e:
        print(f"\\n❌ Proxy Error: Could not connect to the proxy.")
        print(f"   Please ensure your VPN is running and the proxy address is correct.")
        print(f"   Details: {e}")
    except requests.exceptions.ConnectTimeout as e:
        print(f"\\n❌ Connection Timeout: The request timed out while trying to connect to the server.")
        print(f"   This could be a firewall issue or a problem with the proxy server.")
        print(f"   Details: {e}")
    except requests.exceptions.ReadTimeout as e:
        print(f"\\n❌ Read Timeout: The server did not send any data in the allotted time.")
        print(f"   The connection was established, but the server is not responding. This might be an API issue.")
        print(f"   Details: {e}")
    except requests.exceptions.RequestException as e:
        print(f"\\n❌ An unexpected request error occurred: {e}")