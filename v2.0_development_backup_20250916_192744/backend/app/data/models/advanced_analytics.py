from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .database import Base

class CompetitiveAnalysis(Base):
    __tablename__ = "competitive_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brands = Column(JSON)  # 对比的品牌列表
    analysis_result = Column(JSON)  # 分析结果
    analysis_type = Column(String(50), default="competitive")  # 分析类型
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TimeSeriesAnalysis(Base):
    __tablename__ = "timeseries_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keywords = Column(JSON)
    time_range = Column(String(50))  # 7d, 30d, 90d, 1y
    forecast_data = Column(JSON)
    trend_score = Column(Float)  # 趋势评分
    seasonality_detected = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InfluenceAnalysis(Base):
    __tablename__ = "influence_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keywords = Column(JSON)
    influencers_data = Column(JSON)  # 影响者数据
    network_metrics = Column(JSON)  # 网络指标
    viral_content = Column(JSON)  # 病毒式传播内容
    influence_score = Column(Float)  # 整体影响力评分
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SemanticAnalysis(Base):
    __tablename__ = "semantic_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keywords = Column(JSON)
    topics_data = Column(JSON)  # 主题建模结果
    entities_data = Column(JSON)  # 实体识别结果
    content_quality_score = Column(Float)  # 内容质量评分
    semantic_similarity = Column(JSON)  # 语义相似度矩阵
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BusinessIntelligence(Base):
    __tablename__ = "business_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keywords = Column(JSON)
    market_opportunities = Column(JSON)  # 市场机会
    user_needs = Column(JSON)  # 用户需求分析
    roi_predictions = Column(JSON)  # ROI预测
    growth_opportunities = Column(JSON)  # 增长机会
    business_score = Column(Float)  # 商业价值评分
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdvancedAnalysisTask(Base):
    __tablename__ = "advanced_analysis_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(100), unique=True, index=True)  # UUID
    analysis_type = Column(String(50))  # competitive, timeseries, influence, semantic, business
    keywords = Column(JSON)
    parameters = Column(JSON)  # 分析参数
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    result_id = Column(Integer)  # 关联到具体分析结果表的ID
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)