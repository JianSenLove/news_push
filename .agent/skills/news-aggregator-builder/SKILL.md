---
name: news-aggregator-builder
description: 这是一个全面且细节丰富的架构与落地指南，用于构建低延迟、解耦式的新闻聚合 SPA (基于静态响应的单页应用)。当用户要求搭建自动化的 RSS 爬虫系统、AI 摘要与提炼流水线，或者要求创建一个高性能的 Web 资讯冲浪面板（如 Cyber Surfer）时，请务必阅读和使用此技能。
license: Complete terms in LICENSE.txt
---

# 新闻聚合与快速 Web 渲染构建指南

## 技能概览 (Overview)
本技能提取自一个真实的、经过重重迭代与踩坑的“赛博冲浪面板”项目。它展示了如何构建一个端到端的自动化信息聚合平台。
这套架构的核心哲学是：**极致的动静拆分 (Extreme Decoupling)**。即后端（Python）只负责爬取与重度 AI 运算，并将最终结果渲染为纯静态文件；而前端浏览器层只需进行一次数据加载，后续的用户交互（如切页、查看摘要）全部通过操作内存中的 JS 对象完成，达到绝对 0 延迟的用户体验。

## 核心架构设计 (Core Architecture)

### 1. 数据的多维流转 (Data Pipeline)
*   **配置层**：使用 `sources.json` 维护目标 RSS/Atom 源。数据按照“大类 (Category) -> 具体的资讯源头”进行嵌套组织。
*   **爬虫与解析层**：Python 使用 `feedparser` 和 `requests` 模块。必须处理好异常捕获（如：当某个站点引发 HTTP 403 或 404 时，仅做 Warning 记录，决不能中断整个大盘聚合的进程）。
*   **AI 提炼层**：通过调用大语言模型 (LLM) 获取摘要。应当在 Prompt 中约束 AI 仅返回严格的 JSON 数组（包含如：`title`, `link`, `summary`, `analysis` 等字段）。
*   **双写输出落盘**：Pipeline 运行完毕后，除了传统的 Markdown 推送报告外，**必须**输出一份全局结构的静态缓存字典，例如 `output/latest_news.json`。这个文件是 Web 界面达到秒开的关键。

### 2. 衔接与调度 API (Minimal API Layer)
不要用 FastAPI/Django 承载实时计算！API 层只应当做两件事：
*   **极速分发** (`GET /api/news/latest`)：直接读取并返回硬盘上备好的 `latest_news.json` 静态文件。不含任何复杂查询，确保毫秒级响应。
*   **后台唤起** (`POST /api/news/refresh`)：由于 Python 不借助 Celery 等重武器，可直接在此接口中使用非阻塞的 `subprocess.Popen` 调用爬虫主脚本 (`main.py`) 的方式让后台暗中发力。

### 3. 前端零开销渲染 (Zero-Latency SPA)
*   **摒弃框架化重负**：使用纯正的 Vanilla JS (原生 HTML/CSS/JS)。无需 Vue 或 React 即可达到极高质感。
*   **一次性加载机制**：用户每次完整打开网页，仅在生命周期的 `bootApplication` 阶段进行一次网络请求，拿到 `latest_news.json` 中全部分类的数据，保存在内存对象（如 `globalSnapshot`）中。
*   **DOM 重绘切页**：当用户点击侧边栏的任何一个分类（Tab）时，直接对 `globalSnapshot` 进行键值获取，然后把字符串模板（Template Literal） `innerHTML` 映射到主视图容器里，这样即便断网，切页也依旧行云流水。

## 关键代码模块 (Resources)

为了让代码更清晰，本技能将后端的 FastAPI 薄层设计与前端的 JS 页面设计代码分别存放在了引用文档中。
当你需要详细的实现代码时：
*   关于如何写出规范的后台任务分发与静态端点，请阅读: `references/backend_structure.md`
*   关于如何搭建一个高性能的基于内存接管的纯 JS 前端逻辑，请阅读: `references/frontend_pattern.md`

## 常见开发陷阱与防范规范 (Gotchas & Best Practices)

1.  **子进程环境变量丢失 (Subprocess ModuleNotFoundError)**：
    当在 API (`server.py`) 内部通过 `subprocess.Popen` 无阻塞唤起同级的 `main.py` 脚本时。**绝对不要**写 `"python"`。如果系统安装了全局 Python，会导致当前 virtual environment 的 `requirements.txt` (比如找不到 requests 库) 丢失。
    **✅ 规范做法：** 必须使用 `sys.executable` : `subprocess.Popen([sys.executable, "main.py"])`。
2.  **Lucide 图标库的 DOM 破坏性**：
    为了追求精美的赛博/极客视觉，常使用 `lucide.js`。要注意，当调用 `lucide.createIcons()` 后，原本你写的 `<i data-lucide="refresh-cw"></i>` 在网页的真实 DOM 环境中会变成 `<svg>` 节点。
    此时如果在 JS 的 Catch 中依然调用 `document.querySelector('i').classList.remove(...)` 就会报 Null 异常！
    **✅ 规范做法：** 在获取 DOM 时采用回退机制：`const icon = el.querySelector('svg') || el.querySelector('i');` 然后一定要包裹 `if (icon)` 判空逻辑。
3.  **UI 状态流转保障**：
    由于我们的 API 存在“后台默默排产”的情况。所以在手动触发抓取时，一定要在界面上给予明显反馈（让大盘回退到 Loading 或 Welcome 状态），然后再告诉用户：“指令已发送至后台流水线，全网搜罗耗时较长，请稍后自行按 F5 刷新”。
4.  **安全基建**：
    切忌在任何文件写死 API Key 或 Webhook，请严格挂载 `dotenv` 组件从 `.env` 按需读取。
