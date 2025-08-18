# 后端综合开发规格书 (Backend Development Specification)

**版本:** 1.0
**日期:** 2025-08-15
**作者:** CodeBuddy

## 1. 愿景与目标

本后端旨在为 **Social Trend Analyzer** 前端应用提供强大、稳定且高效的数据支持。其核心目标是：将来自不同社交媒体（当前为 X/Twitter 和 Reddit）的原始、非结构化数据，通过 **RAG (Retrieval-Augmented Generation)** 技术栈和大型语言模型 (LLM)，转化为对用户有价值的、结构化的商业洞察。

## 2. 核心设计原则

- **API优先 (API-First):** 后端接口的设计严格围绕前端组件的需求。API的响应格式将直接映射到前端所需的数据结构，以取代现有的 `mock-data.ts`。
- **异步处理 (Asynchronous by Default):** 数据抓取和LLM分析是耗时操作。所有核心分析任务都必须作为后台异步任务执行，以避免前端请求超时，并提供流畅的用户体验。
- **模块化与可扩展 (Modular & Extensible):** 功能模块（数据抓取、数据处理、API服务）应高度解耦，方便未来新增数据源（如 Instagram, TikTok）或替换分析模型。
- **结果可复现与缓存 (Reproducible & Cacheable):** 对相同关键词的分析请求在一定时间内应能返回缓存结果，以降低成本和提高响应速度。

## 3. 技术栈

- **Web框架:** FastAPI
- **Web服务器:** Uvicorn
- **数据库 ORM:** SQLAlchemy
- **数据库:** SQLite (开发) / PostgreSQL (生产)
- **数据验证:** Pydantic
- **异步任务队列:** FastAPI BackgroundTasks (初期) / Celery (扩展)
- **向量数据库 (RAG):** ChromaDB
- **文本向量化 (RAG):** Sentence-Transformers
- **数据抓取:** Praw (Reddit), Requests/AIOHTTP (for Twitter/X API)
- **LLM 集成:** OpenAI

## 4. 系统架构（概念流程）

这是一个简化的核心分析流程：

1.  **[前端]** -> 用户在UI输入关键词，点击“分析”。
2.  **[API]** -> `POST /api/v1/analyze` 接收请求，验证输入，创建一个分析任务，并立即返回一个 `job_id`。
3.  **[后台任务]** -> 分析任务被触发：
    a. **数据抓取 (Collectors):** 并行从 X 和 Reddit 抓取相关帖子/评论。
    b. **数据处理 (Processors):** 清洗文本，使用 `sentence-transformers` 将文本向量化，存入 `ChromaDB`。
    c. **聚类与检索 (Clustering & Retrieval):** 对向量进行聚类，识别出不同的主题（即“趋势”）。
    d. **洞察生成 (Generation):** 对每个主题，调用 OpenAI LLM，使用专用 Prompt 生成：
        - 趋势标题和摘要
        - 痛点 (Pain Points)
        - 机会 (Opportunities)
        - MVP 建议 (MVP Plan)
        - 情感分析 (Emotion Analysis)
    e. **结果存储:** 将所有生成的洞察和原始数据关联，存入主数据库。
4.  **[前端]** -> 使用 `job_id` 轮询 `GET /api/v1/analysis/status/{job_id}`。
5.  **[API]** -> 状态接口返回 `PENDING`, `PROCESSING`, `SUCCESS`, 或 `FAILED`。成功后，返回最终结果的 `analysis_id`。
6.  **[前端]** -> 使用 `analysis_id` 请求 `GET /api/v1/analysis/{analysis_id}` 获取完整数据并渲染UI。

## 5. API 端点设计 (V1)

### `POST /api/v1/analyze`
- **功能:** 启动一个新的趋势分析任务。
- **请求体:**
  ```json
  {
    "keyword": "AI Agent",
    "platforms": ["twitter", "reddit"],
    "options": {
      "force_refresh": false 
    }
  }
  ```
- **成功响应 (202):**
  ```json
  {
    "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
  ```

