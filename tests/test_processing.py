import pytest
from unittest.mock import patch, MagicMock
from src.processing.llm_processor import AIProcessor
from src.ingestion.rss_parser import Article

@patch("src.processing.llm_processor.OpenAI")
def test_ai_summarization(mock_openai):
    """测试调用 AIProcessor.summarize() 能否正确传输分类且返回结构化 JSON"""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # 模拟 openai 返回了一段被包裹起来的 JSON
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = '''
    ```json
    [
        {"title": "FastAPI发布", "summary": "极其好用的框架发布了1.0版本", "analysis": "利好后端开发"}
    ]
    ```
    '''
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client.chat.completions.create.return_value = mock_response

    mock_articles = [
        Article(
            id="test_1",
            title="FastAPI 1.0 released",
            summary="FastAPI has reached stable 1.0 release.",
            link="http://fastapi.tiangolo.com",
            source="Tech News"
        )
    ]
    
    processor = AIProcessor(api_key="fake_key", base_url="fake_url")
    result = processor.summarize(mock_articles, category_name="AI科技", model_name="gpt-3.5")
    
    mock_client.chat.completions.create.assert_called_once()
    
    # API 接口现在应该要求模型返回结构化的 List[Dict] 对象
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["title"] == "FastAPI发布"
