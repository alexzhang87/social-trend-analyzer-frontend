# Node.js 便携版安装脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Node.js 便携版安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 设置下载路径
$nodeVersion = "v20.18.0"  # LTS版本
$downloadUrl = "https://nodejs.org/dist/$nodeVersion/node-$nodeVersion-win-x64.zip"
$installPath = "C:\nodejs-portable"
$zipFile = "$env:TEMP\nodejs.zip"

Write-Host "`n正在下载Node.js便携版..." -ForegroundColor Yellow
Write-Host "版本: $nodeVersion" -ForegroundColor Gray
Write-Host "下载地址: $downloadUrl" -ForegroundColor Gray

try {
    # 下载Node.js
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "下载完成!" -ForegroundColor Green
    
    # 创建安装目录
    if (Test-Path $installPath) {
        Remove-Item -Recurse -Force $installPath
    }
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    
    # 解压文件
    Write-Host "`n正在解压文件..." -ForegroundColor Yellow
    Expand-Archive -Path $zipFile -DestinationPath $installPath -Force
    
    # 移动文件到正确位置
    $extractedFolder = Get-ChildItem -Path $installPath -Directory | Select-Object -First 1
    $extractedPath = $extractedFolder.FullName
    
    # 将内容移动到根目录
    Get-ChildItem -Path $extractedPath | Move-Item -Destination $installPath
    Remove-Item -Path $extractedPath -Force
    
    Write-Host "解压完成!" -ForegroundColor Green
    
    # 添加到PATH环境变量
    Write-Host "`n正在配置环境变量..." -ForegroundColor Yellow
    
    # 获取当前用户的PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # 检查是否已经在PATH中
    if ($currentPath -notlike "*$installPath*") {
        $newPath = "$installPath;$currentPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "已添加到用户PATH环境变量" -ForegroundColor Green
    } else {
        Write-Host "已存在于PATH环境变量中" -ForegroundColor Yellow
    }
    
    # 更新当前会话的PATH
    $env:PATH = "$installPath;$env:PATH"
    
    # 清理下载文件
    Remove-Item -Path $zipFile -Force
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Node.js 便携版安装完成!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    Write-Host "`n安装路径: $installPath" -ForegroundColor Cyan
    Write-Host "Node.js版本: " -NoNewline -ForegroundColor Cyan
    & "$installPath\node.exe" --version
    Write-Host "npm版本: " -NoNewline -ForegroundColor Cyan
    & "$installPath\npm.cmd" --version
    
    Write-Host "`n注意事项:" -ForegroundColor Yellow
    Write-Host "1. 请重新打开命令行窗口以使PATH生效" -ForegroundColor Gray
    Write-Host "2. 或者重启IDE以使环境变量生效" -ForegroundColor Gray
    Write-Host "3. 如果仍有问题，请手动将 $installPath 添加到系统PATH" -ForegroundColor Gray
    
} catch {
    Write-Host "`n安装失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查网络连接或手动下载安装" -ForegroundColor Yellow
}

Write-Host "`n按任意键继续..." -ForegroundColor Gray
Read-Host