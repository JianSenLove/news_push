# 每日科技前沿赛博冲浪助手 (Cyber Surfer Assistant) - TDD 执行看板

本看板基于 Test-Driven Development (TDD) 原则制定，确保每一个功能的开发都有测试用例覆盖，保证项目在长上下文或人员变更时依然能清晰溯源进度。项目语言为 Python 3.14.2，测试框架使用 `pytest`。

## 0. 环境配置与脚手架搭建 (Scaffolding First)
- [x] 0.1 初始化基础项目结构 (`src/`, `tests/`, `config/`, `.env.example`, `requirements.txt`)
- [x] 0.2 在 `d:\project\news_push` 创建虚拟环境并安装基础测试包 (`pytest`)
- [x] 0.3 编写一个极其基础的 `tests/test_env.py`，验证 `import pytest` 和项目路径引用是否成功

## 1. 核心模块 - 信源获取与解析 (Ingestion)
- [x] 1.1 **[RED]** 编写 `tests/test_ingestion.py` 测试：给定一段本地 Mock 的 RSS/XML 字符串，`FeedParser` 需要能成功提取出具有统一结构的 Article 对象列表 (标题、摘要、链接、来源)。
- [x] 1.2 **[GREEN]** 实现 `src/ingestion/rss_parser.py` 使 Mock 测试通过。
- [x] 1.3 **[REFACTOR]** 优化文章实体类的定义（例如使用 `dataclasses`）。

## 2. 核心模块 - 去重与存储 (Storage)
- [x] 2.1 **[RED]** 编写 `tests/test_storage.py` 测试：模拟将一条文章 ID (如 URL) 存入本地 JSON/SQLite，随后校验该 ID 判定为“已存在”。
- [x] 2.2 **[GREEN]** 实现本地防重模块 `src/storage/history.py`，让测试通过。

## 3. 核心模块 - AI 摘要处理 (Processing)
- [x] 3.1 **[RED]** 编写 `tests/test_processing.py` 测试：Mock掉真实的 API 请求，给入预设的 Article 列表，调用 `AIProcessor.summarize()` 应该返回结构化的总结对象/字典。
- [x] 3.2 **[GREEN]** 实现 `src/processing/llm_processor.py` 中的提示词(Prompt)装填。

## 4. 输出模块阶段一 - 本地排版与生成 (Delivery - Local Markdown)
- [x] 4.1 **[RED]** 编写 `tests/test_formatter.py`：输入来自 AI 的处理结果字典，校验是否能将其渲染为合法且美观的 Markdown 字符串，并成功将其写入到出参文件 `output/YYYY-MM-DD-dailynews.md` 中。
- [x] 4.2 **[GREEN]** 实现 `src/delivery/markdown_generator.py` 使其通过测试。此步必须确保每日内容在本地可以被完整构建并独立储存。

## 5. 输出模块阶段二 - 第三方推送集成 (Delivery - Feishu Optional)
- [x] 5.1 **[RED]** 编写 `tests/test_feishu.py`：注入 Mock 依赖，以读取前面的本地 Markdown 结果字符串为输入，验证是否正确发出了预期的 HTTP POST Payload 请求且不报错。
- [x] 5.2 **[GREEN]** 实现 `src/delivery/feishu_sender.py`，只有在设置了 Webhook 的情况下才执行飞书推送。

## 6. 项目串联与总调 (Main Pipeline)
- [x] 6.1 编写 `main.py` 脚本，将步骤 1 -> 2 -> 3 -> 4 -> [5] 连贯执行。
- [x] 6.2 编写端到端的流水线测试 `tests/test_main.py`，全部依赖 Mock 执行以确保胶水代码无语法或传递错误。

## 7. 接入真实网络架构并演示 (Live Run)
- [x] 7.1 读取真实的 `.env` 变量，使用真实的 LLM 进行请求，获取线上 RSS 摘要并保存本地。

## 8. 渠道规范化与可用性校验 (Source Config & Validation)
- [x] 8.1 建立配置文件 `config/sources.json` 以替代硬编码列表。
- [x] 8.2 **[RED]** 编写 `tests/test_source_manager.py` 测试 `SourceManager` 读取文件和有效性探测的功能。
- [x] 8.3 **[GREEN]** 实现 `src/ingestion/source_manager.py`。
- [x] 8.4 重构 `main.py`，接入 `SourceManager`，先校验渠道再抓取。

## 9. 渠道元数据增强与私域扩展 (Source Metadata)
- [x] 9.1 重写 `sources.json`，为每个抓取源添加 `desc` (描述) 字段。
- [x] 9.2 加入高价值私域渠道的推特、技术论坛（利用 RSSHub）。

## 10. 信源分类管理与底层重构 (Category Support)
- [x] 10.1 重新设计 `config/sources.json` 架构，按 `categories` 字典分类聚合渠道。
- [x] 10.2 重构 `SourceManager`，支持读取层级结构并可以按类别查询存活状态。
- [x] 10.3 重构 `AIProcessor`，使其处理数据时能够返回结构化 JSON/Dict 而不是强制排版好，便于前端二次渲染。
- [x] 10.4 修复 `main.py` 及遗留单元测试的接口兼容性。

## 11. 轻量级驱动引擎 API 化 (Backend API)
- [x] 11.1 更新依赖：安装 `fastapi` 与 `uvicorn`。
- [x] 11.2 **[RED]** 编写 `tests/test_api.py`，使用 `TestClient` 测试路由存活、传参验证及返回的数据结构。
- [x] 11.3 **[GREEN]** 实现 `src/api/server.py`，打通基础的 `/api/categories` 可用分类读取接口。
- [x] 11.4 **[GREEN]** 实现核心路由 `/api/news/generate`，将之前 `main.py` 的管线调度代码迁移/重构进异步的接口实现里。

## 12. 专属 Web 冲浪面板开发 (Frontend SPA)
- [x] 12.1 规划前端目录结构 `src/web/static` 与 `src/web/index.html`。
- [x] 12.2 开发基础设计系统 (`CSS` 样式)：强调现代设计感、极客护眼夜间模式、流畅的悬浮态与微交互。
- [x] 12.3 编写 `app.js` 逻辑 (1) - App 初始化时异步向 `/api/categories` 拉取大类标签并生成 Tab 导航栏。
- [x] 12.4 编写 `app.js` 逻辑 (2) - 点击大类标签时，展现加载动画(骨架屏)，并请求 `/api/news/generate`，最后以美观的新闻卡片将其渲染于主视窗。
- [x] 12.5 打包一键执行脚本：通过 `uvicorn` 直接通过 `server:app` 挂载前端页面，合并提供服务。

## 13. 静态化解耦渲染架构 (Static Data Decoupling)
- [x] 13.1 修改 `main.py` 的管线数据存储层：在原本向 `output/` 写 Markdown 文档的同时，增加生成全量分类数据快照 `latest_news.json`。
- [x] 13.2 **[RED]** 编写并打通 API 测试：测试 `/api/news/latest` 端点能否成功抛出底层刚刚构建出的全维度 JSON。
- [x] 13.3 **[GREEN]** 修改 `server.py`：新增 `/api/news/latest` (读取预存文件) 和 `/api/news/refresh` (手动热重载后台) 路由。
- [x] 13.4 修改前端 `app.js`：废弃“按需加载”，改为“一站式加载快照 + 全部内存映射切页”；并实现手动刷新大盘的按钮对接逻辑。
