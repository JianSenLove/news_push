@echo off
REM 切换到项目目录
cd /d D:\project\news_push

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 执行主程序
python main.py

REM (可选) 如果你想在运行完保留窗口看一眼日志，可以取消下一行的注释
REM pause
