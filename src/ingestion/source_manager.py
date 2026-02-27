import json
import logging
import requests
from typing import List, Dict

class SourceManager:
    def __init__(self, config_path: str = "config/sources.json"):
        self.config_path = config_path
        # 解析的新结构是一个 {"类别名称": [大堆配置]} 的字典
        self.categories: Dict[str, List[Dict[str, str]]] = self._load_config()
        
    def _load_config(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("categories", {})
        except FileNotFoundError:
            logging.warning(f"未能找到配置文件 {self.config_path}，使用空配置。")
            return {}
        except Exception as e:
            logging.error(f"解析配置文件失败: {e}")
            return {}
            
    def get_active_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """
        遍历所有的分类下的所有信号源，发送轻量级的 HTTP GET 请求，过滤掉超时或报错的渠道。
        返回可用的分类及信号源结构树。
        """
        active_cats = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for category_name, sources in self.categories.items():
            active_list = []
            for src in sources:
                url = src.get("url")
                name = src.get("name")
                if not url:
                    continue
                    
                try:
                    # 给一个极短的探测超时阈值，例如 10 秒
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        active_list.append(src)
                    else:
                        logging.warning(f"渠道异常 [{name}]: HTTP {resp.status_code}")
                except requests.exceptions.Timeout:
                    logging.warning(f"渠道超时被剔除 [{name}]: {url}")
                except Exception as e:
                    logging.warning(f"渠道请求失败被剔除 [{name}]: {e}")
                    
            if active_list:
                active_cats[category_name] = active_list
                
        return active_cats
