import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# --- .env loading ---
# Build paths to the .env files
base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
env_path = os.path.join(base_dir, '.env')
env_proxy_path = os.path.join(base_dir, '.env.proxy')

# 优先加载标准 .env 文件
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"INFO:     Loaded environment variables from: {env_path}")
else:
    print(f"WARN:     .env file not found at: {env_path}. Using default settings or environment variables.")

# 然后加载代理配置文件（如果存在）
if os.path.exists(env_proxy_path):
    load_dotenv(dotenv_path=env_proxy_path, override=True)
    print(f"INFO:     Loaded proxy settings from: {env_proxy_path}")
# --- end of .env loading ---


class Settings(BaseSettings):
    PROJECT_NAME: str = "Trend Analyzer Backend"
    API_V1_STR: str = "/api/v1"

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

# Create a single, importable instance of the settings
settings = Settings()

# A simple check to see if the key was loaded correctly
if settings.ZHIPU_API_KEY == "not_set":
    print("WARN:     ZHIPU_API_KEY was not found in environment. LLM calls will fail.")