import os
import pytest
from src.storage.history import HistoryManager

def test_history_manager_deduplication(tmp_path):
    """测试历史管理器能否正确持久化存储并去重"""
    test_db_path = tmp_path / "test_history.json"
    manager = HistoryManager(str(test_db_path))
    
    # 刚开始应该是不存在的
    assert manager.is_exists("123") == False
    
    # 存入一条数据
    manager.add("123")
    
    # 存入后应该是存在的
    assert manager.is_exists("123") == True
    
    # 模拟重启服务，重新加载同一个文件
    manager2 = HistoryManager(str(test_db_path))
    assert manager2.is_exists("123") == True
    assert manager2.is_exists("456") == False
