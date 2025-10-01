# Railway 自动化部署脚本 (PowerShell版本)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Railway 自动化部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查Node.js
Write-Host "`n检查Node.js是否已安装..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    Write-Host "Node.js 已安装: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js 未安装，请先安装Node.js" -ForegroundColor Red
    Write-Host "请访问 https://nodejs.org/ 下载并安装Node.js" -ForegroundColor Yellow
    Write-Host "或者使用winget安装: winget install OpenJS.NodeJS" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Railway CLI
Write-Host "`n检查Railway CLI是否已安装..." -ForegroundColor Yellow
try {
    $railwayVersion = railway --version 2>$null
    Write-Host "Railway CLI 已安装: $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "Railway CLI 未安装，正在安装..." -ForegroundColor Yellow
    npm install -g @railway/cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装Railway CLI失败，请检查网络连接" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "Railway CLI 安装成功" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "开始Railway部署流程" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 登录Railway
Write-Host "`n1. 登录Railway..." -ForegroundColor Yellow
Write-Host "这将打开浏览器进行登录" -ForegroundColor Gray
railway login

# 2. 初始化项目
Write-Host "`n2. 初始化Railway项目..." -ForegroundColor Yellow
railway init

# 3. 环境变量设置提示
Write-Host "`n3. 设置环境变量..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "必需的环境变量:" -ForegroundColor White
Write-Host "- ZHIPU_API_KEY: 您的智谱AI API密钥" -ForegroundColor Gray
Write-Host "- SECRET_KEY: JWT密钥（建议使用强随机字符串）" -ForegroundColor Gray
Write-Host "`n可选的环境变量:" -ForegroundColor White
Write-Host "- TWITTERAPI_IO_KEY: 您的Twitter API密钥" -ForegroundColor Gray
Write-Host "- OPENAI_API_KEY: 您的OpenAI API密钥" -ForegroundColor Gray
Write-Host "- DATABASE_URL: 数据库连接URL（Railway可自动提供）" -ForegroundColor Gray
Write-Host "- REDIS_URL: Redis连接URL（Railway可自动提供）" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "`n您可以通过以下命令设置环境变量:" -ForegroundColor Yellow
Write-Host "railway variables set ZHIPU_API_KEY=your_api_key" -ForegroundColor Cyan
Write-Host "railway variables set SECRET_KEY=your_secret_key" -ForegroundColor Cyan
Write-Host "或者在Railway控制台网页中设置" -ForegroundColor Gray

# 询问是否添加数据库服务
$addDb = Read-Host "`n是否要添加PostgreSQL数据库服务? (y/n)"
if ($addDb -eq "y" -or $addDb -eq "Y") {
    Write-Host "添加PostgreSQL服务..." -ForegroundColor Yellow
    railway add postgresql
}

# 询问是否添加Redis服务
$addRedis = Read-Host "`n是否要添加Redis缓存服务? (y/n)"
if ($addRedis -eq "y" -or $addRedis -eq "Y") {
    Write-Host "添加Redis服务..." -ForegroundColor Yellow
    railway add redis
}

Read-Host "`n按Enter键继续部署..."

# 4. 部署
Write-Host "`n4. 开始部署到Railway..." -ForegroundColor Yellow
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "部署成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    Write-Host "`n有用的命令:" -ForegroundColor Yellow
    Write-Host "- 查看部署状态: railway status" -ForegroundColor Cyan
    Write-Host "- 查看日志: railway logs" -ForegroundColor Cyan
    Write-Host "- 实时查看日志: railway logs --follow" -ForegroundColor Cyan
    Write-Host "- 打开Railway控制台: railway open" -ForegroundColor Cyan
    Write-Host "- 查看应用URL: railway domain" -ForegroundColor Cyan
    
    Write-Host "`n获取应用URL..." -ForegroundColor Yellow
    railway domain
    
    Write-Host "`n如果需要初始化数据库，请运行:" -ForegroundColor Yellow
    Write-Host "railway run python railway_init.py" -ForegroundColor Cyan
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "部署失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    
    Write-Host "`n请检查:" -ForegroundColor Yellow
    Write-Host "1. 环境变量是否正确设置" -ForegroundColor Gray
    Write-Host "2. railway.toml配置是否正确" -ForegroundColor Gray
    Write-Host "3. Dockerfile是否有语法错误" -ForegroundColor Gray
    
    Write-Host "`n查看详细错误信息:" -ForegroundColor Yellow
    Write-Host "railway logs" -ForegroundColor Cyan
}

Read-Host "`n按Enter键退出"