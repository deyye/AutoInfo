# core/logger.py
import sys
from loguru import logger
import os

# 确保日志目录存在
os.makedirs("output/logs", exist_ok=True)

# 移除默认 handler
logger.remove()

# 添加控制台输出 (Info 级别)
logger.add(sys.stderr, level="INFO")

# 添加文件输出 (自动按天轮转，保留 10 天，错误单独记录)
logger.add("output/logs/info.log", rotation="00:00", retention="10 days", level="INFO")
logger.add("output/logs/error.log", rotation="10 MB", retention="10 days", level="ERROR")