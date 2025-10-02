@echo off
echo Railway 部署验证脚本
echo.

set /p DOMAIN="请输入你的 Railway 域名（不含 https://）: "

echo.
echo 正在验证部署...

echo.
echo 1. 检查根路径...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://%DOMAIN%/' -UseBasicParsing; Write-Host '✅ 根路径正常 - 状态码:' $response.StatusCode } catch { Write-Host '❌ 根路径失败:' $_.Exception.Message }"

echo.
echo 2. 检查健康检查端点...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://%DOMAIN%/api/v1/health/' -UseBasicParsing; Write-Host '✅ 健康检查正常 - 状态码:' $response.StatusCode } catch { Write-Host '❌ 健康检查失败:' $_.Exception.Message }"

echo.
echo 3. 检查 API 文档...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://%DOMAIN%/docs' -UseBasicParsing; Write-Host '✅ API 文档正常 - 状态码:' $response.StatusCode } catch { Write-Host '❌ API 文档失败:' $_.Exception.Message }"

echo.
echo 验证完成！
echo 如果所有检查都显示 ✅，说明部署成功
echo 如果有 ❌，请检查 Railway 控制台的运行日志

pause