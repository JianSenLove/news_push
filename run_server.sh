#!/usr/bin/env bash

echo "========================================="
echo "====== News Push Backend API Server ======"
echo "========================================="
echo ""

# 自动获取脚本所在目录作为工作目录
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$PROJECT_DIR" || exit 1

# 检查虚拟环境是否存在
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment 'venv' not found."
    echo "Please create it using: python3 -m venv venv and install requirements."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Starting FastAPI with Uvicorn on http://127.0.0.1:8000 ..."
echo "[Tip] Press Ctrl+C to stop the server."
echo ""

# 启动服务端
python -m uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000
