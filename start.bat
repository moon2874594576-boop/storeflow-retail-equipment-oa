@echo off
chcp 65001 >nul
title 企业OA办公系统 - 启动脚本

echo ========================================
echo     企业OA办公系统 启动脚本
echo ========================================
echo.

REM 检查 Python 环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查 Node.js 环境
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] 检测到 Python 环境
python --version

echo [信息] 检测到 Node.js 环境
node --version
npm --version

echo.
echo ========================================
echo     开始初始化项目
echo ========================================
echo.

REM 创建必要的目录
if not exist "backend\logs" mkdir "backend\logs"
if not exist "backend\staticfiles" mkdir "backend\staticfiles"

REM 后端设置
echo [1/6] 安装后端依赖...
cd backend
if not exist "venv" (
    echo [信息] 创建 Python 虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate

pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败
    deactivate
    cd ..
    pause
    exit /b 1
)
echo [1/6] 后端依赖安装完成 ✓

echo.
echo [2/6] 初始化数据库...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [错误] 数据库迁移失败
    deactivate
    cd ..
    pause
    exit /b 1
)
echo [2/6] 数据库初始化完成 ✓

echo.
echo [3/6] 加载初始数据...
python init_data.py
if %errorlevel% neq 0 (
    echo [错误] 初始数据加载失败
    deactivate
    cd ..
    pause
    exit /b 1
)
echo [3/6] 初始数据加载完成 ✓

echo.
echo [4/6] 收集静态文件...
python manage.py collectstatic --noinput -q 2>nul
echo [4/6] 静态文件收集完成 ✓

deactivate
cd ..

REM 前端设置
echo.
echo [5/6] 安装前端依赖...
cd frontend
if not exist "node_modules" (
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
) else (
    echo [信息] 前端依赖已安装，跳过...
)
echo [5/6] 前端依赖安装完成 ✓

echo.
echo [6/6] 构建前端生产版本...
call npm run build
if %errorlevel% neq 0 (
    echo [错误] 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo [6/6] 前端构建完成 ✓

cd ..

echo.
echo ========================================
echo     项目初始化完成！
echo ========================================
echo.
echo [信息] 正在启动后端服务器 (端口: 8000)...
start "Django Backend" cmd /c "cd backend && call venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

echo [信息] 等待后端启动...
timeout /t 3 /nobreak >nul

echo [信息] 正在启动前端开发服务器 (端口: 5173)...
start "Vue Frontend" cmd /c "cd frontend && call npm run dev"

echo.
echo ========================================
echo     服务已启动！
echo ========================================
echo.
echo   后端API: http://localhost:8000/
echo   前端页面: http://localhost:5173/
echo   管理后台: http://localhost:8000/admin/
echo.
echo   默认账号:
echo     管理员: admin / admin123
echo     经理:   manager / manager123
echo     员工:   employee / employee123
echo.
echo   按任意键退出（服务将继续运行）...
echo ========================================
pause >nul
