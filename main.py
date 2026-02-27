import os
import logging
import requests
import datetime
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from src.ingestion.rss_parser import parse_rss_string, Article
from src.ingestion.source_manager import SourceManager
from src.storage.history import HistoryManager
from src.processing.llm_processor import AIProcessor
from src.delivery.markdown_generator import MarkdownGenerator
from src.delivery.feishu_sender import FeishuSender

def fetch_rss_content(url: str) -> str:
    try:
        logging.info(f"正在抓取: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.warning(f"抓取失败 {url}: {e}")
        return ""

def run_pipeline(sources: List[dict] = None):
    """
    全自动资讯流管道
    1. 真实网络抓取多路 RSS 解析
    2. 去重筛选
    3. AI 摘要
    4. 本地 Markdown 构建
    5. 飞书推送 (根据环境变量选填)
    """
    load_dotenv()
    
    # 初始化环境
    api_key = os.getenv("LLM_API_KEY", "dummy_key")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "")
    
    # 获取信源池机制
    if not sources:
        logging.info("正在初始化信源探测器并排除无效链路...")
        manager = SourceManager()
        # 由于现在是按类别获取，返回的是 Dict[str, List]
        categories_dict = manager.get_active_categories()
        if not categories_dict:
            logging.error("没有可用的信源配置或所有信源均无响应。")
            return
            
    # 为了组装带分类标题的精美 Markdown，我们需要分批拉取和分批总结
    ai_summary_markdown = (
        "# 《今日赛博冲浪内参》\n"
        f"**生成时点：** {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
        "**冲浪员：** 一位在代码和咖啡因中寻找平衡的赛博观察者\n\n"
        "---\n\n"
    )
    
    # 历史记录管理器
    history = HistoryManager("history.json")
    has_any_new_articles = False
    
    # 存储纯静态数据快照用于 Web 极速拉取
    latest_news_data: Dict[str, Any] = {}
    
    # 按大类遍历解析文章
    for category_name, category_sources in categories_dict.items():
        logging.info(f"== 正在处理分类: {category_name} ==")
        category_articles: List[Article] = []
        
        for src in category_sources:
            content = fetch_rss_content(src["url"])
            if content:
                parsed = parse_rss_string(content, src["name"])
                category_articles.extend(parsed[:5])
                
        # 针对当前分类过滤已读
        new_category_articles = []
        for art in category_articles:
            if not history.is_exists(art.id):
                new_category_articles.append(art)
                history.add(art.id)  # 顺便加入历史记录
                
        if not new_category_articles:
            logging.info(f"[{category_name}] 今日无新文章跳过。")
            continue
            
        has_any_new_articles = True
        logging.info(f"[{category_name}] 提取 {len(new_category_articles)} 篇待总结新文章")
        
        # 针对当前分类呼叫 AI 提炼
        try:
            processor = AIProcessor(api_key=api_key, base_url=base_url)
            # 拿到该分类的结构化 JSON Array
            ai_summary_json = processor.summarize(new_category_articles, category_name=category_name, model_name=model_name)
            
            # 将该分类存入静态快照数据中
            latest_news_data[category_name] = ai_summary_json
            
            # 立即拼装该分类的 Markdown 大纲 (恢复经典大厂排版)
            icon = "🔖"
            if "AI" in category_name or "黑客" in category_name:
                icon = "🚀"
            elif "极客" in category_name or "开发" in category_name:
                icon = "💻"
            elif "科技" in category_name or "生活" in category_name:
                icon = "🍉"
                
            ai_summary_markdown += f"### {icon} {category_name}\n\n"
            for idx, item in enumerate(ai_summary_json, 1):
                ai_summary_markdown += f"{idx}.  **{item.get('title', '未知标题')}**\n"
                ai_summary_markdown += f"    *   **摘要：** {item.get('summary', '')}\n"
                ai_summary_markdown += f"    *   **链接：** [{item.get('source', '原文链接')}]({item.get('link', '#')})\n"
                ai_summary_markdown += f"    *   **热评：** {item.get('analysis', '')}\n\n"
                
            ai_summary_markdown += "---\n\n"
            
        except Exception as e:
            logging.error(f"AI 处理分类 [{category_name}] 时失败: {e}")
            
    if not has_any_new_articles:
        logging.info("全站今日均无新文章产出，推送终止。")
        return

    # 步骤 4: 本地渲染 Markdown
    generator = MarkdownGenerator(output_dir="output")
    filename = generator.generate(ai_summary_markdown)
    logging.info(f"本地 Markdown 生成成功: {os.path.abspath(filename)}")
    
    # 步骤 4.5: 输出静态全量快照 JSON 供 Web 端极速读取
    try:
        snapshot_path = os.path.join("output", "latest_news.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(latest_news_data, f, ensure_ascii=False, indent=2)
        logging.info(f"本地 JSON 缓存快照更新成功: {os.path.abspath(snapshot_path)}")
    except Exception as e:
        logging.error(f"本地 JSON 缓存快照写入失败: {e}")
    
    # 步骤 5: 飞书推送 (可选)
    if webhook_url and "your_webhook_url_here" not in webhook_url:
        logging.info("检测到飞书 Webhook，正在发起推送...")
        sender = FeishuSender(webhook_url=webhook_url)
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        success = sender.send("🏆 今日科技前沿赛博内参", content)
        if success:
            logging.info("推送到飞书成功。")
        else:
            logging.warning("推送到飞书失败。")
    else:
        logging.info("未配置飞书 Webhook，已跳过线上群推送。")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("=========== 启动资讯采集流水线 ===========")
    run_pipeline()
    logging.info("=========== 本次任务执行完毕 ===========")

