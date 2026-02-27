import pytest
from unittest.mock import patch, MagicMock
from main import run_pipeline
from src.ingestion.rss_parser import Article

@patch("main.fetch_rss_content")
@patch("main.parse_rss_string")
@patch("main.SourceManager")
@patch("main.HistoryManager")
@patch("main.AIProcessor")
@patch("main.MarkdownGenerator")
@patch("main.FeishuSender")
@patch("main.os.getenv")
@patch("builtins.open", new_callable=MagicMock)
def test_main_pipeline(mock_open, mock_getenv, mock_feishu, mock_md, mock_ai, mock_history, mock_source, mock_parse, mock_fetch):
    """测试整个资讯流流水线能否正常运转各部件"""
    
    # 环境变量 Mock
    def mock_env(key, default=None):
        if key == "FEISHU_WEBHOOK_URL":
            return "http://fake.url"
        return default
    mock_getenv.side_effect = mock_env
    
    # 网络层 Mock
    mock_fetch.return_value = "<fake_rss_xml>"
    
    # 解析 Mock (返回1篇文章)
    mock_article = Article("id1", "Title 1", "Summary 1", "http://l.com", "Src")
    mock_parse.return_value = [mock_article]
    
    # 历史记录 Mock (文章为新)
    mock_history_instance = MagicMock()
    mock_history_instance.is_exists.return_value = False
    mock_history.return_value = mock_history_instance
    
    # AI 拦截 Mock：现在应该返回 List[Dict]
    mock_ai_instance = MagicMock()
    mock_ai_instance.summarize.return_value = [{"title": "test_title", "summary": "t_summary", "analysis": "t_analysis", "link": "l_com"}]
    mock_ai.return_value = mock_ai_instance
    
    # Markdown 渲染 Mock
    mock_md_instance = MagicMock()
    mock_md_instance.generate.return_value = "fake_file.md"
    mock_md.return_value = mock_md_instance
    
    # 飞书推送 Mock
    mock_feishu_instance = MagicMock()
    mock_feishu_instance.send.return_value = True
    mock_feishu.return_value = mock_feishu_instance
    
    # 模拟读取刚才写入的文件内容交给飞书发
    file_handle = mock_open.return_value.__enter__.return_value
    file_handle.read.return_value = "Fake Markdown Content"

    # 源管理器 Mock: 现在需要返回分类字典模型
    mock_source_instance = MagicMock()
    mock_source_instance.get_active_categories.return_value = {
        "测试分类": [{"name": "test_src", "url": "http://test"}]
    }
    mock_source.return_value = mock_source_instance

    # 运行主流程 (使用自动读取到的源，即不传参)
    run_pipeline()
    
    # 断言每一层都被依次调用了
    mock_fetch.assert_called_once_with("http://test")
    mock_parse.assert_called_once_with("<fake_rss_xml>", "test_src")
    mock_history_instance.is_exists.assert_called_with("id1")
    mock_ai_instance.summarize.assert_called_once()
    
    # 之前传的是字符串，现在底层是被包进了新格式再下发给 generate
    mock_md_instance.generate.assert_called_once()
    
    mock_feishu_instance.send.assert_called_with("🏆 今日科技前沿赛博内参", "Fake Markdown Content")
    mock_history_instance.add.assert_called_with("id1")
