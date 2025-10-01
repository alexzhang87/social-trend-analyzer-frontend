import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file located in the script's directory
dotenv_path = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

BASE_URL = "http://127.0.0.1:8000"
# Build the absolute path to the seed data file
SEED_DATA_PATH = os.path.join(SCRIPT_DIR, "seed_data.json")
API_KEY = os.getenv("ZHIPU_API_KEY")

def check_api_key():
    """Check if the ZhipuAI API key is set."""
    if not API_KEY:
        print("❌ ERROR: ZHIPU_API_KEY is not set in your .env file.")
        print(f"Please ensure a .env file exists at '{os.path.join(SCRIPT_DIR, '.env')}' with your key:")
        print("ZHIPU_API_KEY=your-key-here")
        return False
    return True

def seed_database():
    """Reads seed data and posts it to the /api/seed endpoint."""
    print("Step 1: Seeding database...")
    try:
        with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        response = requests.post(f"{BASE_URL}/api/seed", json=data)
        response.raise_for_status()
        print(f"✅ {response.json().get('message')}")
        return True
    except FileNotFoundError:
        print(f"❌ ERROR: Seed data file not found at '{SEED_DATA_PATH}'")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to connect to the backend at {BASE_URL}.")
        print("Please ensure the FastAPI server is running in a separate terminal.")
        print(f"Details: {e}")
        return False

def run_analysis():
    """Calls the synchronous analysis endpoint and prints the result."""
    print("\nStep 2: Running synchronous analysis...")
    print("(This may take a minute as it involves multiple LLM calls)...")
    try:
        response = requests.post(f"{BASE_URL}/api/analyze/sync")
        response.raise_for_status()
        
        analysis_result = response.json()
        
        print("✅ Analysis complete!")
        print(f"Found {analysis_result.get('trend_count', 0)} trends.")
        
        # Pretty-print the result to a file in the same directory as the script
        output_filename = os.path.join(SCRIPT_DIR, "analysis_result.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Full analysis result has been saved to '{output_filename}'")
        
        # Print a summary of the first trend
        if analysis_result.get("results"):
            first_trend = analysis_result["results"][0]
            print("\n--- Summary of First Trend ---")
            print(f"Title: {first_trend.get('title')}")
            print(f"Summary: {first_trend.get('summary')}")
            print(f"Hot Score: {first_trend.get('hot_score')}")
            print("----------------------------")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to run analysis.")
        print(f"Details: {e}")
        if "500" in str(e):
             print("\nHint: A 500 Internal Server Error often means the LLM call failed.")
             print("Please double-check your ZHIPU_API_KEY and ensure you have a valid subscription/credits.")


if __name__ == "__main__":
    print("🚀 Starting Backend Test Runner...")
    if check_api_key():
        if seed_database():
            run_analysis()