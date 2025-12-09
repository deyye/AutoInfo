# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 基础配置
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS = 5  # 爬虫并发数
    MAX_LLM_CONCURRENT = 3       # LLM 并发数
    REQUEST_TIMEOUT = 15         # 请求超时秒数
    
    # 路径配置
    DB_PATH = "output/cache.db"
    SOURCES_PATH = "config/sources.json"
    TEMPLATE_PATH = "config/report.md.j2"

settings = Settings()