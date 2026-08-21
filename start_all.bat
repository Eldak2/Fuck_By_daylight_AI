@echo off
cd /d "C:\Users\aleks\Documents\Projects\Fuck_By_Daylight_AI"

set PYTHONW=C:\Users\aleks\miniconda3\pythonw.exe
set PYTHON=C:\Users\aleks\miniconda3\python.exe
set COMBAT_PYTHON=C:\Users\aleks\miniconda3\envs\combat\python.exe

echo Запуск API (без окна)...
start "" %PYTHONW% -c "from src.api import run_api; run_api()"

echo Запуск CombatVLA (без окна)...
start "" %COMBAT_PYTHON% C:\Users\aleks\Documents\Projects\CombatVLA\combat_server.py

echo Запуск оверлея (без окна)...
start "" %PYTHONW% main.py

echo Все сервисы запущены!
exit