@echo off
chcp 65001 >nul
title RonVideo2Pic

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not installed. Please install Python 3.8+
    echo Python 未安装，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM Check dependencies
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies... / 正在安装依赖...
    pip install -r requirements.txt
)

python video2pic.py

pause
