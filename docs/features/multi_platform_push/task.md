# 开发进程与 TDD 打卡单

*在此处严格按照 TDD 拆分测试和实现步骤。请直接在此处打钩追踪进度以确保下一个 Agent 能无损接手。*

- [ ] [RED] 编写 `tests/test_dingtalk.py`，模拟传入 Markdown，断言是否按照钉钉机器人的文档构建出了正确的 JSON Payload 以及发出了 POST 请求。
- [ ] [GREEN] 创建并实现 `src/delivery/dingtalk_sender.py`。
- [ ] [RED] 编写 `tests/test_telegram.py`，模拟传入长文本 Markdown，由于 TG 字数限制，需断言实现了切片发送或正确调用了 Telegram Bot API。
- [ ] [GREEN] 创建并实现 `src/delivery/telegram_sender.py`。
- [ ] [REFACTOR] 提取共用的 `BaseSender` 抽象类，规范所有推送模块的网络重试机制（Retries）和错误日志记录。
