"""
数据质量API端点
提供数据质量检查、去重、清洗和异常检测的REST接口
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import json
import pandas as pd
from io import StringIO

from ...data.models.database import get_db, User
from ...core.auth import get_current_user
from ...services.data_quality_service import (
    data_quality_service,
    QualityMetrics,
    DuplicationResult,
    AnomalyResult,
    DataQualityLevel
)

router = APIRouter()

# Pydantic模型定义

class DataQualityRequest(BaseModel):
    """数据质量检查请求"""
    data: Dict[str, Any] = Field(..., description="待检查的数据")
    check_duplicates: bool = Field(True, description="是否检查重复")
    detect_anomalies: bool = Field(True, description="是否检测异常")

class TextCleaningRequest(BaseModel):
    """文本清洗请求"""
    text: str = Field(..., description="待清洗的文本")
    normalize_language: bool = Field(True, description="是否标准化语言")
    remove_emojis: bool = Field(False, description="是否移除表情符号")

class BatchQualityRequest(BaseModel):
    """批量质量检查请求"""
    data_batch: List[Dict[str, Any]] = Field(..., description="数据批次")
    generate_report: bool = Field(True, description="是否生成报告")

class DuplicationCheckRequest(BaseModel):
    """重复检查请求"""
    text: str = Field(..., description="待检查的文本")
    data_id: Optional[str] = Field(None, description="数据ID")

class QualityMetricsResponse(BaseModel):
    """质量指标响应"""
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    uniqueness: float
    relevance: float
    overall_score: float
    level: str

class DuplicationResultResponse(BaseModel):
    """去重结果响应"""
    is_duplicate: bool
    similarity_score: float
    duplicate_id: Optional[str]
    duplicate_type: str

class AnomalyResultResponse(BaseModel):
    """异常检测结果响应"""
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    description: str

class QualityReportResponse(BaseModel):
    """质量报告响应"""
    timestamp: str
    total_records: int
    quality_distribution: Dict[str, Dict[str, float]]
    average_scores: Dict[str, float]
    recommendations: List[str]

# API端点

@router.post("/assess", response_model=QualityMetricsResponse)
async def assess_data_quality(
    request: DataQualityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    评估数据质量
    """
    try:
        quality_metrics = await data_quality_service.assess_data_quality(request.data)
        
        return QualityMetricsResponse(
            completeness=quality_metrics.completeness,
            accuracy=quality_metrics.accuracy,
            consistency=quality_metrics.consistency,
            validity=quality_metrics.validity,
            uniqueness=quality_metrics.uniqueness,
            relevance=quality_metrics.relevance,
            overall_score=quality_metrics.overall_score,
            level=quality_metrics.level.value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing data quality: {str(e)}")

@router.post("/check-duplication", response_model=DuplicationResultResponse)
async def check_duplication(
    request: DuplicationCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检查数据重复
    """
    try:
        duplication_result = await data_quality_service.check_duplication(
            request.text, 
            request.data_id
        )
        
        return DuplicationResultResponse(
            is_duplicate=duplication_result.is_duplicate,
            similarity_score=duplication_result.similarity_score,
            duplicate_id=duplication_result.duplicate_id,
            duplicate_type=duplication_result.duplicate_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking duplication: {str(e)}")

@router.post("/clean-text")
async def clean_text(
    request: TextCleaningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清洗文本数据
    """
    try:
        cleaned_text = await data_quality_service.clean_text_data(request.text)
        
        return {
            "original_text": request.text,
            "cleaned_text": cleaned_text,
            "original_length": len(request.text),
            "cleaned_length": len(cleaned_text),
            "reduction_ratio": (len(request.text) - len(cleaned_text)) / len(request.text) if request.text else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning text: {str(e)}")

@router.post("/detect-anomalies")
async def detect_anomalies(
    request: DataQualityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检测数据异常
    """
    try:
        anomalies = await data_quality_service.detect_anomalies(request.data)
        
        anomaly_responses = [
            AnomalyResultResponse(
                is_anomaly=anomaly.is_anomaly,
                anomaly_score=anomaly.anomaly_score,
                anomaly_type=anomaly.anomaly_type,
                description=anomaly.description
            )
            for anomaly in anomalies
        ]
        
        return {
            "data_id": request.data.get("id", "unknown"),
            "anomaly_count": len(anomaly_responses),
            "has_anomalies": len(anomaly_responses) > 0,
            "anomalies": anomaly_responses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")

@router.post("/batch-assess", response_model=QualityReportResponse)
async def batch_quality_assessment(
    request: BatchQualityRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量质量评估
    """
    try:
        if len(request.data_batch) > 1000:
            raise HTTPException(status_code=400, detail="Batch size too large. Maximum 1000 records allowed.")
        
        if request.generate_report:
            quality_report = await data_quality_service.generate_quality_report(request.data_batch)
            return QualityReportResponse(**quality_report)
        else:
            quality_metrics = await data_quality_service.batch_quality_check(request.data_batch)
            
            # 简化的响应
            total_count = len(quality_metrics)
            avg_score = sum(m.overall_score for m in quality_metrics) / total_count if total_count > 0 else 0
            
            return {
                "timestamp": "2024-01-01T00:00:00",
                "total_records": total_count,
                "quality_distribution": {},
                "average_scores": {"overall": avg_score},
                "recommendations": []
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch assessment: {str(e)}")

@router.post("/upload-csv")
async def upload_csv_for_quality_check(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传CSV文件进行质量检查
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # 读取CSV文件
        content = await file.read()
        csv_data = StringIO(content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        if len(df) > 1000:
            raise HTTPException(status_code=400, detail="CSV file too large. Maximum 1000 rows allowed.")
        
        # 转换为字典列表
        data_batch = df.to_dict('records')
        
        # 生成质量报告
        quality_report = await data_quality_service.generate_quality_report(data_batch)
        
        return {
            "filename": file.filename,
            "rows_processed": len(data_batch),
            "columns": list(df.columns),
            "quality_report": quality_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

@router.get("/quality-rules")
async def get_quality_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据质量规则
    """
    try:
        return {
            "quality_rules": data_quality_service.quality_rules,
            "quality_levels": [level.value for level in DataQualityLevel],
            "supported_languages": data_quality_service.quality_rules['allowed_languages']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quality rules: {str(e)}")

@router.put("/quality-rules")
async def update_quality_rules(
    rules: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新数据质量规则（仅管理员）
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only administrators can update quality rules")
        
        # 验证规则格式
        valid_keys = {
            'min_length', 'max_length', 'min_words', 'max_words',
            'min_sentences', 'max_sentences', 'allowed_languages',
            'spam_keywords', 'profanity_threshold'
        }
        
        for key in rules:
            if key not in valid_keys:
                raise HTTPException(status_code=400, detail=f"Invalid rule key: {key}")
        
        # 更新规则
        data_quality_service.quality_rules.update(rules)
        
        return {
            "message": "Quality rules updated successfully",
            "updated_rules": rules
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating quality rules: {str(e)}")

@router.get("/statistics")
async def get_quality_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据质量统计信息
    """
    try:
        return {
            "processed_hashes_count": len(data_quality_service.processed_hashes),
            "quality_rules": data_quality_service.quality_rules,
            "service_status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.delete("/cache")
async def clear_quality_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清除质量检查缓存（仅管理员）
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only administrators can clear cache")
        
        # 清除缓存
        cache_size = len(data_quality_service.processed_hashes)
        data_quality_service.processed_hashes.clear()
        
        return {
            "message": "Quality cache cleared successfully",
            "cleared_items": cache_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.post("/validate-schema")
async def validate_data_schema(
    schema: Dict[str, Any],
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    验证数据模式
    """
    try:
        validation_errors = []
        
        # 检查必需字段
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")
        
        # 检查字段类型
        field_types = schema.get('properties', {})
        for field, expected_type in field_types.items():
            if field in data:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type.get('type', 'string'):
                    validation_errors.append(f"Field {field} has type {actual_type}, expected {expected_type.get('type')}")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "schema": schema,
            "data_fields": list(data.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating schema: {str(e)}")