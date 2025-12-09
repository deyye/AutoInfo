import feedparser
import trafilatura
import requests
from datetime import datetime

class DataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_rss(self, url, limit=3):
        """解析 RSS Feed"""
        print(f"📡 正在抓取 RSS: {url}...")
        feed = feedparser.parse(url)
        articles = []
        
        # 只取最新的 N 条
        for entry in feed.entries[:limit]:
            content = self.extract_content(entry.link)
            if content:
                articles.append({
                    "title": entry.title,
                    "url": entry.link,
                    "content": content[:3000], # 截断避免 Token 溢出
                    "published": getattr(entry, 'published', str(datetime.now()))
                })
        return articles

    def extract_content(self, url):
        """核心：智能提取网页正文"""
        try:
            downloaded = trafilatura.fetch_url(url)
            # include_comments=False 过滤评论，include_tables=True 保留表格
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
            return text
        except Exception as e:
            print(f"❌ 提取失败 {url}: {e}")
            return None