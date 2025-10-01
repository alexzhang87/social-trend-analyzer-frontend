# Ngrok 自动下载和安装脚本
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Ngrok 自动下载和安装" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host

# 设置下载目录
$ngrokDir = "C:\ngrok"
$ngrokExe = "$ngrokDir\ngrok.exe"

# 创建目录
if (!(Test-Path $ngrokDir)) {
    Write-Host "📁 创建ngrok目录: $ngrokDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ngrokDir -Force | Out-Null
}

# 检查是否已存在
if (Test-Path $ngrokExe) {
    Write-Host "✅ Ngrok已存在，跳过下载" -ForegroundColor Green
    & $ngrokExe version
} else {
    Write-Host "📥 下载Ngrok..." -ForegroundColor Yellow
    
    # Ngrok下载URL
    $downloadUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    $zipFile = "$ngrokDir\ngrok.zip"
    
    try {
        # 下载文件
        Write-Host "正在从 $downloadUrl 下载..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
        
        # 解压文件
        Write-Host "📦 解压文件..." -ForegroundColor Yellow
        Expand-Archive -Path $zipFile -DestinationPath $ngrokDir -Force
        
        # 删除zip文件
        Remove-Item $zipFile -Force
        
        Write-Host "✅ Ngrok下载完成!" -ForegroundColor Green
        
        # 验证安装
        if (Test-Path $ngrokExe) {
            & $ngrokExe version
        }
        
    } catch {
        Write-Host "❌ 下载失败: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "请手动下载: https://ngrok.com/download" -ForegroundColor Yellow
        exit 1
    }
}

# 添加到PATH环境变量
Write-Host "🔧 配置环境变量..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$ngrokDir*") {
    $newPath = "$currentPath;$ngrokDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✅ 已添加到PATH环境变量" -ForegroundColor Green
    Write-Host "⚠️  请重启PowerShell窗口以使PATH生效" -ForegroundColor Yellow
} else {
    Write-Host "✅ PATH环境变量已配置" -ForegroundColor Green
}

Write-Host
Write-Host "🎉 Ngrok安装完成!" -ForegroundColor Green
Write-Host
Write-Host "📋 下一步操作:" -ForegroundColor Cyan
Write-Host "1. 重启PowerShell窗口" -ForegroundColor White
Write-Host "2. 运行: ngrok version (验证安装)" -ForegroundColor White
Write-Host "3. 访问 https://ngrok.com/signup 注册账号" -ForegroundColor White
Write-Host "4. 获取authtoken并运行: ngrok authtoken YOUR_TOKEN" -ForegroundColor White
Write-Host "5. 运行: ngrok http 8000 (创建隧道)" -ForegroundColor White
Write-Host

# 提供快捷方式
Write-Host "💡 或者运行以下命令直接打开ngrok目录:" -ForegroundColor Yellow
Write-Host "explorer $ngrokDir" -ForegroundColor Cyan