@echo off
echo 正在准备 GitHub 部署...

REM 检查是否已初始化 git
if not exist .git (
    echo 初始化 Git 仓库...
    git init
    git branch -M main
)

REM 添加 .gitignore 以排除大文件
echo 更新 .gitignore...
echo node_modules/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo collected_data/ >> .gitignore
echo model_outputs/ >> .gitignore
echo *.json >> .gitignore
echo *.csv >> .gitignore
echo *.pth >> .gitignore
echo logs/ >> .gitignore
echo uploads/ >> .gitignore

echo 添加文件到 Git...
git add .
git commit -m "Railway deployment ready"

echo.
echo 请按以下步骤完成 GitHub 部署：
echo 1. 在 GitHub 创建新仓库（不要初始化 README）
echo 2. 复制仓库 URL
echo 3. 运行：git remote add origin [你的仓库URL]
echo 4. 运行：git push -u origin main
echo 5. 在 Railway 控制台选择 "Deploy from GitHub repo"
echo 6. 选择你的仓库并完成部署

pause