# 开发进程与 TDD 打卡单

*这是一项以纯前端 DOM 操控和轮询为主的特性，传统的 Python `pytest` 无法直接覆盖 DOM。开发时重心在于控制反转与状态呈现的测试。*

- [ ] [RED] 分析 `app.js`，设计一个新的 `autoRefreshAndRender()` 函数并构造 Mock 测试状态。
- [ ] [GREEN] 在 `app.js` 中拦截刷新按钮的事件，改写为异步 `fetch()` 调用触发后端，并设置轮询探测后端数据的变化。
- [ ] [REFACTOR] 优化 Loading 动画（Skeleton Screen）在刷新期间的展示逻辑。
