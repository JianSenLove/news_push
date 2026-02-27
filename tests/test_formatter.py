import os
import pytest
from src.delivery.markdown_generator import MarkdownGenerator

def test_markdown_generator_output(tmp_path):
    """测试将 AI 内容渲染为 Markdown 文件并保存到本地"""
    
    # 模拟输入参数
    ai_summary_content = "【AI 前沿】\n这是今天的新闻：\n- GPT-4 发布了。\n"
    
    # 创建渲染器，将输出目录指向 pytest 的临时目录 tmp_path
    generator = MarkdownGenerator(output_dir=str(tmp_path))
    
    # 执行生成
    file_path = generator.generate(ai_summary_content)
    
    # 验证文件是否存在且合法
    assert os.path.exists(file_path), "Markdown file should be created"
    assert file_path.endswith(".md"), "File should end with .md"
    
    # 验证文件内容是否正确拼装
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "# 每日科技前沿赛博冲浪内参" in content
        assert "这是今天的新闻：" in content
