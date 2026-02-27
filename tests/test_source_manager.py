import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.ingestion.source_manager import SourceManager

def test_source_manager_read_categories(tmp_path):
    """测试 SourceManager 读取基于频道分类结构的新版 JSON"""
    mock_config = {
        "categories": {
            "科技": [
                {"name": "TechNews", "url": "http://tech.example.com"}
            ],
            "生活": [
                {"name": "LifeStyle", "url": "http://life.example.com"},
                {"name": "BadSource", "url": "http://bad.example.com"}
            ]
        }
    }
    
    config_file = tmp_path / "sources.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(mock_config, f)
        
    manager = SourceManager(config_path=str(config_file))
    
    assert "科技" in manager.categories
    assert "生活" in manager.categories
    assert len(manager.categories["生活"]) == 2

    # 测试可用性探测，预期 BadSource 会被剔除
    def mock_requests_get(url, **kwargs):
        if "bad" in url:
            raise Exception("Timeout")
        resp = MagicMock()
        resp.status_code = 200
        return resp
        
    with patch("src.ingestion.source_manager.requests.get", side_effect=mock_requests_get):
        active_cats = manager.get_active_categories()
        
        # 结果应保留两类
        assert len(active_cats["科技"]) == 1
        assert len(active_cats["生活"]) == 1
        assert active_cats["生活"][0]["name"] == "LifeStyle"

