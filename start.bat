@echo off
setlocal
chcp 65001 >nul
title StoreFlow Demo
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [StoreFlow] Create the Python 3.12 environment first:
  echo python -m venv .venv
  echo .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "%~dp0main.py" %*
set task_exit=%errorlevel%
if not "%task_exit%"=="0" pause
exit /b %task_exit%
