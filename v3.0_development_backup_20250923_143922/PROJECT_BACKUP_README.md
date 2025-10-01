# 项目备份说明 - V2.0 完整版本

## 备份时间
- 备份日期: 2025年9月23日
- 备份时间: 14:39:22
- 备份版本: V2.0 稳定版

## 项目概述
**IdeaEden - 社交媒体趋势分析与创业想法验证平台**

这是一个基于AI的创业想法验证和市场分析平台，帮助创业者通过数据驱动的方式验证商业想法。

## 当前功能模块

### 1. 核心分析功能
- **Keyword Analysis**: 关键词趋势分析和市场洞察
- **Professional Analysis**: 深度市场分析和商业可行性评估
- **AI Insights**: 实时智能洞察和预警系统
- **PMF Scorecard**: 产品市场匹配度评估工具

### 2. 用户管理系统
- 用户注册/登录
- 订阅层级管理 (Free/Starter/Pro)
- 积分系统和使用限制
- 用户数据管理

### 3. 数据源集成
- Google Trends API
- Reddit API
- 社交媒体数据抓取
- 搜索量和竞争度分析

## 技术架构

### 后端 (Python/FastAPI)
```
backend/
├── app/
│   ├── api/          # API路由
│   │   ├── trends.py # 趋势分析API
│   │   ├── ai_insights.py # AI洞察API
│   │   └── auth.py   # 认证API
│   ├── services/     # 业务逻辑层
│   │   ├── analysis_service.py
│   │   ├── ai_insights_service.py
│   │   └── cache_service.py
│   ├── data/         # 数据层
│   │   ├── models/   # 数据模型
│   │   └── database/ # 数据库配置
│   └── core/         # 核心功能
│       ├── auth.py   # 认证逻辑
│       └── config.py # 配置管理
```

### 前端 (React/TypeScript/Vite)
```
frontend/
├── src/
│   ├── components/   # UI组件
│   │   ├── unified-workspace.tsx # 统一工作台
│   │   ├── pmf-scorecard.tsx     # PMF评估
│   │   └── automated-pmf-evaluation.tsx
│   ├── services/     # API服务
│   │   ├── aiInsightsApi.ts
│   │   └── api.ts
│   ├── hooks/        # React Hooks
│   └── lib/          # 工具库
```

## 数据库结构
- **Users**: 用户信息和认证
- **Subscriptions**: 订阅管理
- **CreditTransactions**: 积分交易记录
- **AnalysisResults**: 分析结果缓存

## 当前已知问题
1. **功能重叠**: Professional Analysis、AI Insights、PMF Scorecard存在约70%功能重叠
2. **用户体验**: 多个入口导致用户选择困难
3. **数据孤岛**: 各功能模块数据不互通
4. **维护成本**: 重复代码增加维护难度

## 性能指标
- **响应时间**: 平均2-5秒
- **并发支持**: 最大50用户同时在线
- **缓存命中率**: 约85%
- **API成功率**: 95%+

## 部署配置
- **开发环境**: localhost:5173 (前端) + localhost:8000 (后端)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **缓存**: Redis
- **容器化**: Docker + Docker Compose

## 依赖版本
### 后端主要依赖
- FastAPI: 0.104.1
- SQLAlchemy: 2.0.23
- Pydantic: 2.5.0
- Redis: 5.0.1

### 前端主要依赖
- React: 18.2.0
- TypeScript: 5.2.2
- Vite: 5.0.8
- Tailwind CSS: 3.3.6

## 备份内容清单
- ✅ 完整源代码 (frontend + backend)
- ✅ 配置文件 (.env, docker-compose.yml)
- ✅ 文档资料 (docs/ + *.md)
- ✅ 数据库模式和种子数据
- ✅ 部署脚本和工具

## 恢复说明
1. 复制备份文件到新目录
2. 安装依赖: `npm install` (前端) + `pip install -r requirements.txt` (后端)
3. 配置环境变量
4. 初始化数据库: `python init_db.py`
5. 启动服务: `start_system.bat`

## 下一步计划
基于此备份，将开发V3.0版本 - "智能创业助手"，采用对话式界面整合所有分析功能。

---
**备份创建者**: AI Assistant
**备份目的**: 为V3.0版本开发做准备
**重要性**: 高 - 包含完整的可工作版本