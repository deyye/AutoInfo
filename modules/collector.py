import hashlib
import asyncio
import feedparser
import trafilatura
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor
from core.logger import logger
from config.settings import settings

class DataCollector:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_REQUESTS)

    def _get_url_hash(self, url):
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def sync_fetch_feed(self, url):
        """同步解析 Feed（供 executor 调用）"""
        return feedparser.parse(url)

    def sync_extract(self, url):
        """同步提取正文（供 executor 调用）"""
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded, include_comments=False)

    async def fetch_rss_entries(self, source):
        """异步获取 RSS 列表"""
        loop = asyncio.get_running_loop()
        try:
            feed = await loop.run_in_executor(None, self.sync_fetch_feed, source['url'])
            return feed.entries[:3] # 限制每源 3 条
        except Exception as e:
            logger.error(f"RSS 解析失败 {source['name']}: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def extract_content(self, url):
        """异步+重试机制提取正文"""
        loop = asyncio.get_running_loop()
        try:
            content = await loop.run_in_executor(self.executor, self.sync_extract, url)
            return content
        except Exception as e:
            logger.warning(f"提取失败 (正在重试): {url} - {e}")
            raise e  # 抛出给 tenacity 进行重试