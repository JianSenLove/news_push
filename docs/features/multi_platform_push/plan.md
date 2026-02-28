# 架构与实现计划 (Implementation Plan)

## 1. 痛点分析与目标
系统应当支持更多类型的目标端推送渠道。目前耦合在主逻辑中的仅有 Feishu。

## 2. 核心模块与系统设计 (Proposed Changes)
通过工厂模式 (Factory Pattern) 或外观模式 (Facade Pattern) 在 `main.py` 统一下发：
```python
def deliver_all(markdown_text: str):
    if settings.DINGTALK_WEBHOOK:
        DingtalkSender().send(markdown_text)
    if settings.TG_BOT_TOKEN:
        TelegramSender().send(markdown_text)
```

抽象出 BaseSender 并在对应的 `sender.py` 处理自己的网络重试和限流。

## 3. 验证与部署 (Verification)
1. 用户在 `.env` 中填入有效的钉钉 Webhook URL。
2. 运行 `main.py`。
3. 查看对应钉钉群是否漂亮地收到了以 Markdown 格式排版的早报。
