@echo off
echo ========================================
echo 🚀 启动社交媒体趋势分析系统 (简化版)
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 检查虚拟环境...
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

echo.
echo 🔧 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 📦 安装依赖...
pip install -r requirements.txt

echo.
echo 🌐 启动后端服务 (端口8001)...
start "Backend Server" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload && pause"

echo.
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak > nul

echo.
echo 🌐 启动前端开发服务器 (端口5173)...
cd /d "%~dp0social-trend-analyzer"
start "Frontend Server" cmd /c "npm run dev && pause"

echo.
echo ========================================
echo ✅ 系统启动完成！
echo 🌐 后端API: http://localhost:8001
echo 📚 API文档: http://localhost:8001/docs
echo 🖥️  前端界面: http://localhost:5173
echo ========================================
pause