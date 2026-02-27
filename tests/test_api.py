import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("src.api.server.SourceManager")
def test_get_categories(mock_source_manager):
    # 模拟底座层 SourceManager 返回分类字典
    mock_instance = MagicMock()
    mock_instance.get_active_categories.return_value = {
        "AI科技": [{"name": "AI源", "url": "http://ai"}],
        "后端开发": [{"name": "Web源", "url": "http://web"}]
    }
    mock_source_manager.return_value = mock_instance
    
    response = client.get("/api/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "AI科技" in data["categories"]
    assert len(data["categories"]) == 2

@patch("os.path.exists")
@patch("builtins.open", new_callable=MagicMock)
def test_latest_news(mock_file, mock_exists):
    # 模拟 latest_news.json 存在且含有合法数据
    mock_exists.return_value = True
    
    mock_file.return_value.__enter__.return_value.read.return_value = '{"AI科技": [{"title": "新进展"}]}'
    
    response = client.get("/api/news/latest")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "AI科技" in data["data"]
    assert data["data"]["AI科技"][0]["title"] == "新进展"

@patch("subprocess.Popen")
def test_refresh_news(mock_popen):
    response = client.post("/api/news/refresh")
    assert response.status_code == 200
    assert response.json()["message"] == "已在后台派发流水线更新任务。"
    mock_popen.assert_called_once()
