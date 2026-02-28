# 每日科技前沿赛博冲浪助手 (Cyber Surfer Assistant)

这是一个自动化的新闻资讯聚合与 AI 总结系统，同时包含了一个精美的定制化前端交互面板（Web SPA）。
它每天帮用户抓取最新的科技动态、资讯，并通过大语言模型（LLM）进行智能提炼总结，最后可以通过本地生成文档、推送到飞书或在其专门开发的独立页面上优雅地展示。

项目按照严格的 **TDD（测试驱动开发）** 模式进行构建，具备模块化、低延迟、解耦式的高性能架构。

---

## 🎯 核心功能与模块

1. **信源获取与解析 (Ingestion)**
   - 能够通过解析配置文件 `config/sources.json` 根据不同的类别（Category）聚合抓取 RSS/XML 源、推特以及技术论坛（如利用 RSSHub）的文章。
   - 具备渠道健康度探测能力，过滤失效链接。

2. **去重与纪录 (Storage)**
   - 采用本地轻量级访问历史记录，记录新闻 URL 等信息（基于 JSON 或 SQLite），对已抓取的新闻内容进行去重，防止重复推送和处理。

3. **AI 智能处理与摘要 (Processing)**
   - 接入了大语言模型（LLM），将抓取到的原生文章进行高质量阅读理解，提炼为一句话总结和深度分析。
   - 强制约束 AI 返回结构化的 JSON/字典结果，为后续排版与前端交互打好底层基础。

4. **多渠道输出分发 (Delivery)**
   - **本地归档**：可自动生成排版优美、包含分类与 Emoji 的 Markdown 文档，存放在 `output/`。
   - **自动化推送 (可选)**：支持配置飞书 Webhook 等，可以把加工提炼好的精简简报自动进行推流分发。

5. **极客 Web 冲浪面板 (Frontend SPA)**
   - 提供了一个专属的极其现代化的前沿网站！采用玻璃拟物、极客护眼夜间模式、卡片式布局以及流畅的悬停微操作。
   - **静态化解耦渲染架构**：不需要用户每次打开页面都去爬虫加载，后台流水线直接输出全维度静态快照 JSON（`latest_news.json` 供极速访问），配合纯原生 JS，点击任意一个品类 Tab 瞬间加载。

---

## 🛠️ 技术栈与工程规范

- **服务端语言环境**：Python 3.x
- **核心框架**：`FastAPI` 与 `Uvicorn`（提供高速轻量的异步 API 及静态页面承载）
- **大模型支持**：由于采取 `OpenAI SDK` 兼任转发策略，不仅支持原生 OpenAI 接口，也**完全支持兼容本地大模型或是三方代理中转计费平台**（通过自定义 API_KEY 和 BASE_URL）。
- **前端支持**：Vanilla HTML / JavaScript / CSS，强调极致加载体验，去除了笨重复杂的现代组件库层，追求纯粹。
- **开发与质控**：秉持 Test-Driven Development 哲学，引入 `pytest`；测试用例完备度极高，核心模块与第三方集成均存在完整的 Mock Test 拦截保障机制。

---

## 🤝 参与贡献与可选开发计划

本项目欢迎各位开发者的共同维护和参与！为了保证项目的规范与整洁，请仔细阅读以下文档：
- **开发规范**：请参阅 [🛠️ 团队协作与开发规范 (CONTRIBUTING.md)](./CONTRIBUTING.md)，包含分支管理、测试标准及 TASK 书写要求。
- **可选功能认领**：我们整理了大量的优化点，请查看 [🚀 可选功能开发与优化记录 (OPTIONS.md)](./OPTIONS.md)，并在开始开发前进行登记。
- **任务与计划追踪**：请将独立功能点开发通过附带 **TASK** 和 **PLAN** 的 Issue 提交，或建立项目内的日志文档（如 `task.md`）进行追踪定位。
- **核心配置文件**：系统的核心数据源与类目结构保存在 `config/sources.json` 中；环境变量与各种 API Key 等隐私配置存放在 `.env` 文件。

---

## 🚀 极其简单的启动指引

### 1. 快速克隆与环境配置（Mac / Linux / Windows 均适配）

进入项目的根目录，复制出 `.env` 的副本（由于 gitignore 保护了您的私人数据，请不要直接通过 git 提交）。
```bash
# 进入目录
cd news_push

# 基于样板创建真实的配置文件（如果是在 Mac/Linux）
cp .env.example .env

# （如在 Windows 系统）： 
# copy .env.example .env
```
随后请**打开 `.env` 文件**填入您的真实大模型相关接口、Model标识，以及飞书的 WebhookURL（如果不需要外网群推送，可以不修改它）。

### 2. 初始安装（配置虚拟环境）

确保您本机已经安装了 Python（>3.9），在命令行中执行：
```bash
# 激活 python3 虚拟环境
python3 -m venv venv

# Mac / Linux: 激活并在其中安装依赖
source venv/bin/activate
pip install -r requirements.txt

# Windows: 激活并在其中安装依赖
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 3. 一键挂载服务端 (FastAPI & 大屏看板)

当上述虚拟环境完备后，你可以通过对应的启动脚本，随时拉起它！

- **对于 Mac / Linux 用户**：
  直接在终端输入面板服务拉起指令：
  ```bash
  # 首次使用可先给脚本权限: chmod +x run_server.sh run_news.sh
  ./run_server.sh
  ```
  此时您的控制台会提示 `Uvicorn running on http://127.0.0.1:8000`。
  打开浏览器访问：[127.0.0.1:8000](http://127.0.0.1:8000/)，即刻体验！

- **对于 Windows 用户**：
  直接双击 `run_server.bat` 打开大屏看板面板。

### 4. 驱动后台人工刷新（数据管线作业）

除了启动挂载接口面板服务以外，有时候我们在晚上或空闲时手动抓一把最新的内容，可以通过运行手动刷新流水线脚本：
- **Mac / Linux 用户**: 执行 `./run_news.sh`
- **Windows 用户**: 执行 `run_news.bat`
*(当执行这部分脚本的时候，你可透过控制台日志观察到爬虫读取、大模型提炼压缩成文章快照并推流的全貌！这亦是 TDD 验证的主战场)*

---

🌟 **Have Fun and Happy Surfing of the Latest Tech Info!** 🌟
