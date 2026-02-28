#!/usr/bin/env bash

# 自动获取脚本所在目录作为工作目录（移除写死绝对路径，避免环境迁移报错）
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$PROJECT_DIR" || exit 1

# 检查并激活虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment 'venv' not found."
    echo "Please create it using: python3 -m venv venv and install requirements."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Running main pipeline..."
# 执行主程序跑爬虫洗稿流水线
python main.py

echo "Done."
