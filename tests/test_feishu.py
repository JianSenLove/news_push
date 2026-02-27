import pytest
from unittest.mock import patch, MagicMock
from src.delivery.feishu_sender import FeishuSender

@patch("src.delivery.feishu_sender.requests.post")
def test_feishu_sender_success(mock_post):
    """测试飞书发送器能正确构造 payload 并发起 POST 请求"""
    
    # 构建 Mock 返回
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 0, "msg": "success"}
    mock_post.return_value = mock_response
    
    sender = FeishuSender(webhook_url="https://fake.feishu.url/webhook/123")
    
    markdown_text = "测试内容"
    result = sender.send("测试标题", markdown_text)
    
    # 验证请求被调用
    mock_post.assert_called_once()
    assert result == True
    
    # 验证发出去了含有 msg_type 和 content 的正确参数
    called_kwargs = mock_post.call_args.kwargs
    assert "json" in called_kwargs
    payload = called_kwargs["json"]
    assert "msg_type" in payload
    assert payload["msg_type"] == "interactive" or payload["msg_type"] == "text"
