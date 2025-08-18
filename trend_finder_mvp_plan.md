# Trend-Finder MVP 产品规划与开发指南

## 产品架构总览

```
用户输入关键词 → 前端验证 → 后端API处理 → 数据获取 → AI分析 → 结果返回 → 前端可视化
```

## 核心功能模块划分

### 模块1: 搜索输入界面 (Search Interface)

**产品需求：**
- 用户能够快速输入关键词并选择分析参数
- 界面简洁，避免选择困惑
- 提供即时的参数验证反馈

**前端职责：**
- 渲染搜索表单
- 实时验证用户输入
- 管理加载状态
- 处理错误提示

**后端职责：**
- 验证API请求参数
- 返回参数错误信息
- 记录请求日志（可选）

---

### 模块2: 数据获取与处理 (Data Processing)

**产品需求：**
- 从Twitter/Reddit获取关键词相关数据
- 数据清洗和标准化
- 按时间维度聚合数据

**前端职责：**
- 发起API请求
- 显示处理进度
- 处理超时和错误

**后端职责：**
- 调用Twitter.io和Reddit API
- 数据清洗和去重
- 时间序列数据聚合
- 异常处理和重试机制

---

### 模块3: AI洞察生成 (AI Insights)

**产品需求：**
- 基于原始数据生成用户痛点分析
- 识别潜在商业机会
- 输出格式化、可操作的建议

**前端职责：**
- 展示AI分析结果
- 格式化文本显示
- 提供结果操作(复制等)

**后端职责：**
- 构建高质量的AI prompt
- 调用GPT-4o-mini API
- 结果解析和格式化
- 置信度评估

---

### 模块4: 数据可视化 (Data Visualization)

**产品需求：**
- 清晰的趋势图表展示
- 关键指标突出显示
- 响应式设计适配

**前端职责：**
- 渲染图表组件
- 数据动画效果
- 交互功能(hover, tooltip)
- 移动端适配

**后端职责：**
- 生成图表友好的数据格式
- 计算关键指标
- 优化数据传输大小

## 技术栈选型

### 前端技术栈
```
- Framework: React 18 + TypeScript
- Styling: Tailwind CSS
- Charts: Recharts
- HTTP Client: Axios
- State Management: useState/useEffect
- Build Tool: Vite
```

### 后端技术栈
```
- Framework: Node.js + Express
- Language: TypeScript
- API Client: Axios
- Environment: dotenv
- CORS: cors middleware
- Validation: joi
```

## API设计规范

### 核心分析接口
```
POST /api/analyze
Content-Type: application/json

Request:
{
  "keyword": "AI toys",
  "platforms": ["twitter", "reddit"],
  "timeRange": "7days"
}

Response:
{
  "success": true,
  "data": {
    "trendData": [
      { "date": "2024-01-01", "twitter": 45, "reddit": 23 },
      { "date": "2024-01-02", "twitter": 52, "reddit": 31 }
    ],
    "metrics": {
      "totalMentions": 234,
      "dominantPlatform": "twitter",
      "trendDirection": "rising"
    },
    "insights": {
      "painPoints": [
        {
          "title": "High Cost Barrier",
          "description": "Users frequently mention AI toys being too expensive",
          "confidence": 0.85
        }
      ],
      "opportunities": [
        {
          "title": "Budget-Friendly AI Toys",
          "description": "Market gap for affordable AI toy alternatives",
          "potential": "high"
        }
      ]
    }
  },
  "meta": {
    "processingTime": 45,
    "dataPoints": 500
  }
}
```

## 开发阶段规划

### Phase 1: 基础架构 (Day 1-2)
- [ ] 前端项目初始化
- [ ] 后端API框架搭建
- [ ] 基础路由和中间件
- [ ] 开发环境配置

### Phase 2: 核心功能 (Day 3-4)
- [ ] 搜索界面开发
- [ ] 数据获取服务
- [ ] AI分析集成
- [ ] 前后端联调

### Phase 3: 可视化与优化 (Day 5-6)
- [ ] 图表组件开发
- [ ] 响应式布局优化
- [ ] 错误处理完善
- [ ] 性能优化

### Phase 4: 部署与测试 (Day 7)
- [ ] 生产环境部署
- [ ] 端到端测试
- [ ] 用户接受测试
- [ ] 问题修复

## 成本预算规划

### API调用成本
```
Twitter.io: $20/月 (10万条数据)
Reddit API: 免费层级
GPT-4o-mini: $30/月 (预估50万tokens)
总计: $50/月 (支持约200次分析)
```

### 开发和部署成本
```
Vercel/Netlify: 免费层级
域名: $12/年
监控工具: 免费层级
总计: $12/年 + $50/月运营成本
```
