# 社交趋势分析平台 - 渐进式AI优化方案

## 📋 项目概述

**目标**：在4-6周内构建一个成本可控、效果优于现有基线、具备持续学习能力的AI增强分析系统。

**核心理念**：渐进优化，商业驱动 - 基于现有GLM-4.5基础设施，建立数据驱动的模型优化飞轮。

**技术基础**：
- 已有GLM-4.5模型集成和LLMProvider架构
- 现有LargeDatasetService提供1000+条训练数据
- 完整的Redis缓存和Celery异步任务处理能力
- 三级订阅商业化模式（FREE/STARTER/PRO）为差异化服务提供基础

## 🎯 核心价值主张

1. **商业驱动**：基于现有三级订阅模式，优先解决“情感分析”和“主题聚类”两个核心问题
2. **成本可控**：最大化利用现有GLM-4.5基础设施，阐释式使用轻量级模型处理高频请求
3. **数据闭环**：打通“用户反馈 → 数据标注 → 模型训练 → 服务优化 → 用户体验提升”的自动化流程
4. **风险可控**：保留现有分析流程作为降级方案，确保服务稳定性

## 📊 目标指标（渐进式实现）

### 第1-2周目标（MVP验证）
- 情感分类：F1-macro ≥ 0.60（基于现有数据）
- 主题聚类：一致性 ≥ 0.40（TF-IDF + K-means）
- 商业机会识别：简化规则引擎
- 系统延迟：P95 < 10秒

### 第3-4周目标（产品化）
- 情感分类：F1-macro ≥ 0.75
- 主题聚类：NMI ≥ 0.60，轮廓系数 ≥ 0.40
- 商业机会识别：Precision@K ≥ 0.50
- 系统延迟：P95 < 5秒

### 业务指标（基于现有商业化模式）
- 用户反馈正向率提升 ≥ 15%（第2周）→ 25%（第4周）
- 分析结果点击/收藏率提升 ≥ 10%（第2周）→ 20%（第4周）
- 单次分析成本下降 ≥ 20%（第3周）
- 订阅转化率提升 ≥ 5%（第4周）

## 📅 渐进式实施计划（4-6周）

### Day 1: 数据基建与治理

#### 任务1：创建数据清洗管道
**文件位置**：`backend/app/services/data_processing_service.py`

```python
class DataProcessingService:
    def __init__(self):
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but'])
        
    def clean_text(self, text: str) -> str:
        """标准化文本清洗"""
        # 小写化
        text = text.lower()
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # 移除特殊字符
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # 处理表情符号
        text = self.normalize_emojis(text)
        return text.strip()
        
    def normalize_emojis(self, text: str) -> str:
        """表情符号标准化"""
        # 将表情符号转换为文本描述
        return emoji.demojize(text)
```

#### 任务2：实现语义去重
```python
from datasketch import MinHashLSH, MinHash

class DeduplicationService:
    def __init__(self):
        self.lsh = MinHashLSH(threshold=0.8, num_perm=128)
        self.seen_hashes = {}
        
    def is_duplicate(self, text: str, time_window_hours: int = 24) -> bool:
        """检测近期重复内容"""
        minhash = self.create_minhash(text)
        
        # 检查LSH中是否有相似内容
        similar_docs = self.lsh.query(minhash)
        
        if similar_docs:
            # 检查时间窗口
            for doc_id in similar_docs:
                if self.is_within_time_window(doc_id, time_window_hours):
                    return True
        
        # 添加到LSH
        doc_id = f"doc_{len(self.seen_hashes)}"
        self.lsh.insert(doc_id, minhash)
        self.seen_hashes[doc_id] = {
            'timestamp': datetime.utcnow(),
            'text': text
        }
        
        return False
```

