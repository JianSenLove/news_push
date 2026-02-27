# 后端 FastAPI 极简架构蓝图 (Backend FastAPI Blueprint)

在构建解耦（Decoupled）架构的 Web 应用时，后端的角色应当被极度简化。特别是在融合了高耗时的 AI 大模型提炼环节时，我们**绝对不能**在单个 HTTP 请求的生命周期内去同步调用耗时数千毫秒的 OpenAI/LLM 接口。

后端的唯一使命是：
1. **提供静态归档**的 0 延迟读取。
2. **异步派遣**计算密集型的脚本进程。

## Python 服务器核心示例 (`server.py`)

这套模板采用 `FastAPI` 和内置的异步语法，可以直接供前端的 Vanilla JS 进行无缝衔接。

```python
import os
import subprocess
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="赛博冲浪面板 - 极速后端")

# 在开发阶段放开 CORS 跨域限制
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 约定静态数据挂载路径
OUTPUT_FILE = os.path.join("output", "latest_news.json")

# 【端点 1】: 闪电般极速的数据分发接口
# 注意：该接口不含任何计算逻辑，仅供读取硬盘中的最新 JSON 字典供前端渲染。
@app.get("/api/news/latest")
async def get_latest_news():
    if not os.path.exists(OUTPUT_FILE):
        return {"data": {}, "message": "全网数据快照尚未生成"}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件加载异常: {str(e)}")

# 【端点 2】: “阅后即焚式”的后台任务触发器
# 通过这个接口，Web 端按下 “刷新/重新抓取” 按钮后立刻返回结果响应，而将耗时的网虫程序挂在后台进程缓慢工作。
@app.post("/api/news/refresh")
async def trigger_refresh():
    try:
        # 你的主业务爬虫与大模型对话逻辑应存在这儿： main.py
        script_path = os.path.join(os.getcwd(), "main.py")
        
        # 💣 致命陷阱提示：
        # 这里严禁使用 subprocess.Popen(["python", script_path])！
        # 在某些环境或 pm2 守卫进程中，"python" 变量可能越过虚拟环境直接找到主机的 Base Python。
        # 这里必须显式地用当前环境变量中的执行器 sys.executable！
        subprocess.Popen([sys.executable, script_path])
        return {"message": "后台全网探测和洗稿流水线已下放运行。"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 挂载单页面应用 (SPA) 到根目录
# 要求：在根目录下拥有 src/web 文件夹，其中包含 index.html 和样式、脚本
app.mount("/", StaticFiles(directory="src/web", html=True), name="web")
```

## 注意事项与拓展

- **权限设计**：如果你的站点是要暴露在公网，且爬取成本非常高（如消耗大量 OpenAI Token），请务必在 `/api/news/refresh` 上增加鉴权（如 Header 校验或 Token `Depends`），防止恶意攻击者无限刷光你的 API 额度。
- **锁机制 (Locking)**：为避免同一个用户连点 10 次后台，导致主计算机内存溢出并派发 10 个 main.py，最好在服务端设置一个轻量级的文件锁机制。当已有流水线运行时阻断新的任务。
