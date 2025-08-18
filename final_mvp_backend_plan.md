# 终极后端开发方案 (MVP) - 融合版

**版本:** 2.0 (融合版)
**日期:** 2025-08-15
**目标:** 结合所有方案优点，制定一份单人开发者在AI辅助下，能以最低成本和最快速度完成的、可直接支撑现有前端的后端MVP开发计划。

---

## 1. 核心设计哲学 (Guiding Philosophy)

- **种子优先，快速验证 (Seed-First, Validate Fast):** MVP阶段，我们不应被实时数据抓取的复杂性拖慢。首要任务是建立一个能处理**静态种子数据**的核心分析流程，快速打通前后端，替换掉模拟数据。这是通往可用产品的最短路径。
- **AI工具驱动 (AI-Tool Driven):** 整个开发过程将高度依赖AI编程助手 (如Cursor, Copilot)。所有方案设计都将为此优化，提供清晰、可复制的指令。
- **成本效益最大化 (Maximum Cost-Effectiveness):** 严格选用免费或按需付费的低成本服务，确保MVP阶段的月度成本控制在最低水平。
- **异步为王 (Asynchronous by Default):** 即使初期是同步实现，整体架构设计必须面向异步，为未来的性能扩展预留空间。

---

## 2. 技术栈 (The Best-of-Breed Stack)

| 类别 | 技术选型 | 理由 |
| :--- | :--- | :--- |
| **语言/框架** | Python 3.10+ / FastAPI | 一致推荐，轻量、高效、自带文档。 |
| **数据库** | SQLite | MVP阶段的唯一选择，零配置，文件即数据库。 |
| **LLM模型** | OpenAI GPT-4o-mini | 优异的成本效益，强大的JSON输出能力。 |
| **文本向量化** | `sentence-transformers` | 本地运行，免费且效果出色，是实现RAG的核心。 |
| **向量数据库** | ChromaDB | 本地运行，轻量级，与FastAPI集成简单。 |
| **数据抓取** | `aiohttp` + `praw` | 异步抓取，性能更佳，代码参考Claude方案。 |
| **任务队列** | FastAPI `BackgroundTasks` | 内置功能，足以满足MVP的异步需求，无需引入Celery等重型框架。 |
| **部署** | Docker / Render | Docker保证环境一致性，Render提供简单的一键部署免费套餐。 |

---

## 3. MVP实施路径 (The "Seed-First" Roadmap)

这是整个MVP开发的核心策略，分为两个紧密衔接的阶段。

### **阶段一：种子数据与同步核心 (7天内完成)**

**目标：用真实API彻底取代前端的 `mock-data.ts`。**

1.  **搭建FastAPI基础项目:**
    *   创建项目结构，安装 `requirements.txt`。
    *   实现一个健康的 `/api/health` 端点。

2.  **实现 `/api/seed` 端点:**
    *   **关键任务:** 创建一个API，允许通过上传CSV或JSON文件，将预先收集好的社交媒体帖子数据（包含平台、作者、内容、链接、点赞数等）批量导入到SQLite的 `raw_posts` 表中。
    *   **价值:** 这让我们能立即用高质量的、贴近真实场景的数据进行开发和测试，而无需等待实时抓取功能的完成。

3.  **构建同步分析流程:**
    *   创建一个 `AnalysisService`，当被调用时，它会**同步地**执行以下操作：
        a.  **向量化 (Embed):** 从 `raw_posts` 表中读取帖子，使用 `sentence-transformers` 将文本内容转换为向量，存入ChromaDB。
        b.  **聚类 (Cluster):** 对向量进行聚类（如KMeans），识别出不同的主题。每个主题成为一个“趋势 (Trend)”。
        c.  **生成洞察 (Generate):** 对每个聚类出的趋势，调用 **GPT-4o-mini**，使用**分步Prompt**（见下文）生成标题、摘要、痛点、机会、情感分析等。
        d.  **结果入库:** 将完整的分析结果存入SQLite的 `analysis_results` 表。

4.  **实现 `/api/analysis/{analysis_id}` 端点:**
    *   该接口直接从 `analysis_results` 表中读取已完成的分析结果，并以完全匹配前端组件需求的JSON格式返回。

**阶段一验收标准：** 前端可以调用一个（虽然可能很慢的）真实API，并成功渲染出与mock数据一致的、由LLM真实生成的分析报告。

### **阶段二：异步处理与实时抓取 (阶段一成功后进行)**

**目标：提升用户体验，并接入实时数据源。**