#### 任务3：建立用户反馈到标注库的桥梁
**数据库模型扩展**：
```python
class PendingAnnotation(Base):
    __tablename__ = "pending_annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("trend_analyses.id"))
    feedback_id = Column(Integer, ForeignKey("user_feedback.id"))
    source_text = Column(Text)
    predicted_sentiment = Column(String(20))
    predicted_topics = Column(JSON)
    user_correction = Column(JSON)  # 用户反馈的正确标签
    annotation_status = Column(String(20), default="pending")  # pending, reviewed, annotated
    priority_score = Column(Float, default=0.0)  # 标注优先级
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Day 2-3: V1模型训练

#### 任务4：弱监督自动标注
**文件位置**：`backend/app/services/auto_annotation_service.py`

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

class AutoAnnotationService:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.topic_keywords = {
            'technology': ['ai', 'tech', 'software', 'app', 'digital'],
            'business': ['market', 'sales', 'revenue', 'profit', 'company'],
            'social': ['community', 'people', 'social', 'culture', 'society']
        }
        
    def auto_annotate_sentiment(self, text: str) -> dict:
        """自动情感标注"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'confidence': abs(scores['compound']),
            'scores': scores
        }
        
    def auto_annotate_topics(self, text: str) -> list:
        """自动主题标注"""
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                detected_topics.append({
                    'topic': topic,
                    'score': score / len(keywords),
                    'matched_keywords': [kw for kw in keywords if kw in text_lower]
                })
                
        return sorted(detected_topics, key=lambda x: x['score'], reverse=True)
```

#### 任务5：训练情感分类器V1
**文件位置**：`backend/app/ml/sentiment_classifier.py`

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import torch

