# 🔒 Ngrok HTTPS隧道设置指南

## 🎯 **为什么需要Ngrok？**

Product Hunt API要求重定向URI必须使用HTTPS协议，而本地开发通常使用HTTP。Ngrok可以为本地服务创建HTTPS隧道。

## 📥 **安装Ngrok**

### Windows用户
1. **下载**: 访问 https://ngrok.com/download 下载Windows版本
2. **解压**: 将下载的zip文件解压到任意目录
3. **添加到PATH** (可选): 将ngrok.exe添加到系统PATH环境变量

### 或者使用Chocolatey
```bash
choco install ngrok
```

### 或者使用Scoop
```bash
scoop install ngrok
```

## 🚀 **使用步骤**

### 步骤1: 注册Ngrok账号
1. 访问 https://ngrok.com/ 注册免费账号
2. 登录后获取您的认证令牌
3. 在终端中运行认证命令：
```bash
ngrok authtoken YOUR_AUTH_TOKEN_HERE
```

### 步骤2: 启动本地服务器
确保您的后端服务在8000端口运行：
```bash
cd backend
python main.py
# 或者运行批处理文件
start_backend_simple.bat
```

### 步骤3: 创建HTTPS隧道
在新的终端窗口中运行：
```bash
ngrok http 8000
```

### 步骤4: 获取HTTPS URL
Ngrok会显示类似以下输出：
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000
Forwarding                    http://abc123def456.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**复制HTTPS URL**: `https://abc123def456.ngrok.io`

## 🔧 **配置Product Hunt API**

使用获得的HTTPS URL配置Product Hunt应用：

```
应用名称: Social Trend Analyzer
应用描述: AI-powered social media trend analysis platform for entrepreneurs and startups
应用网站: https://abc123def456.ngrok.io
回调URL: https://abc123def456.ngrok.io/auth/callback
```

## 📝 **更新环境变量**

在您的`.env`文件中更新：
```bash
PRODUCT_HUNT_REDIRECT_URI=https://abc123def456.ngrok.io/auth/callback
```

## 🎯 **测试配置**

运行Product Hunt API测试：
```bash
cd backend
python test_product_hunt_api.py
```

## ⚠️ **重要注意事项**

### 免费账号限制
- **隧道数量**: 1个并发隧道
- **连接数**: 40个连接/分钟
- **URL变化**: 每次重启ngrok都会生成新的URL

### URL变化处理
每次重启ngrok时：
1. 复制新的HTTPS URL
2. 更新Product Hunt应用的回调URL
3. 更新`.env`文件中的`PRODUCT_HUNT_REDIRECT_URI`

### 生产环境
在生产环境中，使用您的真实域名：
```
回调URL: https://yourdomain.com/auth/callback
```

## 🚀 **快速启动脚本**

创建一个批处理文件 `start_with_ngrok.bat`：
```batch
@echo off
echo 启动后端服务...
start "Backend" cmd /c "cd backend && python main.py"

echo 等待服务启动...
timeout /t 5 /nobreak >nul

echo 启动ngrok隧道...
start "Ngrok" cmd /c "ngrok http 8000"

echo 服务已启动！
echo 1. 复制ngrok显示的HTTPS URL
echo 2. 更新Product Hunt应用的回调URL  
echo 3. 更新.env文件中的PRODUCT_HUNT_REDIRECT_URI
pause
```

## 🔍 **故障排除**

### 问题1: Ngrok命令未找到
**解决**: 确保ngrok.exe在PATH中或使用完整路径

### 问题2: 认证令牌错误
**解决**: 重新运行 `ngrok authtoken YOUR_TOKEN`

### 问题3: 隧道连接失败
**解决**: 检查防火墙设置，确保8000端口可访问

### 问题4: Product Hunt回调失败
**解决**: 确保回调URL与ngrok URL完全匹配

---

**下一步**: 设置好ngrok后，使用生成的HTTPS URL在Product Hunt创建应用！