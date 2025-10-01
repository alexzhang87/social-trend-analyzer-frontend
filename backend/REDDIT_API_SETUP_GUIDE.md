# Reddit 官方API注册与配置指南

## 🎯 **注册步骤**

### 第一步：访问Reddit应用管理页面
```
https://www.reddit.com/prefs/apps
```

### 第二步：创建应用
1. 点击页面底部的 **"Create App"** 或 **"Create Another App"** 按钮
2. 填写应用信息：

```
应用名称: Social Trend Analyzer
应用类型: ⚫ script (选择这个选项，适合服务端应用)
描述: AI-powered social media trend analysis platform for entrepreneurs
关于URL: http://localhost:8000 (开发期间可以用localhost)
重定向URI: http://localhost:8000/auth/callback
```

### 第三步：获取API凭证
创建成功后，您会看到：

```
应用名称: Social Trend Analyzer
├── client_id: (14个字符的字符串，显示在应用名称正下方)
└── secret: (27个字符的字符串，点击应用查看详情获得)
```

## 🔧 **配置环境变量**

在您的 `.env` 文件中添加以下配置：

```bash
# Reddit 官方API配置
REDDIT_CLIENT_ID=your_14_character_client_id_here
REDDIT_CLIENT_SECRET=your_27_character_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### ⚠️ **Google账户登录用户特别说明**

如果您使用Google账户注册Reddit，需要完成以下步骤：

#### 步骤1: 查找Reddit用户名
1. 登录Reddit网站
2. 点击右上角头像，查看用户名（格式如：u/your_username）
3. 用户名就是去掉 "u/" 的部分

#### 步骤2: 设置Reddit密码
1. 访问：https://www.reddit.com/settings/privacy
2. 找到 "Account Security" 部分
3. 点击 "Set Password" 设置新密码
4. **重要**：这个密码专门用于API访问，建议设置强密码

#### 步骤3: 更新环境变量
```bash
# 示例配置
REDDIT_CLIENT_ID=hH0BEEYddOeBpKMO-2GH_A
REDDIT_CLIENT_SECRET=2l2t5XyqAxIGSJMLLGAGjlct1DBmmA
REDDIT_USERNAME=your_actual_reddit_username  # 不是邮箱地址
REDDIT_PASSWORD=your_newly_set_password       # 刚设置的密码
```

## ✅ **验证配置**

### 方法1: 使用测试脚本
运行以下命令验证API连接：

```bash
cd backend
python test_reddit_api.py
```

### 方法2: 手动验证
访问以下URL确认应用创建成功：
```
https://www.reddit.com/prefs/apps
```

## 📊 **API限制与最佳实践**

### 速率限制
- **60次请求/分钟** (每秒1次)
- **600次请求/10分钟**
- 超过限制会收到429错误

### 最佳实践
1. **请求间隔**: 每次请求间隔至少1秒
2. **User-Agent**: 使用唯一的User-Agent标识
3. **错误处理**: 正确处理429和503错误
4. **缓存**: 缓存API响应减少重复请求

## 🚨 **常见问题排查**

### 问题1: 认证失败 (401错误)
**原因**: client_id或client_secret错误
**解决**: 重新检查`.env`文件中的凭证

### 问题2: 速率限制 (429错误)  
**原因**: 请求过于频繁
**解决**: 增加请求间隔时间

### 问题3: 无法获取token
**原因**: 用户名或密码错误
**解决**: 确认Reddit账号凭证正确

## 📋 **后续集成步骤**

1. ✅ 注册API账号 (当前任务)
2. 🔄 测试API连接
3. 🔄 集成到分析服务
4. 🔄 添加错误处理和重试机制
5. 🔄 性能优化和缓存

## 💡 **提示**

- Reddit API完全免费，无需信用卡
- 创建应用后立即可用，无需审核
- 建议创建专门的Reddit账号用于API访问
- 保存好client_id和secret，这些信息很重要

---

**下一步**: 完成注册后，请运行测试脚本验证集成是否成功！