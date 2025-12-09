import asyncio
import json
from datetime import datetime
from core.logger import logger
from core.database import CacheDB
from core.models import ArticleModel
from modules.collector import DataCollector
from modules.analyst import IntelligenceAnalyst
from config.settings import settings

async def process_single_article(collector, analyst, db, entry, source):
    """处理单篇文章的原子操作"""
    url = entry.link
    url_hash = collector._get_url_hash(url)
    
    # 1. 缓存检查
    cached_summary = await db.is_processed(url_hash)
    if cached_summary:
        logger.info(f"⚡ 命中缓存: {entry.title[:15]}")
        # 即使命中缓存，也构造成对象返回，以便生成报告
        return ArticleModel(
            title=entry.title, url=url, source_name=source['name'],
            category=source['category'], content="cached", summary=cached_summary
        )

    # 2. 采集内容
    content = await collector.extract_content(url)
    if not content:
        return None

    # 3. 数据验证与清洗
    try:
        article = ArticleModel(
            title=entry.title,
            url=url,
            source_name=source['name'],
            category=source['category'],
            content=content
        )
    except ValueError as e:
        logger.warning(f"数据清洗过滤: {e} - {url}")
        return None

    # 4. LLM 摘要
    summary = await analyst.summarize(article.content)
    article.summary = summary

    # 5. 写入缓存
    await db.save_result(url_hash, url, article.title, summary)
    logger.success(f"✅ 处理完成: {article.title[:15]}")
    
    return article

async def main():
    logger.info("🚀 智能情报系统 v2.0 启动")
    
    # 初始化
    db = CacheDB()
    await db.init_db()
    collector = DataCollector()
    analyst = IntelligenceAnalyst()
    
    # 加载源
    with open(settings.SOURCES_PATH, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    tasks = []
    
    # 第一阶段：并发获取 RSS 列表
    logger.info("📡 正在并发扫描 RSS 源...")
    for source in sources:
        # 这里为了演示简单，直接await，也可以gather
        entries = await collector.fetch_rss_entries(source)
        for entry in entries:
            tasks.append(process_single_article(collector, analyst, db, entry, source))

    # 第二阶段：并发处理文章 (采集 -> 清洗 -> 摘要 -> 缓存)
    logger.info(f"即使处理任务数: {len(tasks)}")
    if not tasks:
        logger.warning("没有发现新文章")
        return

    results = await asyncio.gather(*tasks)
    valid_articles = [r for r in results if r is not None]

    # 第三阶段：生成报告
    if valid_articles:
        logger.info("📝 正在生成最终简报...")
        # 提取所有摘要用于生成 Insight
        all_summaries = [a.summary for a in valid_articles]
        insight = await analyst.generate_insight(all_summaries)
        
        # 渲染
        report_content = analyst.render_report(valid_articles, insight)
        
        filename = f"output/Daily_Briefing_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.success(f"🎉 报告生成完毕: {filename}")
    else:
        logger.info("无需生成报告 (无有效数据)")

if __name__ == "__main__":
    asyncio.run(main())