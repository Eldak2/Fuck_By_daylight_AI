@echo off
title Fuck_By_Daylight_AI - API
echo ========================================
echo   🔥 Fuck_By_Daylight_AI API Сервер
echo   📡 Запуск на http://127.0.0.1:5000
echo ========================================
echo.

cd /d "%~dp0"

if not exist .env (
    echo ⚠️ .env не найден! Копирую из .env.example
    copy .env.example .env
)

set PYTHON=C:\Users\aleks\miniconda3\python.exe

echo 🚀 Запуск API...
%PYTHON% -c "import sys; sys.path.insert(0, '.'); from src.api import run_api; run_api()"