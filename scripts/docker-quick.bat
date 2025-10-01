@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Docker 快速操作脚本
REM ========================================

set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

if "%1"=="" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help

if "%1"=="dev" goto :start_dev
if "%1"=="prod" goto :start_prod
if "%1"=="test" goto :start_test
if "%1"=="stop" goto :stop_all
if "%1"=="restart" goto :restart
if "%1"=="logs" goto :show_logs
if "%1"=="status" goto :show_status
if "%1"=="clean" goto :clean_all
if "%1"=="build" goto :build_all
if "%1"=="reset" goto :reset_all

echo %RED%错误: 未知命令 '%1'%NC%
echo.
goto :show_help

:show_help
echo %BLUE%Docker 快速操作脚本%NC%
echo.
echo 用法: %0 [COMMAND] [OPTIONS]
echo.
echo 命令:
echo   dev                启动开发环境
echo   prod               启动生产环境
echo   test               启动测试环境
echo   stop               停止所有服务
echo   restart            重启服务
echo   logs [service]     查看日志
echo   status             查看服务状态
echo   build              构建所有镜像
echo   clean              清理未使用的镜像和容器
echo   reset              重置所有数据（危险操作）
echo.
echo 选项:
echo   -h, --help         显示此帮助信息
echo.
echo 示例:
echo   %0 dev             # 启动开发环境
echo   %0 logs backend    # 查看后端日志
echo   %0 clean           # 清理Docker资源
goto :end

:start_dev
echo %BLUE%启动开发环境...%NC%
if not exist "docker-compose.dev.yml" (
    echo %RED%错误: docker-compose.dev.yml 文件不存在%NC%
    goto :end
)

echo %YELLOW%正在拉取最新镜像...%NC%
docker-compose -f docker-compose.dev.yml pull

echo %YELLOW%正在启动开发服务...%NC%
docker-compose -f docker-compose.dev.yml up -d

if %errorlevel% equ 0 (
    echo %GREEN%✓ 开发环境启动成功！%NC%
    echo.
    echo %BLUE%服务访问地址:%NC%
    echo   前端: http://localhost:3000
    echo   后端: http://localhost:8000
    echo   Redis Commander: http://localhost:8081
    echo   Adminer: http://localhost:8080
    echo.
    echo %YELLOW%查看日志: %0 logs%NC%
    echo %YELLOW%停止服务: %0 stop%NC%
) else (
    echo %RED%✗ 开发环境启动失败%NC%
)
goto :end

:start_prod
echo %BLUE%启动生产环境...%NC%
if not exist "docker-compose.prod.yml" (
    echo %RED%错误: docker-compose.prod.yml 文件不存在%NC%
    goto :end
)

echo %YELLOW%正在构建生产镜像...%NC%
docker-compose -f docker-compose.prod.yml build

echo %YELLOW%正在启动生产服务...%NC%
docker-compose -f docker-compose.prod.yml up -d

if %errorlevel% equ 0 (
    echo %GREEN%✓ 生产环境启动成功！%NC%
    echo.
    echo %BLUE%服务访问地址:%NC%
    echo   应用: http://localhost
    echo   Grafana: http://localhost:3001
    echo   Prometheus: http://localhost:9090
    echo.
    echo %YELLOW%查看日志: %0 logs%NC%
    echo %YELLOW%停止服务: %0 stop%NC%
) else (
    echo %RED%✗ 生产环境启动失败%NC%
)
goto :end

:start_test
echo %BLUE%启动测试环境...%NC%
if not exist "docker-compose.yml" (
    echo %RED%错误: docker-compose.yml 文件不存在%NC%
    goto :end
)

echo %YELLOW%正在启动测试服务...%NC%
docker-compose up -d

if %errorlevel% equ 0 (
    echo %GREEN%✓ 测试环境启动成功！%NC%
    echo.
    echo %BLUE%服务访问地址:%NC%
    echo   前端: http://localhost:3000
    echo   后端: http://localhost:8000
    echo.
    echo %YELLOW%查看日志: %0 logs%NC%
    echo %YELLOW%停止服务: %0 stop%NC%
) else (
    echo %RED%✗ 测试环境启动失败%NC%
)
goto :end

:stop_all
echo %BLUE%停止所有服务...%NC%

if exist "docker-compose.dev.yml" (
    echo %YELLOW%停止开发环境...%NC%
    docker-compose -f docker-compose.dev.yml down
)

if exist "docker-compose.prod.yml" (
    echo %YELLOW%停止生产环境...%NC%
    docker-compose -f docker-compose.prod.yml down
)

if exist "docker-compose.yml" (
    echo %YELLOW%停止测试环境...%NC%
    docker-compose down
)

echo %GREEN%✓ 所有服务已停止%NC%
goto :end

:restart
echo %BLUE%重启服务...%NC%
call :stop_all
echo.
if exist ".current-env" (
    set /p current_env=<.current-env
    if "!current_env!"=="development" call :start_dev
    if "!current_env!"=="production" call :start_prod
    if "!current_env!"=="testing" call :start_test
) else (
    echo %YELLOW%未检测到当前环境，请手动指定环境启动%NC%
)
goto :end

:show_logs
if "%2"=="" (
    echo %BLUE%显示所有服务日志...%NC%
    docker-compose logs -f
) else (
    echo %BLUE%显示 %2 服务日志...%NC%
    docker-compose logs -f %2
)
goto :end

:show_status
echo %BLUE%Docker 服务状态:%NC%
echo.
docker-compose ps
echo.
echo %BLUE%Docker 镜像:%NC%
docker images | findstr "social-trend"
echo.
echo %BLUE%Docker 网络:%NC%
docker network ls | findstr "social-trend"
goto :end

:build_all
echo %BLUE%构建所有镜像...%NC%

if exist "docker-compose.dev.yml" (
    echo %YELLOW%构建开发镜像...%NC%
    docker-compose -f docker-compose.dev.yml build
)

if exist "docker-compose.prod.yml" (
    echo %YELLOW%构建生产镜像...%NC%
    docker-compose -f docker-compose.prod.yml build
)

echo %GREEN%✓ 镜像构建完成%NC%
goto :end

:clean_all
echo %BLUE%清理Docker资源...%NC%
echo %YELLOW%警告: 这将删除未使用的镜像、容器和网络%NC%
set /p confirm="确认继续？(y/N): "
if /i "!confirm!"=="y" (
    echo %YELLOW%正在清理...%NC%
    docker system prune -f
    docker volume prune -f
    echo %GREEN%✓ 清理完成%NC%
) else (
    echo %YELLOW%已取消清理操作%NC%
)
goto :end

:reset_all
echo %RED%危险操作: 重置所有数据%NC%
echo %YELLOW%这将删除所有容器、镜像、卷和网络%NC%
set /p confirm="确认继续？(y/N): "
if /i "!confirm!"=="y" (
    echo %YELLOW%正在重置...%NC%
    call :stop_all
    docker system prune -a -f --volumes
    echo %GREEN%✓ 重置完成%NC%
) else (
    echo %YELLOW%已取消重置操作%NC%
)
goto :end

:end
endlocal