@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
python -m src.api
pause