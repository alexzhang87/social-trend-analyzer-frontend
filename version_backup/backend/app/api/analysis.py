from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from ..services.analysis_service import AnalysisService
from ..utils.logger import logger

router = APIRouter()
analysis_service = AnalysisService()

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    text: str
    sentiment: str

@router.post("/", response_model=AnalysisResponse)
def analyze_text(request: AnalysisRequest):
    """
    对给定的文本进行情感分析。

    - **text**: 需要进行情感分析的文本。
    """
    logger.info(f"收到对文本的情感分析请求: '{request.text[:50]}...'")
    
    if not request.text:
        raise HTTPException(status_code=400, detail="文本内容不能为空。")
        
    try:
        sentiment = analysis_service.analyze_sentiment(request.text)
        logger.info(f"文本分析完成，情感: {sentiment}")
        
        return AnalysisResponse(
            text=request.text,
            sentiment=sentiment
        )
        
    except Exception as e:
        logger.error(f"处理情感分析请求时发生错误: {e}")
        raise HTTPException(status_code=500, detail="处理请求时发生内部错误。")