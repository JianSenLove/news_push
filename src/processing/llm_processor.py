import re
import json
from openai import OpenAI
from src.ingestion.rss_parser import Article
from typing import List, Dict, Any

class AIProcessor:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
    def summarize(self, articles: List[Article], category_name: str = "综合报导", model_name: str = "gpt-3.5-turbo") -> List[Dict[str, Any]]:
        if not articles:
            return []
            
        system_prompt = (
            f"你是一个资深的前沿科技观察家，当前你正在专司处理【{category_name}】板块的新闻信息。\n"
            "你需要阅读输入的信息，进行高质量提炼总结。\n"
            "要求：\n"
            "1. 必须且只能输出合法的 JSON 格式。最外层必须是一个数组 (Array)。\n"
            "2. 数组内每个对象代表一条总结好的新闻，字段包含：'title'(标题)、'summary'(一句话总结摘要)、'analysis'(深度短评或意义)、'link'(原始链接)。\n"
            "3. 不要输出除 JSON 外的任何废话、Markdown说明文本，如果使用 markdown json 块请保证结构严谨。\n"
        )
        
        content_lines = []
        for i, art in enumerate(articles):
            content_lines.append(f"[{i+1}] 标题: {art.title}\n摘要: {art.summary}\n来源: {art.source}\n链接: {art.link}\n")
            
        user_content = "请归类总结提取以下原始资讯为 JSON：\n" + "\n".join(content_lines)
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # 尝试清洗 ```json ``` 的包裹
        json_str = raw_content
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_content, re.DOTALL)
        if match:
            json_str = match.group(1)
            
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 解析失败保护
            return [{"title": "AI解析失败", "summary": "解析大模型数据失败", "analysis": raw_content, "link": ""}]
