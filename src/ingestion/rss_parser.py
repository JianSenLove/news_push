import feedparser
from dataclasses import dataclass
from typing import List

@dataclass
class Article:
    id: str
    title: str
    summary: str
    link: str
    source: str

def parse_rss_string(rss_string: str, source_name: str) -> List[Article]:
    """解析给定的 RSS/XML 字符串并返回 Article 对象列表"""
    feed = feedparser.parse(rss_string)
    articles = []
    
    for entry in feed.entries:
        article = Article(
            id=entry.get('link', ''),
            title=entry.get('title', ''),
            summary=entry.get('description', entry.get('summary', '')),
            link=entry.get('link', ''),
            source=source_name
        )
        articles.append(article)
        
    return articles
