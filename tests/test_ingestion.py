import pytest
from src.ingestion.rss_parser import parse_rss_string, Article

def test_parse_rss_string():
    """测试给定的 RSS/XML 字符串能被正确提取回 Article 列表"""
    mock_rss = """
    <rss version="2.0">
        <channel>
            <title>Mock Hacker News</title>
            <item>
                <title>Show HN: My new TDD tool</title>
                <link>https://news.ycombinator.com/item?id=123</link>
                <description>A cool tool built with Python.</description>
            </item>
            <item>
                <title>Ask HN: AI in 2026?</title>
                <link>https://news.ycombinator.com/item?id=124</link>
                <description>What are your thoughts on AI?</description>
            </item>
        </channel>
    </rss>
    """
    
    articles = parse_rss_string(mock_rss, source_name="Mock Hacker News")
    
    # 验证文章数量
    assert len(articles) == 2
    
    # 验证第一篇文章实体的具体字段结构和内容
    first_article = articles[0]
    assert isinstance(first_article, Article)
    assert first_article.title == "Show HN: My new TDD tool"
    assert first_article.link == "https://news.ycombinator.com/item?id=123"
    assert first_article.summary == "A cool tool built with Python."
    assert first_article.source == "Mock Hacker News"
    assert first_article.id == "https://news.ycombinator.com/item?id=123" # 默认使用 link 做 id
