import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional
import os

# --- .env loading ---
# Use absolute paths to ensure reliability
# __file__ is the path to the current file (config.py)
# os.path.abspath gets the absolute path
# os.path.dirname gets the directory of a path
# So, we go up two directories from config.py to find the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
env_path = os.path.join(project_root, '.env')
env_proxy_path = os.path.join(project_root, '.env.proxy')

# Load the standard .env file if it exists
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"INFO:     Loaded environment variables from: {env_path}")
else:
    print(f"WARN:     .env file not found at: {env_path}. Using default settings or environment variables.")

# Load the proxy .env file if it exists, overriding previous settings
if os.path.exists(env_proxy_path):
    load_dotenv(dotenv_path=env_proxy_path, override=True)
    print(f"INFO:     Loaded proxy settings from: {env_proxy_path}")
# --- end of .env loading ---


class Settings(BaseSettings):
    PROJECT_NAME: str = "Trend Analyzer Backend"
    API_V1_STR: str = "/api/v1"
    
    # --- JWT Settings ---
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # --- Admin Settings ---
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    # --- Celery Settings ---
    # These are read from the environment, with default values for local development.
    CELERY_BROKER_URL: str = "redis://localhost:6380/0"  # 修改为6380
    CELERY_RESULT_BACKEND: str = "redis://localhost:6380/0"  # 修改为6380

    # --- Service Settings ---
    USE_MOCK_DATA: bool = False

    # --- Database ---
    # The DATABASE_URL will be read from the environment, with a default value.
    DATABASE_URL: str = "sqlite:///./test.db"

    # --- LLM ---
    # The ZHIPU_API_KEY will be read from the environment.
    # We set a default value to avoid Pydantic validation errors if the key is not set,
    # but our application logic will check for its presence.
    ZHIPU_API_KEY: str = "not_set"
    
    # --- Data Sources (placeholders) ---
    TWITTERAPI_IO_KEY: str = "your_twitterapi_io_key"
    REDDIT_CLIENT_ID: str = "your_reddit_client_id"
    REDDIT_CLIENT_SECRET: str = "your_reddit_client_secret"
    REDDIT_USER_AGENT: str = "trend-analyzer/1.0 by your_username"
    
    # --- Proxy Settings ---
    USE_PROXY: bool = False
    HTTP_PROXY: str = ""
    HTTPS_PROXY: str = ""

    # Stripe配置
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:5173"

# Create a single, importable instance of the settings
settings = Settings()

# A simple check to see if the key was loaded correctly
if settings.ZHIPU_API_KEY == "not_set":
    print("WARN:     ZHIPU_API_KEY was not found in environment. LLM calls will fail.")
