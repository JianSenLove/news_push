import os
import datetime

class MarkdownGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def generate(self, content: str) -> str:
        """生成并保存 Markdown 格式的排版资讯文件，返回保存的绝对路径"""
        # 为了防止同日多次运行产生覆盖，增加时分秒的时间戳
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        
        md_content = f"# 每日科技前沿赛博冲浪内参 ({today_str})\n\n"
        md_content += "---\n\n"
        md_content += content
        
        file_name = f"{today_str}_{time_str}-dailynews.md"
        file_path = os.path.join(self.output_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        return file_path
