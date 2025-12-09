import aiosqlite
from config.settings import settings
from core.logger import logger

class CacheDB:
    def __init__(self):
        self.db_path = settings.DB_PATH

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url_hash TEXT PRIMARY KEY,
                    url TEXT,
                    title TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def is_processed(self, url_hash):
        """检查是否处理过，如果处理过直接返回摘要"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT summary FROM articles WHERE url_hash = ?", (url_hash,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def save_result(self, url_hash, url, title, summary):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO articles (url_hash, url, title, summary) VALUES (?, ?, ?, ?)",
                (url_hash, url, title, summary)
            )
            await db.commit()
            logger.debug(f"缓存已保存: {title[:10]}...")