class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
        
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class SentimentClassifierTrainer:
    def __init__(self, model_name='distilbert-base-uncased'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=3  # positive, negative, neutral
        )
        
    def train(self, train_texts, train_labels, val_texts, val_labels):
        """训练情感分类器"""
        train_dataset = SentimentDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = SentimentDataset(val_texts, val_labels, self.tokenizer)
        
        training_args = TrainingArguments(
            output_dir='./sentiment_model',
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        trainer.train()
        return trainer
```

#### 任务6：训练主题模型V1
**文件位置**：`backend/app/ml/topic_classifier.py`

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
import numpy as np

class TopicClassifier:
    def __init__(self, n_topics=10, max_features=1000):
        self.n_topics = n_topics
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.nmf_model = NMF(n_components=n_topics, random_state=42)
        self.topic_labels = []
        
    def fit(self, texts):
        """训练主题模型"""
        # TF-IDF向量化
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # NMF主题建模
        self.nmf_model.fit(tfidf_matrix)
        
        # 生成主题标签
        feature_names = self.vectorizer.get_feature_names_out()
        self.topic_labels = self._generate_topic_labels(feature_names)
        
        return self
        
    def predict(self, texts):
        """预测文本主题"""
        tfidf_matrix = self.vectorizer.transform(texts)
        topic_weights = self.nmf_model.transform(tfidf_matrix)
        
        # 获取主要主题
        main_topics = np.argmax(topic_weights, axis=1)
        topic_scores = np.max(topic_weights, axis=1)
        
        results = []
        for i, (topic_idx, score) in enumerate(zip(main_topics, topic_scores)):
            results.append({
                'main_topic': self.topic_labels[topic_idx],
                'topic_id': int(topic_idx),
                'confidence': float(score),
                'all_topics': {
                    self.topic_labels[j]: float(topic_weights[i][j]) 
                    for j in range(self.n_topics)
                }
            })
            
        return results
        
    def _generate_topic_labels(self, feature_names):
        """生成主题标签"""
        labels = []
        for topic_idx in range(self.n_topics):
            top_words = [feature_names[i] for i in 
                        self.nmf_model.components_[topic_idx].argsort()[-5:][::-1]]
            labels.append('_'.join(top_words[:3]))
        return labels
```

### Day 4: RAG增强与LLM集成

#### 任务7：实现简版RAG
**文件位置**：`backend/app/services/rag_service.py`

```python
import json
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleRAGService:
    def __init__(self):
        self.knowledge_base = {}
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.topic_vectors = None
        
    def build_knowledge_base(self, topics_data: List[Dict]):
        """构建知识库"""
        self.knowledge_base = {
            topic['name']: {
                'keywords': topic['keywords'],
                'description': topic['description'],
                'context': topic.get('context', ''),
                'business_implications': topic.get('business_implications', [])
            }
            for topic in topics_data
        }
        
        # 构建向量索引
        topic_texts = [f"{topic['description']} {' '.join(topic['keywords'])}" 
                      for topic in topics_data]
        self.topic_vectors = self.vectorizer.fit_transform(topic_texts)
        
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索相关上下文"""
        if not self.topic_vectors:
            return []
            
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.topic_vectors)[0]
        
        # 获取最相似的主题
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        topic_names = list(self.knowledge_base.keys())
        
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 相似度阈值
                topic_name = topic_names[idx]
                results.append({
                    'topic': topic_name,
                    'similarity': float(similarities[idx]),
                    'context': self.knowledge_base[topic_name]
                })
                
        return results
```

#### 任务8：改造LLM调用逻辑
**文件位置**：`backend/app/services/enhanced_llm_service.py`

```python
from .llm_service import LLMProvider
from .rag_service import SimpleRAGService
from typing import Dict, List

class EnhancedLLMService:
    def __init__(self, llm_provider: LLMProvider, rag_service: SimpleRAGService):
        self.llm_provider = llm_provider
        self.rag_service = rag_service
        
    def generate_enhanced_analysis(self, 
                                 text_data: List[str],
                                 sentiment_results: List[Dict],
                                 topic_results: List[Dict],
                                 keywords: List[str]) -> Dict:
        """生成增强分析"""
        
        # 1. 聚合小模型结果
        sentiment_summary = self._summarize_sentiments(sentiment_results)
        topic_summary = self._summarize_topics(topic_results)
        
        # 2. RAG检索相关上下文
        query = f"{' '.join(keywords)} {topic_summary['main_topics']}"
        context = self.rag_service.retrieve_context(query)
        
        # 3. 构建增强Prompt
        enhanced_prompt = self._build_enhanced_prompt(
            keywords, sentiment_summary, topic_summary, context
        )
        
        # 4. 调用LLM生成洞察
        insights = self.llm_provider.generate_response(enhanced_prompt)
        
        return {
            'sentiment_analysis': sentiment_summary,
            'topic_analysis': topic_summary,
            'context_retrieved': context,
            'business_insights': insights,
            'confidence_score': self._calculate_confidence(sentiment_results, topic_results)
        }
        
    def _build_enhanced_prompt(self, keywords, sentiment_summary, topic_summary, context):
        """构建增强Prompt"""
        context_text = "\n".join([
            f"- {ctx['topic']}: {ctx['context']['description']}"
            for ctx in context
        ])
        
        prompt = f"""
        基于以下分析结果，生成深度商业洞察：
        
        关键词：{', '.join(keywords)}
        
        情感分析结果：
        - 正面情感：{sentiment_summary['positive_ratio']:.1%}
        - 负面情感：{sentiment_summary['negative_ratio']:.1%}
        - 中性情感：{sentiment_summary['neutral_ratio']:.1%}
        - 主要情感趋势：{sentiment_summary['dominant_sentiment']}
        
        主题分析结果：
        - 核心主题：{', '.join(topic_summary['main_topics'])}
        - 主题分布：{topic_summary['topic_distribution']}
        
        相关背景知识：
        {context_text}
        
        请基于以上信息，生成：
        1. 市场趋势分析
        2. 用户情感洞察
        3. 商业机会识别
        4. 风险预警
        5. 行动建议
        
        要求：具体、可执行、有数据支撑。
        """
        
        return prompt
```

### Day 5: 服务化与API集成

#### 任务9：创建模型服务API
**文件位置**：`backend/app/api/models.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from ..ml.sentiment_classifier import SentimentClassifierTrainer
from ..ml.topic_classifier import TopicClassifier
from ..services.enhanced_llm_service import EnhancedLLMService

router = APIRouter(prefix="/api/v1/models", tags=["models"])

# 全局模型实例
sentiment_model = None
topic_model = None
enhanced_llm = None

class TextAnalysisRequest(BaseModel):
    texts: List[str]
    include_sentiment: bool = True
    include_topics: bool = True
    include_insights: bool = False
    keywords: List[str] = []

class TextAnalysisResponse(BaseModel):
    sentiment_results: List[Dict] = []
    topic_results: List[Dict] = []
    business_insights: Dict = {}
    processing_time: float
    confidence_score: float

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_texts(request: TextAnalysisRequest):
    """文本分析API"""
    import time
    start_time = time.time()
    
    try:
        results = {
            'sentiment_results': [],
            'topic_results': [],
            'business_insights': {},
            'confidence_score': 0.0
        }
        
        # 情感分析
        if request.include_sentiment and sentiment_model:
            results['sentiment_results'] = sentiment_model.predict(request.texts)
            
        # 主题分析
        if request.include_topics and topic_model:
            results['topic_results'] = topic_model.predict(request.texts)
            
        # 商业洞察生成
        if request.include_insights and enhanced_llm:
            insights = enhanced_llm.generate_enhanced_analysis(
                request.texts,
                results['sentiment_results'],
                results['topic_results'],
                request.keywords
            )
            results['business_insights'] = insights
            results['confidence_score'] = insights.get('confidence_score', 0.0)
            
        processing_time = time.time() - start_time
        results['processing_time'] = processing_time
        
        return TextAnalysisResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/retrain/sentiment")
async def retrain_sentiment_model():
    """重新训练情感模型"""
    global sentiment_model
    try:
        # 从数据库获取最新标注数据
        # 重新训练模型
        # 更新全局模型实例
        return {"status": "success", "message": "Sentiment model retrained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@router.post("/retrain/topics")
async def retrain_topic_model():
    """重新训练主题模型"""
    global topic_model
    try:
        # 从数据库获取最新数据
        # 重新训练模型
        # 更新全局模型实例
        return {"status": "success", "message": "Topic model retrained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")
```

#### 任务10：更新主分析流程
**文件位置**：修改 `backend/app/services/analysis_service.py`

```python
# 在现有的 AnalysisService 类中添加

from .enhanced_llm_service import EnhancedLLMService
from ..api.models import TextAnalysisRequest
import httpx

class AnalysisService:
    def __init__(self):
        # ... 现有初始化代码 ...
        self.model_api_base = "http://localhost:8000/api/v1/models"
        
    async def analyze_with_enhanced_models(self, keywords: List[str], data: List[Dict]) -> Dict:
        """使用增强模型进行分析"""
        
        # 1. 提取文本数据
        texts = [item.get('text', '') for item in data if item.get('text')]
        
        if not texts:
            return await self.analyze_standard(keywords, data)  # 回退到原有方法
            
        try:
            # 2. 调用模型API进行分析
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.model_api_base}/analyze",
                    json={
                        "texts": texts[:100],  # 限制数量避免超时
                        "include_sentiment": True,
                        "include_topics": True,
                        "include_insights": True,
                        "keywords": keywords
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    model_results = response.json()
                    
                    # 3. 整合结果
                    enhanced_analysis = self._integrate_model_results(
                        keywords, data, model_results
                    )
                    
                    return enhanced_analysis
                else:
                    logger.warning(f"Model API failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            
        # 4. 失败时回退到原有分析方法
        return await self.analyze_standard(keywords, data)
        
    def _integrate_model_results(self, keywords: List[str], raw_data: List[Dict], model_results: Dict) -> Dict:
        """整合模型结果"""
        
        # 基础统计
        total_posts = len(raw_data)
        total_engagement = sum(item.get('likes', 0) + item.get('retweets', 0) for item in raw_data)
        
        # 情感分析结果
        sentiment_results = model_results.get('sentiment_results', [])
        sentiment_distribution = self._calculate_sentiment_distribution(sentiment_results)
        
        # 主题分析结果
        topic_results = model_results.get('topic_results', [])
        topic_distribution = self._calculate_topic_distribution(topic_results)
        
        # 商业洞察
        business_insights = model_results.get('business_insights', {})
        
        return {
            "keywords": keywords,
            "summary": {
                "total_posts": total_posts,
                "total_engagement": total_engagement,
                "sentiment_score": sentiment_distribution.get('overall_score', 0),
                "confidence_score": model_results.get('confidence_score', 0)
            },
            "sentiment_analysis": sentiment_distribution,
            "topic_analysis": topic_distribution,
            "business_insights": business_insights,
            "top_posts": self._get_top_posts(raw_data, sentiment_results),
            "trends": self._analyze_trends(raw_data, sentiment_results, topic_results),
            "recommendations": business_insights.get('recommendations', [])
        }
```

### Day 6-7: 评估、部署与规划

#### 任务11：建立评估体系
**文件位置**：`backend/app/ml/evaluation_service.py`

```python
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.metrics import normalized_mutual_info_score, silhouette_score
import numpy as np
from typing import List, Dict

class ModelEvaluationService:
    def __init__(self):
        self.golden_dataset = []  # 黄金标准数据集
        
    def load_golden_dataset(self, file_path: str):
        """加载黄金标准数据集"""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            self.golden_dataset = json.load(f)
            
    def evaluate_sentiment_model(self, model, test_texts: List[str], true_labels: List[str]) -> Dict:
        """评估情感分析模型"""
        predictions = model.predict(test_texts)
        pred_labels = [pred['sentiment'] for pred in predictions]
        
        accuracy = accuracy_score(true_labels, pred_labels)
        f1_macro = f1_score(true_labels, pred_labels, average='macro')
        f1_weighted = f1_score(true_labels, pred_labels, average='weighted')
        
        report = classification_report(true_labels, pred_labels, output_dict=True)
        
        return {
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
            'classification_report': report,
            'confusion_matrix': self._calculate_confusion_matrix(true_labels, pred_labels)
        }
        
    def evaluate_topic_model(self, model, test_texts: List[str], true_topics: List[List[str]]) -> Dict:
        """评估主题模型"""
        predictions = model.predict(test_texts)
        
        # 计算主题一致性
        topic_consistency = self._calculate_topic_consistency(predictions, true_topics)
        
        # 计算主题多样性
        topic_diversity = self._calculate_topic_diversity(predictions)
        
        return {
            'topic_consistency': topic_consistency,
            'topic_diversity': topic_diversity,
            'average_confidence': np.mean([pred['confidence'] for pred in predictions])
        }
        
    def generate_evaluation_report(self, sentiment_eval: Dict, topic_eval: Dict) -> str:
        """生成评估报告"""
        report = f"""
# 模型评估报告

## 情感分析模型
- 准确率: {sentiment_eval['accuracy']:.3f}
- F1分数(宏平均): {sentiment_eval['f1_macro']:.3f}
- F1分数(加权平均): {sentiment_eval['f1_weighted']:.3f}

## 主题分析模型
- 主题一致性: {topic_eval['topic_consistency']:.3f}
- 主题多样性: {topic_eval['topic_diversity']:.3f}
- 平均置信度: {topic_eval['average_confidence']:.3f}

## 建议
{'✅ 模型性能良好' if sentiment_eval['f1_macro'] > 0.7 else '⚠️ 需要改进情感分析模型'}
{'✅ 主题识别效果良好' if topic_eval['topic_consistency'] > 0.6 else '⚠️ 需要改进主题模型'}
        """
        
        return report
```

#### 任务12：部署配置与监控
**文件位置**：`backend/app/core/model_config.py`

```python
from pydantic import BaseSettings
from typing import Dict, List

class ModelConfig(BaseSettings):
    # 模型路径配置
    SENTIMENT_MODEL_PATH: str = "./models/sentiment_v1"
    TOPIC_MODEL_PATH: str = "./models/topic_v1"
    RAG_KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base.json"
    
    # 性能配置
    MAX_BATCH_SIZE: int = 32
    MODEL_TIMEOUT: float = 30.0
    CACHE_TTL: int = 3600  # 1小时
    
    # 质量阈值
    MIN_CONFIDENCE_THRESHOLD: float = 0.5
    SENTIMENT_F1_THRESHOLD: float = 0.7
    TOPIC_CONSISTENCY_THRESHOLD: float = 0.6
    
    # 重训练配置
    RETRAIN_TRIGGER_THRESHOLD: int = 100  # 新标注数据达到100条时触发重训练
    RETRAIN_SCHEDULE: str = "0 2 * * 0"  # 每周日凌晨2点
    
    # 监控配置
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ENABLE_DRIFT_DETECTION: bool = True
    DRIFT_DETECTION_WINDOW: int = 7  # 7天
    
    class Config:
        env_file = ".env"

model_config = ModelConfig()
```

## 📈 V2阶段规划（第7-12周：深度优化）

### 第7-8周：数据驱动优化
1. **主动学习系统**
   - 实现不确定性采样算法
   - 建立半自动标注工作流（70%自动 + 20%人工验证 + 10%专家审核）
   - 优化标注质量控制机制

2. **A/B测试框架**
   - 实现模型版本管理系统
   - 建立在线实验平台
   - 监控关键业务指标（用户满意度、转化率、留存率）

3. **模型蒸馏优化**
   - 使用GLM-4.5输出训练轻量级模型
   - 实现知识蒸馏流程
   - 优化推理性能和成本控制

### 第9-10周：系统完善
1. **向量数据库集成**
   - 引入Chroma/FAISS向量数据库
   - 实现语义检索和相似匹配
   - 优化RAG效果和响应速度

2. **多模态支持**
   - 图像内容分析（社交媒体图片理解）
   - 视频内容理解（短视频趋势分析）
   - 多模态融合分析

3. **实时学习系统**
   - 在线学习算法实现
   - 概念漂移检测机制
   - 自适应模型更新系统

### 第11-12周：高级商业化
1. **企业级功能**
   - 多用户协作工作区
   - 高级数据导出和集成
   - 定制化分析模板

2. **API商业化**
   - RESTful API对外开放
   - API使用量计费模式
   - 合作伙伴集成方案

## 🎯 成功指标与里程碑

### 第1周目标
- [ ] 完成数据清洗和去重管道
- [ ] 训练出情感分析V1模型（F1 > 0.6）
- [ ] 训练出主题分析V1模型（一致性 > 0.5）
- [ ] 实现RAG增强的LLM调用
- [ ] 部署模型API服务
- [ ] 建立基础评估体系

### 第2周目标
- [ ] 用户反馈正向率提升10%
- [ ] 分析结果置信度提升15%
- [ ] 推理延迟控制在5秒内
- [ ] 建立自动重训练流程

### 第4周目标
- [ ] 情感分析F1达到0.8+
- [ ] 主题一致性达到0.7+
- [ ] 用户反馈正向率提升25%
- [ ] 分析成本降低30%

## 🔧 技术栈与依赖（基于现有架构）

### 已有技术基础
```txt
# 后端架构
FastAPI==0.104.1
SQLAlchemy==2.0.23
Celery[redis]==5.3.4
Redis==5.0.1
Uvicorn==0.24.0

# AI/ML集成
zhipuai==2.0.1  # GLM-4.5已集成
transformers==4.35.0
torch==2.1.0
scikit-learn==1.3.0

# 数据处理
numpy==1.24.0
pandas==2.0.0

# 前端架构
React 18 + TypeScript
Tailwind CSS
Recharts 3.1.2
```

### 新增依赖（渐进式添加）
```txt
# 第1-2周：基础模型
vaderSentiment==3.3.2  # 简化情感分析
jieba==0.42.1  # 中文分词支持
emojiapi  # 表情符号处理

# 第3-4周：进阶模型
datasketch==1.6.4  # 语义去重
sentence-transformers==2.2.2  # 语义相似度

# 第5-6周：向量检索（可选）
chromadb==0.4.15  # 向量数据库
faiss-cpu==1.7.4  # 相似性检索

# 监控和评估
wandb==0.15.0  # 实验跟踪（可选）
mlflow==2.7.0  # 模型管理（可选）
```

### 现有文件结构扩展
```
backend/app/
├── services/
│   ├── analysis_service.py  # 现有，需扩展
│   ├── llm_service.py       # 现有GLM-4.5集成
│   ├── large_dataset_service.py  # 现有数据服务
│   ├── enhanced_analysis_service.py  # 新增
│   ├── feedback_enhancement.py      # 新增
│   └── simple_models.py            # 新增
├── ml/  # 新增目录
│   ├── sentiment_analyzer.py
│   ├── topic_extractor.py
│   └── model_trainer.py
├── api/
│   ├── trends.py           # 现有，需更新
│   └── enhanced_trends.py  # 新增
└── data/models/
    ├── database.py         # 现有，需扩展
    └── training_models.py  # 新增
```

## ⚠️ 风险评估与缓解策略

### 高风险项及缓解方案

#### 1. 模型性能不达预期
**风险等级**: 高
**缓解策略**:
- 设置现实的baseline（F1 > 0.6），渐进改进
- 保留现有分析流程作为降级方案
- 实时监控模型表现，支持快速回滚

#### 2. 用户反馈数据质量不高
**风险等级**: 高
**缓解策略**:
- 实现多层验证机制：自动标注 + 人工验证 + 专家审核
- 使用GLM-4.5输出作为伪标签补充
- 建立激励机制鼓励高质量反馈

#### 3. 系统性能和成本问题
**风险等级**: 中
**缓解策略**:
- 逐步替代GLM调用，优先使用轻量级模型
- 实现智能缓存和结果复用
- 设置成本上限和自动降级机制

### 中低风险项

#### 4. 用户接受度不高
**风险等级**: 中
**缓解策略**:
- 灰度发布，先向部分用户开放
- A/B测试对比新旧版本效果
- 收集用户反馈并快速迭代

#### 5. 技术团队能力不足
**风险等级**: 低
**缓解策略**:
- 充分利用现有技术架构和代码基础
- 使用成熟的开源工具和框架
- 逐步学习和积累经验

---

## 📝 下一步详细方案

### 立即开始（本周）

#### Day 1-2: 环境准备和基础架构

**1. 更新后端依赖**
```bash
# 在backend/requirements.txt中添加
echo "vaderSentiment==3.3.2" >> backend/requirements.txt
echo "jieba==0.42.1" >> backend/requirements.txt
echo "emoji==2.8.0" >> backend/requirements.txt

# 安装依赖
cd backend && pip install -r requirements.txt
```

**2. 创建增强分析服务**
- 文件位置: `backend/app/services/enhanced_analysis_service.py`
- 继承现有`AnalysisService`类
- 实现三级分层分析逻辑

**3. 扩展数据库模型**
- 在`database.py`中添加反馈相关表
- 创建数据库迁移脚本

#### Day 3-5: 核心功能实现

**1. 实现简化模型**
```python
# 优先级顺序
1. VADER情感分析器增强版
2. TF-IDF + K-means主题聚类
3. 基于规则的商业机会识别
```

**2. API路由更新**
- 在`main.py`中注册新的增强分析API
- 更新现有`trends.py`路由支持分层分析

**3. 前端集成**
- 更新`trend-analyzer.tsx`组件
- 添加反馈收集功能

#### Day 6-7: 测试和优化

**1. 单元测试**
```bash
# 创建测试文件
touch backend/test_enhanced_analysis.py
touch backend/test_simple_models.py
```

**2. 集成测试**
- 测试不同订阅等级的分析结果
- 验证性能指标（延迟 < 10秒）

**3. 灰度发布准备**
- 配置特性开关（feature flag）
- 准备A/B测试环境

### 第2周计划

#### Day 8-10: 用户反馈系统
- 完善反馈收集API
- 实现反馈数据分析仪表板
- 建立数据标注工作流

#### Day 11-14: 数据收集和评估
- 向部分用户开放增强功能
- 收集初期反馈数据
- 评估模型基础性能

### 每周检查点

**关键指标监控**:
- 用户满意度评分
- 系统响应时间
- 错误率和异常监控
- 模型预测准确率

**风险评估**:
- 每周评估技术风险
- 用户反馈分析
- 成本和资源使用情况

**调整策略**:
- 根据实际数据调整目标
- 优化模型参数和算法
- 更新风险缓解措施

---

## ✅ 行动清单

### 立即执行项目
- [ ] **高优先级**: 创建`enhanced_analysis_service.py`
- [ ] **高优先级**: 实现VADER增强情感分析
- [ ] **中优先级**: 扩展数据库模型支持反馈
- [ ] **中优先级**: 更新API路由支持分层分析
- [ ] **低优先级**: 创建单元测试

### 第2周项目
- [ ] 用户反馈收集系统
- [ ] A/B测试框架搭建
- [ ] 数据标注工作流
- [ ] 性能监控仪表板

### 长期规划项目
- [ ] 向量数据库集成（第5-6周）
- [ ] 高级模型训练（第7-8周）
- [ ] 多模态分析支持（第9-10周）
- [ ] API商业化开放（第11-12周）

---

**总结**: 这个修正后的方案更加务实和可执行，基于您现有的技术基础和商业化模式，采用渐进式方法降低风险，确保每个阶段都有明确的价值输出和可衡量的成果。
```
