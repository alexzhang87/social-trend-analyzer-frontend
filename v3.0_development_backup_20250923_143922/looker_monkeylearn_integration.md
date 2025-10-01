# Looker Studio + MonkeyLearn 直接可用功能集成指南

## 🎯 Looker Studio 可直接嵌入的图表功能

### ✅ **免费嵌入功能**
Looker Studio支持通过iframe嵌入报告，可以选择"Anyone with the link can view"权限设置，这些图表你可以直接使用：

#### 📊 **基础图表类型**
```javascript
// 可直接嵌入的图表
const availableCharts = {
  "折线图": "时间序列数据，如品牌提及量趋势",
  "条形图": "平台对比、竞品声量对比", 
  "饼图": "情感分布、平台分布",
  "散点图": "用户活跃度vs影响力分析",
  "热力图": "最佳发布时间、地理分布",
  "表格": "竞品分析详细数据",
  "计分卡": "KPI指标展示（总提及量、情感得分）",
  "地理图": "用户分布地图",
  "漏斗图": "用户转化路径",
  "雷达图": "产品功能对比分析"
}
```

#### 🔧 **嵌入实现方式**
```html
<!-- 直接iframe嵌入 -->
<iframe 
  src="https://datastudio.google.com/embed/reporting/[REPORT_ID]/page/[PAGE_ID]"
  width="100%" 
  height="400"
  frameborder="0" 
  allowfullscreen>
</iframe>

<!-- JavaScript SDK嵌入 (更多控制) -->
<script src="https://apis.google.com/js/api.js"></script>
<div id="looker-chart"></div>
<script>
  // 动态加载图表
  function loadChart() {
    gapi.load('client', function() {
      // 配置图表参数
    });
  }
</script>
```

### 💰 **收费功能** 
完整的嵌入式分析功能通常需要每月$5,000以上的费用，包括：
- 白标签嵌入
- 用户权限管理
- 高级API访问
- 企业级安全

---

## 🤖 MonkeyLearn 可直接调用的API功能

### ✅ **核心分析功能**
MonkeyLearn提供预训练模型和自定义模型，包括情感分析、主题检测等，支持Python、Ruby、Node、Java和PHP的SDK

#### 📈 **1. 情感分析 (Sentiment Analysis)**
```python
# 直接可用的API调用
import monkeylearn

ml = MonkeyLearn('your-api-key')
model_id = 'cl_pi3C7JiL'  # 预训练情感分析模型

# 分析文本情感
result = ml.classifiers.classify(model_id, [
    'I love this new product!',
    'This feature is terrible',
    'It\'s okay, nothing special'
])

# 返回结果
{
  "positive": 0.85,  # 85%正面
  "negative": 0.10,  # 10%负面  
  "neutral": 0.05    # 5%中性
}
```

#### 🏷️ **2. 主题分类 (Topic Classification)**
```python
# 预训练主题分类器
topic_model = 'cl_5icAVzKR'

result = ml.classifiers.classify(topic_model, [
    'The new iPhone camera is amazing',
    'Battery life could be better', 
    'Love the design and build quality'
])

# 返回主题标签
[
    {'label': 'Camera', 'confidence': 0.92},
    {'label': 'Battery', 'confidence': 0.88},
    {'label': 'Design', 'confidence': 0.91}
]
```

#### 🔍 **3. 关键词提取 (Keyword Extraction)**
```python
# 关键词提取器
extractor_model = 'ex_YCya9nrn'

result = ml.extractors.extract(extractor_model, [
    'This startup has amazing AI technology but poor customer service'
])

# 提取关键词
[
    {'keyword': 'AI technology', 'relevance': 0.95},
    {'keyword': 'customer service', 'relevance': 0.87},
    {'keyword': 'startup', 'relevance': 0.75}
]
```

#### 🎯 **4. 意图识别 (Intent Detection)**
```python
# 自定义意图分类器
intent_model = 'cl_custom_intent'

result = ml.classifiers.classify(intent_model, [
    'I want to buy this product',
    'How much does it cost?',
    'This is broken, I need help'
])

# 返回用户意图
[
    {'intent': 'Purchase', 'confidence': 0.89},
    {'intent': 'Pricing_Inquiry', 'confidence': 0.92}, 
    {'intent': 'Support_Request', 'confidence': 0.94}
]
```

### 💡 **实际应用场景**

