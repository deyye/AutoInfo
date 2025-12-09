import json
import os
from datetime import datetime
from collector import DataCollector
from analyst import IntelligenceAnalyst

# 路径配置
CONFIG_PATH = 'config/sources.json'
OUTPUT_DIR = 'output'

def main():
    # 1. 初始化
    collector = DataCollector()
    analyst = IntelligenceAnalyst()
    raw_data = []
    
    # 2. 读取配置
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    print("🚀 情报系统启动...")

    # 3. 循环采集
    for source in sources:
        print(f"\nProcessing Source: {source['name']}")
        
        if source['type'] == 'rss':
            articles = collector.fetch_rss(source['url'], limit=2) # 演示用，限制2条
            
            for art in articles:
                print(f"  - 分析: {art['title']}...")
                summary = analyst.summarize_article(art['content'])
                
                raw_data.append({
                    "source": source['name'],
                    "category": source['category'],
                    "title": art['title'],
                    "url": art['url'],
                    "summary": summary
                })

    # 4. 生成最终报告
    print("\n🧠 正在生成最终情报简报...")
    final_report = analyst.generate_final_report(raw_data)

    # 5. 保存结果
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{OUTPUT_DIR}/Daily_Briefing_{date_str}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"✅ 报告已生成: {filename}")

if __name__ == "__main__":
    main()