@echo off
title Установка автозапуска
echo ========================================
echo   🔥 Установка автозапуска
echo   Fuck_By_Daylight_AI будет запускаться
echo   при старте Windows
echo ========================================
echo.

cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Запустите от имени администратора!
    pause
    exit /b 1
)

set "PROJECT_PATH=%~dp0"
set "BAT_PATH=%PROJECT_PATH%start_all.bat"

echo 📋 Создание задачи в планировщике Windows...
schtasks /create /tn "Fuck_By_Daylight_AI" /tr "%BAT_PATH%" /sc onlogon /delay 0000:30 /ru "%USERNAME%" /rl HIGHEST /f

if errorlevel 1 (
    echo ❌ Не удалось создать задачу!
    pause
    exit /b 1
)

echo ✅ Задача создана! При следующем входе в систему агент запустится автоматически.
echo.
pause