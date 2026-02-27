import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from src.ingestion.source_manager import SourceManager
from src.ingestion.rss_parser import parse_rss_string, Article
from src.storage.history import HistoryManager
from src.processing.llm_processor import AIProcessor
import subprocess
import json
import sys

# 移除原有的 requests 和 fetch_rss_content，不再需要实时在 API 层抓取

# ---- 初始化 FastAPI 应用 ----
app = FastAPI(title="News Push Backend API", version="1.0.0")

# 允许跨域，方便前端分离开发访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 数据模型 ----
class CategoryResponse(BaseModel):
    categories: List[str]

# 废弃原 NewsRequest 结构，因为现在是大盘模式而不是单一分类拿取

# ---- 挂载前端页面路由 ----
# 为 /static 提供静态资源
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# 为根路径提供 index.html 以实现 SPA 访问
@app.get("/")
def serve_index():
    index_path = os.path.join(os.getcwd(), "src", "web", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found"}

# ---- 原有业务路由接口 ----
@app.get("/api/categories", response_model=CategoryResponse)
def get_categories():
    """获取系统当前支持的所有资讯分类"""
    manager = SourceManager()
    categories_dict = manager.get_active_categories()
    if not categories_dict:
        raise HTTPException(status_code=500, detail="无可用信源或配置加载失败")
    return {"categories": list(categories_dict.keys())}
    
@app.get("/api/news/latest")
def get_latest_news():
    """读取本地最新产出的全量静态热榜数据"""
    snapshot_path = os.path.join(os.getcwd(), "output", "latest_news.json")
    if not os.path.exists(snapshot_path):
        return {"data": {}, "message": "尚未生成全量快照"}
        
    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"data": data}
    except Exception as e:
        logging.error(f"读取由于快照失败: {e}")
        raise HTTPException(status_code=500, detail="解析全量缓存数据失败")

@app.post("/api/news/refresh")
def refresh_news_pipeline():
    """手动调用流水账后端脚本强制更新最新大盘快照"""
    try:
        # 非阻塞派发进程
        # 因为我们是在 venv 下运行的，可以复用当前进程的环境
        script_path = os.path.join(os.getcwd(), "main.py")
        subprocess.Popen([sys.executable, script_path])
        return {"message": "已在后台派发流水线更新任务。"}
    except Exception as e:
        logging.error(f"派发更新任务失败: {e}")
        raise HTTPException(status_code=500, detail="启动更新指令失败")

@app.get("/health")
def health_check():
    return {"status": "ok"}
