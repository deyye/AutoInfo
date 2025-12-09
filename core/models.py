from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional

class ArticleModel(BaseModel):
    title: str
    url: str
    source_name: str
    category: str
    content: str
    published_at: str = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary: Optional[str] = None

    @field_validator('content')
    def clean_content(cls, v):
        """自动清洗内容"""
        if not v:
            raise ValueError("内容为空")
            
        # 如果是缓存占位符，直接跳过长度检查
        if v == "cached":
            return v

        # 清洗逻辑：去除过多的换行符，去除干扰字符
        v = v.replace("\n\n\n", "\n").strip()
        if len(v) < 50:
            raise ValueError("内容过短，可能提取失败")
        return v