#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_DIR}"

MODE="${1:-news}"
AUTO_OPEN=1
SERVER_HOST="${NEWS_PUSH_HOST:-127.0.0.1}"
SERVER_PORT="${NEWS_PUSH_PORT:-8010}"

if [ "${MODE}" = "server" ]; then
  for arg in "${@:2}"; do
    case "${arg}" in
      --no-open)
        AUTO_OPEN=0
        ;;
      --port=*)
        SERVER_PORT="${arg#*=}"
        ;;
      ''|*[!0-9]*)
        ;;
      *)
        SERVER_PORT="${arg}"
        ;;
    esac
  done
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[ERROR] Python is not installed."
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "[INFO] venv not found. Creating virtual environment..."
  "${PYTHON_BIN}" -m venv venv
fi

# shellcheck disable=SC1091
source "venv/bin/activate"

DEPS_MARKER="venv/.deps_installed"
if [ ! -f "${DEPS_MARKER}" ] || [ "requirements.txt" -nt "${DEPS_MARKER}" ]; then
  echo "[INFO] Installing/updating dependencies..."
  pip install -r requirements.txt
  touch "${DEPS_MARKER}"
fi

case "${MODE}" in
  news)
    echo "[INFO] Running news pipeline..."
    exec python main.py
    ;;
  server)
    URL="http://${SERVER_HOST}:${SERVER_PORT}/"
    echo "[INFO] Starting FastAPI server at ${URL} ..."
    echo "[TIP] Press Ctrl+C to stop."
    python -m uvicorn src.api.server:app --reload --host "${SERVER_HOST}" --port "${SERVER_PORT}" &
    SERVER_PID=$!

    if [ "${AUTO_OPEN}" -eq 1 ]; then
      # Wait briefly so browser opens after server starts listening.
      sleep 1
      if command -v open >/dev/null 2>&1; then
        if ! open "${URL}" >/dev/null 2>&1; then
          echo "[WARN] Failed to auto-open browser. Open this URL manually:"
          echo "       ${URL}"
        fi
      elif command -v xdg-open >/dev/null 2>&1; then
        if ! xdg-open "${URL}" >/dev/null 2>&1; then
          echo "[WARN] Failed to auto-open browser. Open this URL manually:"
          echo "       ${URL}"
        fi
      else
        echo "[WARN] Cannot find 'open' or 'xdg-open'. Open this URL manually:"
        echo "       ${URL}"
      fi
    fi

    wait "${SERVER_PID}"
    ;;
  *)
    echo "[ERROR] Unknown mode: ${MODE}"
    echo "Usage: ./run.sh [news|server] [port|--port=PORT] [--no-open]"
    exit 1
    ;;
esac
