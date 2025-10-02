@echo off
echo 创建 Railway 部署包...

REM 创建临时部署目录
if exist deploy_package rmdir /s /q deploy_package
mkdir deploy_package

REM 复制必要文件
echo 复制核心文件...
copy Dockerfile.railway deploy_package\Dockerfile
copy railway.toml deploy_package\
copy requirements.txt deploy_package\

REM 复制 backend 目录（排除大文件）
echo 复制 backend 目录...
xcopy backend deploy_package\backend\ /E /I /Q ^
    /EXCLUDE:backend\.gitignore ^
    /EXCLUDE:backend\collected_data ^
    /EXCLUDE:backend\model_outputs ^
    /EXCLUDE:backend\logs ^
    /EXCLUDE:backend\uploads ^
    /EXCLUDE:backend\__pycache__ ^
    /EXCLUDE:backend\*.pyc

REM 创建压缩包
echo 创建压缩包...
powershell Compress-Archive -Path deploy_package\* -DestinationPath railway_deploy.zip -Force

echo.
echo 部署包已创建：railway_deploy.zip
echo 你可以在 Railway 控制台直接上传这个 ZIP 文件
echo.

pause