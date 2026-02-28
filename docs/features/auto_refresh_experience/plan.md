# 架构与实现计划 (Implementation Plan)

## 1. 痛点分析与目标
当前点击“刷新大盘”可能会发起一个阻塞的 Ajax 或者什么都没做。需要让前端感知到后端异步生成 Markdown 的结果。

## 2. 核心模块与系统设计 (Proposed Changes)
建议使用简单的轮询机制 (Polling) 或 Long-polling：
1. 点击 Refresh，向 `/api/news/refresh` 发起请求。
2. 前端每隔 3 秒请求一次 `/api/news/latest`，对比时间戳或 Hash。
3. 若发生更新，清空当前 DOM，基于最新的数据重新调用 `renderCards(data)`。

## 3. 验证与部署 (Verification)
1. 点击 Web 界面的“获取最新”按钮。
2. 观察控制台发出请求。
3. 等待约 10~30 秒（后端 AI 处理耗时），断言无需按 F5 页面即自动绘制出新抓取的新闻。