1.  **改造为异步流程:**
    *   将 `AnalysisService` 的核心逻辑移入一个由 `BackgroundTasks` 触发的函数中。
    *   修改 `/api/analyze` 接口，使其不再等待分析完成，而是立即返回一个 `job_id`。
    *   实现 `/api/analysis/status/{job_id}` 接口，供前端轮询任务状态 (`PENDING`, `SUCCESS`, `FAILED`)。

2.  **实现实时数据抓取器:**
    *   参考 **Claude方案** 中提供的代码，实现 `TwitterCollector` 和 `RedditCollector`。
    *   在 `AnalysisService` 的后台任务中，第一步就是调用这些抓取器来获取实时数据，然后再进行后续的分析流程。

---

## 4. LLM Prompt策略 (Modular Prompting)

为了提高LLM输出的稳定性和准确性，我们不使用单一的巨大Prompt，而是将任务分解为一系列小而精的调用，这借鉴了Claude方案的思路：

1.  **提取趋势标题/摘要:** 输入一个聚类的帖子样本，要求LLM总结出趋势标题和摘要。
2.  **提取痛点:** 输入趋势样本，要求LLM以结构化JSON格式返回3个核心痛点（包含描述、意图、严重性）。
3.  **生成机会:** 将上一步生成的痛点作为输入，要求LLM生成对应的3个商业机会（包含描述、影响、实施难度）。
4.  **生成MVP计划:** 将最优的机会作为输入，要求LLM生成一个为期7天的MVP计划。
5.  **情感分析:** 输入趋势样本，要求LLM返回情感分布的百分比（Joy, Sadness, Anger等）。

---

## 5. AI辅助开发指令 (Prompts for Your AI Assistant)

您可以直接将以下指令复制给您的AI编程助手，以生成阶段一的核心代码。

**指令一：项目初始化与Seed API**
```
Generate a Python FastAPI project using Docker.
1. Create a main.py for the FastAPI app.
2. Use SQLAlchemy to define a `raw_posts` table in a SQLite database (fields: id, platform, author, text, url, likes, created_at).
3. Implement a `/api/seed` endpoint that accepts a JSON array of posts and saves them to the `raw_posts` table.
4. Include a `requirements.txt`, a `Dockerfile`, and a `docker-compose.yml` to run the app.
5. Provide instructions on how to run it locally and test the `/api/seed` endpoint with curl.
```

**指令二：核心RAG分析服务**
```
In the existing FastAPI project, add an `AnalysisService`.
1. Add `sentence-transformers` and `chromadb` to requirements.
2. The service should have a method `analyze_synchronously(posts)` that performs the following:
   a. Takes a list of posts.
   b. Uses 'all-MiniLM-L6-v2' to create embeddings for each post's text.
   c. Stores these embeddings in a local ChromaDB collection.
   d. Uses KMeans to cluster the posts into 3 groups based on their embeddings.
   e. For each cluster, prepare a summary of the posts.
3. Create a new endpoint `POST /api/analyze/sync` that fetches all posts from the database, runs this analysis, and returns a simple JSON with the clustered post IDs.
```

---

## 6. 测试与验证 (Validation Plan)

- **第一轮 (本地验证):** 运行 `docker-compose up`，使用curl或脚本调用 `/api/seed` 上传至少50条样本数据。然后调用分析接口，确保能返回不报错的、结构正确的JSON。
- **第二轮 (功能验证):** 仔细检查LLM生成的JSON内容。痛点是否真的来自原文？MVP计划是否合理？这一步需要人工判断，并根据结果微调Prompt。
- **第三轮 (前后端联调):** 前端切换API地址，调用真实后端接口。验证所有UI组件（词云、趋势卡片、详情弹窗）是否都能正确显示数据。

---

## 7. 关键注意事项 (Critical Checklist)

- **密钥管理:** 所有API Key（OpenAI, Twitter等）必须通过 `.env` 文件加载，绝不能硬编码或提交到Git。
- **成本监控:** 每次调用LLM时，都应log下使用的模型和token数量，便于未来追踪成本。
- **缓存策略:** 对相同的分析请求，应设置缓存（例如，1小时内对同一关键词的请求直接返回缓存结果），以大幅降低LLM成本。
- **错误处理:** 所有外部API调用（数据抓取、LLM）都必须包含在 `try...except`块中，并实现合理的重试逻辑（如backoff库）。
- **合规与隐私:** 只使用公开数据，并明确告知用户数据来源。在处理用户生成内容时，注意去除个人身份信息 (PII)。