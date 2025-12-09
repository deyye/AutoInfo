from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class IntelligenceAnalyst:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.model = os.getenv("LLM_MODEL")

    def summarize_article(self, text):
        """对单篇文章进行快速摘要"""
        prompt = f"""
        你是一个专业的情报分析师。请阅读以下文章内容，用简练的中文总结核心观点（不超过3点）。
        如果不包含实质性信息，请返回"无效信息"。
        
        文章内容：
        {text}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"分析出错: {e}"

    def generate_final_report(self, summaries):
        """生成最终的 Markdown 简报"""
        data_context = ""
        for item in summaries:
            data_context += f"【来源】{item['source']} - {item['category']}\n"
            data_context += f"【标题】{item['title']}\n"
            data_context += f"【摘要】{item['summary']}\n"
            data_context += f"【链接】{item['url']}\n\n"

        prompt = f"""
        基于以下抓取到的情报数据，写一份《每日情报简报》。
        要求：
        1. 使用 Markdown 格式。
        2. 按【领域/类别】分类。
        3. 提炼出今天的 3 个关键趋势或洞察（Key Insights）。
        4. 语气专业、客观。
        
        情报数据：
        {data_context}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content