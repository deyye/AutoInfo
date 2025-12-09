from openai import AsyncOpenAI
from jinja2 import Template
import asyncio
from config.settings import settings
from core.logger import logger
from datetime import datetime

class IntelligenceAnalyst:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.sem = asyncio.Semaphore(settings.MAX_LLM_CONCURRENT)

    async def summarize(self, text):
        """并发受限的摘要生成"""
        async with self.sem:
            try:
                # 简单截断防止 Token 溢出
                input_text = text[:4000]
                response = await self.client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个情报分析专家。请用中文简要总结文章核心（100字以内）。"},
                        {"role": "user", "content": input_text}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"LLM 调用失败: {e}")
                return "摘要生成失败"

    async def generate_insight(self, summaries):
        """生成全局洞察"""
        context = "\n".join([f"- {s}" for s in summaries])
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "user", "content": f"基于以下新闻摘要，总结3个关键趋势或一句话洞察：\n{context}"}
                ]
            )
            return response.choices[0].message.content
        except:
            return "今日暂无特别趋势。"

    def render_report(self, processed_data, insight):
        """使用 Jinja2 渲染报告"""
        with open(settings.TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 将列表转换为按分类分组的字典
        grouped_data = {}
        for item in processed_data:
            cat = item.category
            if cat not in grouped_data:
                grouped_data[cat] = []
            grouped_data[cat].append(item)
            
        return template.render(
            date=datetime.now().strftime("%Y-%m-%d"),
            data=grouped_data,
            insight=insight
        )