### `GET /api/v1/analysis/status/{job_id}`
- **功能:** 查询分析任务的状态。
- **成功响应 (200):**
  ```json
  {
    "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "status": "SUCCESS", // PENDING, PROCESSING, SUCCESS, FAILED
    "analysis_id": "xyz-789" // 仅在 SUCCESS 时提供
  }
  ```

### `GET /api/v1/analysis/{analysis_id}`
- **功能:** 获取完整的分析结果，数据结构直接匹配前端组件需求。
- **成功响应 (200):**
  ```json
  {
    "id": "xyz-789",
    "keyword": "AI Agent",
    "createdAt": "2025-08-15T16:00:00Z",
    "overview": {
      "totalMentions": 1205,
      "socialReach": 2500000,
      "engagement": 15000,
      "sentiment": { "positive": 65, "neutral": 20, "negative": 15 }
    },
    "wordCloud": [
      { "text": "Devin", "value": 98 },
      { "text": "AutoGen", "value": 75 },
      { "text": "workflow", "value": 60 }
    ],
    "trends": [
      {
        "id": "trend-001",
        "title": "自主AI代理正在重塑软件开发工作流",
        "summary": "开发者正在热烈讨论像Devin这样的AI代理如何自动化编码、测试和部署任务，这可能导致生产力的大幅提升。",
        "hot_score": 95,
        "category": "技术变革",
        "insights": {
          "pain_points": "...",
          "opportunities": "...",
          "mvp_plan": "..."
        },
        "emotion_analysis": { "joy": 50, "sadness": 5, "anger": 3, "sarcasm": 10, "neutral": 32 },
        "top_mentions": [
          {
            "id": "mention-t-001",
            "platform": "twitter",
            "author": "@dev_guru",
            "avatar": "...",
            "text": "Just tried an AI agent to build a full-stack app. It's not perfect, but it finished 80% of the boilerplate. The future is here.",
            "likes": 1200,
            "comments": 250,
            "sentiment": "Positive"
          }
        ]
      }
    ]
  }
  ```

## 6. 数据库模型 (核心表)

- **`AnalysisJob`**: 存储分析任务的状态。
  - `id`, `job_id`, `keyword`, `status`, `analysis_id`, `created_at`
- **`AnalysisResult`**: 存储完整的分析报告JSON。
  - `id`, `keyword`, `result_json`, `created_at`
- **`Trend`**: 存储每个趋势的详细信息。
- **`Mention`**: 存储原始抓取的数据。
- **`AuditLog`**: 记录对LLM的调用、成本和Token使用情况。

## 7. 开发里程碑

### 阶段一: 核心框架与同步MVP (目标：替换前端Mock数据)
1.  **[完成]** 搭建FastAPI项目，配置环境。
2.  **[进行中]** 实现上述数据库模型 (SQLAlchemy)。
3.  **[待办]** 实现 `POST /api/v1/analyze` 和 `GET /api/v1/analysis/{analysis_id}`。
4.  **[待办]** **暂时采用同步方式** 实现核心分析流程，用于快速验证端到端逻辑。
5.  **[待办]** 对接OpenAI API，实现基于固定Prompt的洞察生成。
6.  **目标:** 前端可以调用真实API，尽管响应会比较慢。

### 阶段二: 异步化与性能优化
1.  **[待办]** 将核心分析流程迁移到 `BackgroundTasks`。
2.  **[待办]** 实现 `GET /api/v1/analysis/status/{job_id}` 状态轮询接口。
3.  **[待办]** 实现结果缓存机制（例如，基于关键词和时间的Redis缓存）。

### 阶段三: 生产化与运营
1.  **[待办]** 实现 `AuditLog`，自动记录LLM调用。
2.  **[待办]** 完善错误处理和日志记录 (集成Sentry)。
3.  **[待办]** 编写 `Dockerfile` 和 `docker-compose.yml`，为部署做准备。

### 阶段四: 管理与扩展
1.  **[待办]** 开发一个简单的管理后台（如FastAPI-Admin），用于查看审计日志和手动触发分析。
2.  **[待办]** 抽象数据抓取器接口，为未来添加新平台做准备。