#### 🔄 **实时数据处理流程**
```python
# 完整的数据处理管道
def analyze_social_mentions(text_data):
    results = {}
    
    # 1. 情感分析
    sentiment = ml.classifiers.classify('cl_pi3C7JiL', text_data)
    results['sentiment'] = sentiment
    
    # 2. 主题分类  
    topics = ml.classifiers.classify('cl_5icAVzKR', text_data)
    results['topics'] = topics
    
    # 3. 关键词提取
    keywords = ml.extractors.extract('ex_YCya9nrn', text_data)
    results['keywords'] = keywords
    
    return results

# 处理Twitter数据
twitter_mentions = [
    "Love the new update!",
    "Bug in the payment system", 
    "Great customer support team"
]

analysis_results = analyze_social_mentions(twitter_mentions)
```

---

## 🔗 集成到你的Dashboard

### 📊 **Looker Studio + MonkeyLearn 组合使用**

#### **方案1: 数据预处理 → Looker可视化**
```python
# Step 1: MonkeyLearn分析数据
def process_social_data():
    raw_data = get_social_mentions()  # 获取社媒数据
    
    analyzed_data = []
    for mention in raw_data:
        # MonkeyLearn分析
        sentiment = ml.classifiers.classify('cl_pi3C7JiL', [mention['text']])
        topics = ml.classifiers.classify('cl_5icAVzKR', [mention['text']])
        
        analyzed_data.append({
            'text': mention['text'],
            'platform': mention['platform'],
            'date': mention['date'],
            'sentiment_score': sentiment[0]['probability'],
            'sentiment_label': sentiment[0]['label'],
            'topic': topics[0]['label']
        })
    
    return analyzed_data

# Step 2: 推送到Google Sheets (作为Looker数据源)
def update_looker_data(analyzed_data):
    # 更新Google Sheets
    worksheet.update_with_dataframe(df_analyzed_data)
    
    # Looker Studio自动刷新图表
```

#### **方案2: 实时API + 嵌入式图表**
```html
<!-- 网站中的实时Dashboard -->
<div class="dashboard-container">
  <!-- MonkeyLearn实时分析结果 -->
  <div class="sentiment-widget">
    <h3>实时情感分析</h3>
    <div id="sentiment-gauge"></div>
  </div>
  
  <!-- Looker Studio嵌入图表 -->
  <div class="trends-chart">
    <iframe 
      src="https://datastudio.google.com/embed/reporting/[YOUR_REPORT_ID]"
      width="100%" 
      height="400">
    </iframe>
  </div>
</div>

<script>
// 每30分钟更新MonkeyLearn数据
setInterval(async () => {
  const latestMentions = await fetchLatestMentions();
  const sentiment = await analyzeWithMonkeyLearn(latestMentions);
  updateSentimentWidget(sentiment);
}, 30 * 60 * 1000);
</script>
```

---

## 💰 **成本估算**

### **MonkeyLearn定价** 
MonkeyLearn提供多种定价计划，包括免费层和付费企业版
- **免费版**: 1,000次API调用/月
- **专业版**: $299/月，100,000次调用
- **企业版**: 定制价格，无限调用

### **Looker Studio定价**
- **基础版**: 免费 (有Google品牌水印)
- **专业版**: $10/用户/月 (无品牌水印)
- **嵌入式**: $5,000+/月 (白标签)

### **推荐方案 (MVP阶段)**
```
总成本: ~$309/月
- MonkeyLearn专业版: $299/月
- Looker Studio免费版: $0/月  
- Google Sheets数据连接: $10/月
```

---

## 🚀 **立即可实现的功能**

### ✅ **第一周可上线**
1. **情感分析仪表板**: MonkeyLearn API + Looker饼图
2. **趋势分析**: Google Sheets + Looker折线图
3. **竞品对比**: 条形图展示竞品提及量

### ✅ **第二周可优化**  
1. **主题分类**: 自动标记用户讨论话题
2. **关键词云**: 提取高频关键词
3. **实时警报**: 情感急剧变化时发送通知

### ✅ **第三周可扩展**
1. **预测模型**: 基于历史数据预测趋势
2. **用户画像**: 结合多个分类器分析用户特征
3. **ROI分析**: 营销活动效果量化

这样你就可以立即开始集成这两个工具，快速搭建MVP版本的数据分析平台！