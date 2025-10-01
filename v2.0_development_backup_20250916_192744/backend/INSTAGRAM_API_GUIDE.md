# Instagram Basic Display API 申请指南

## 概述
Instagram Basic Display API允许用户读取自己Instagram账户的基本资料信息、照片和视频。

## 申请步骤

### 1. 创建Facebook开发者账户
1. 访问 [Facebook for Developers](https://developers.facebook.com)
2. 使用Facebook账户登录
3. 完成开发者账户注册

### 2. 创建Facebook应用
1. 点击"我的应用" -> "创建应用"
2. 选择应用类型："消费者" 或 "商务"
3. 填写应用信息：
   - **应用显示名称**：您的应用名称
   - **应用联系邮箱**：有效的邮箱地址
   - **应用用途**：描述应用用途

### 3. 添加Instagram Basic Display产品
1. 在应用仪表板中，点击"添加产品"
2. 找到"Instagram Basic Display"，点击"设置"
3. 配置OAuth重定向URI：
   ```
   https://yourdomain.com/auth/instagram/callback
   ```
   (测试期间可以使用 `http://localhost:3000/callback`)

### 4. 创建Instagram测试用户
1. 在"Instagram Basic Display" -> "基本显示"页面
2. 点击"创建新应用"
3. 在"Instagram测试用户"部分添加测试用户
4. 邀请Instagram账户成为测试用户

### 5. 获取访问令牌
1. 使用以下URL获取授权码：
```
https://api.instagram.com/oauth/authorize
  ?client_id={app-id}
  &redirect_uri={redirect-uri}
  &scope=user_profile,user_media
  &response_type=code
```

2. 交换访问令牌：
```bash
curl -X POST \
  https://api.instagram.com/oauth/access_token \
  -F client_id={app-id} \
  -F client_secret={app-secret} \
  -F grant_type=authorization_code \
  -F redirect_uri={redirect-uri} \
  -F code={code}
```

## 使用示例

### Python代码示例
```python
import requests

# 基本配置
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
access_token = "YOUR_ACCESS_TOKEN"

# 获取用户信息
def get_user_profile():
    url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
    response = requests.get(url)
    return response.json()

# 获取用户媒体
def get_user_media():
    url = f"https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp&access_token={access_token}"
    response = requests.get(url)
    return response.json()

# 使用示例
profile = get_user_profile()
media = get_user_media()
```

## 限制和注意事项

### 功能限制
- 只能访问应用用户自己的数据
- 不能搜索其他用户或hashtag
- 不能发布内容
- 有API调用频率限制

### 数据范围
可访问的数据字段：
- 用户资料：id, username
- 媒体：id, caption, media_type, media_url, permalink, thumbnail_url, timestamp

### 申请要求
- 需要有效的Facebook/Instagram账户
- 应用必须有明确的用途说明
- 需要遵守Instagram的使用条款

## 替代方案

### 1. Instagram Graph API (商业账户)
- 功能更强大
- 支持商业账户分析
- 需要Facebook页面和Instagram商业账户

### 2. 第三方服务
- Hootsuite API
- Sprout Social API
- Buffer API

### 3. 网页抓取方案
- 使用Selenium自动化
- 注意反爬虫限制
- 可能违反服务条款

## 费用
Instagram Basic Display API本身免费，但有以下限制：
- 每小时200次API调用
- 需要定期刷新访问令牌

## 开发建议
1. **测试环境**：先在测试环境中完成集成
2. **错误处理**：实现完善的错误处理机制
3. **令牌管理**：自动化访问令牌刷新
4. **数据缓存**：减少API调用次数