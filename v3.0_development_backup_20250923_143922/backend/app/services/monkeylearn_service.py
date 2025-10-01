"""
MonkeyLearn API 服务
提供专业的文本分析和情感分析功能作为现有VADER/TextBlob的补充

注意：MonkeyLearn是付费服务（起步$299/月），但提供了高质量的预训练模型
- 情感分析模型
- 主题分类模型  
- 意图检测模型
- 关键词提取模型

使用说明：
1. 在MonkeyLearn注册账号并获取API Token
2. 在环境变量中设置 MONKEYLEARN_API_TOKEN
3. 如果未设置API Token，服务将优雅降级到本地分析
"""

import os
import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("trend-analyzer")

class MonkeyLearnService:
    """MonkeyLearn API服务"""
    
    def __init__(self):
        self.api_token = os.getenv("MONKEYLEARN_API_TOKEN")
        self.base_url = "https://api.monkeylearn.com/v3"
        self.available = bool(self.api_token)
        
        # 预训练模型ID（MonkeyLearn公开模型）
        self.models = {
            "sentiment": "cl_pi3C7JiL",  # 情感分析模型
            "emotion": "cl_Jx8qzYJh",   # 情绪检测模型
            "intent": "cl_3RnrF5nh",    # 意图分析模型
            "topics": "cl_5icAVzKR"     # 主题分类模型
        }
        
        if self.available:
            logger.info("MonkeyLearn API 已启用")
        else:
            logger.info("MonkeyLearn API 未配置，将使用本地分析")
    
    async def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        使用MonkeyLearn进行情感分析
        
        Args:
            texts: 文本列表（最多200个）
            
        Returns:
            情感分析结果列表
        """
        if not self.available:
            logger.warning("MonkeyLearn API未配置，跳过分析")
            return self._fallback_sentiment_analysis(texts)
        
        if not texts:
            return []
        
        # MonkeyLearn限制每次最多200个文本
        texts = texts[:200]
        
        try:
            url = f"{self.base_url}/classifiers/{self.models['sentiment']}/classify/"
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "data": texts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._process_sentiment_results(result, texts)
                    else:
                        logger.error(f"MonkeyLearn情感分析失败: HTTP {response.status}")
                        error_text = await response.text()
                        logger.error(f"错误详情: {error_text}")
                        return self._fallback_sentiment_analysis(texts)
        
        except Exception as e:
            logger.error(f"MonkeyLearn情感分析异常: {e}")
            return self._fallback_sentiment_analysis(texts)
    
    async def classify_topics(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        使用MonkeyLearn进行主题分类
        
        Args:
            texts: 文本列表
            
        Returns:
            主题分类结果列表
        """
        if not self.available:
            logger.warning("MonkeyLearn API未配置，跳过主题分类")
            return [{"text": text, "topics": [], "confidence": 0.0} for text in texts]
        
        if not texts:
            return []
        
        texts = texts[:200]  # 限制数量
        
        try:
            url = f"{self.base_url}/classifiers/{self.models['topics']}/classify/"
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "data": texts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._process_topic_results(result, texts)
                    else:
                        logger.error(f"MonkeyLearn主题分类失败: HTTP {response.status}")
                        return [{"text": text, "topics": [], "confidence": 0.0} for text in texts]
        
        except Exception as e:
            logger.error(f"MonkeyLearn主题分类异常: {e}")
            return [{"text": text, "topics": [], "confidence": 0.0} for text in texts]
    
    async def detect_intent(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        使用MonkeyLearn进行意图检测
        
        Args:
            texts: 文本列表
            
        Returns:
            意图检测结果列表
        """
        if not self.available:
            logger.warning("MonkeyLearn API未配置，跳过意图检测")
            return [{"text": text, "intent": "unknown", "confidence": 0.0} for text in texts]
        
        if not texts:
            return []
        
        texts = texts[:200]
        
        try:
            url = f"{self.base_url}/classifiers/{self.models['intent']}/classify/"
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "data": texts
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._process_intent_results(result, texts)
                    else:
                        logger.error(f"MonkeyLearn意图检测失败: HTTP {response.status}")
                        return [{"text": text, "intent": "unknown", "confidence": 0.0} for text in texts]
        
        except Exception as e:
            logger.error(f"MonkeyLearn意图检测异常: {e}")
            return [{"text": text, "intent": "unknown", "confidence": 0.0} for text in texts]
    
    async def comprehensive_analysis(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        综合分析（情感+主题+意图）
        
        Args:
            texts: 文本列表
            
        Returns:
            综合分析结果列表
        """
        if not texts:
            return []
        
        # 并行执行多种分析
        tasks = [
            self.analyze_sentiment(texts),
            self.classify_topics(texts),
            self.detect_intent(texts)
        ]
        
        try:
            sentiment_results, topic_results, intent_results = await asyncio.gather(*tasks)
            
            # 合并结果
            comprehensive_results = []
            for i, text in enumerate(texts):
                result = {
                    "text": text,
                    "monkeylearn_analysis": {
                        "sentiment": sentiment_results[i] if i < len(sentiment_results) else None,
                        "topics": topic_results[i] if i < len(topic_results) else None,
                        "intent": intent_results[i] if i < len(intent_results) else None,
                        "analyzed_at": datetime.now().isoformat(),
                        "api_available": self.available
                    }
                }
                comprehensive_results.append(result)
            
            logger.info(f"MonkeyLearn综合分析完成，处理了 {len(texts)} 个文本")
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"MonkeyLearn综合分析失败: {e}")
            return [{"text": text, "monkeylearn_analysis": None} for text in texts]
    
    def _process_sentiment_results(self, result: Dict, texts: List[str]) -> List[Dict[str, Any]]:
        """处理情感分析结果"""
        processed_results = []
        
        for i, classification in enumerate(result.get("classifications", [])):
            text = texts[i] if i < len(texts) else ""
            
            predictions = classification.get("predictions", [])
            if predictions:
                top_prediction = predictions[0]
                sentiment = top_prediction.get("tag_name", "neutral")
                confidence = top_prediction.get("confidence", 0.0)
            else:
                sentiment = "neutral"
                confidence = 0.0
            
            processed_results.append({
                "text": text,
                "sentiment": sentiment,
                "confidence": confidence,
                "predictions": predictions
            })
        
        return processed_results
    
    def _process_topic_results(self, result: Dict, texts: List[str]) -> List[Dict[str, Any]]:
        """处理主题分类结果"""
        processed_results = []
        
        for i, classification in enumerate(result.get("classifications", [])):
            text = texts[i] if i < len(texts) else ""
            
            predictions = classification.get("predictions", [])
            topics = []
            avg_confidence = 0.0
            
            if predictions:
                topics = [pred.get("tag_name", "") for pred in predictions]
                confidences = [pred.get("confidence", 0.0) for pred in predictions]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            processed_results.append({
                "text": text,
                "topics": topics,
                "confidence": avg_confidence,
                "predictions": predictions
            })
        
        return processed_results
    
    def _process_intent_results(self, result: Dict, texts: List[str]) -> List[Dict[str, Any]]:
        """处理意图检测结果"""
        processed_results = []
        
        for i, classification in enumerate(result.get("classifications", [])):
            text = texts[i] if i < len(texts) else ""
            
            predictions = classification.get("predictions", [])
            if predictions:
                top_prediction = predictions[0]
                intent = top_prediction.get("tag_name", "unknown")
                confidence = top_prediction.get("confidence", 0.0)
            else:
                intent = "unknown"
                confidence = 0.0
            
            processed_results.append({
                "text": text,
                "intent": intent,
                "confidence": confidence,
                "predictions": predictions
            })
        
        return processed_results
    
    def _fallback_sentiment_analysis(self, texts: List[str]) -> List[Dict[str, Any]]:
        """当MonkeyLearn不可用时的降级分析"""
        # 使用本地VADER进行简单分析
        from .enhanced_text_analysis_service import enhanced_text_analysis_service
        
        fallback_results = []
        for text in texts:
            try:
                local_result = enhanced_text_analysis_service.analyze_sentiment_comprehensive(text)
                fallback_results.append({
                    "text": text,
                    "sentiment": local_result.get("sentiment", "neutral"),
                    "confidence": local_result.get("confidence", 0.0),
                    "predictions": [],
                    "fallback": True
                })
            except Exception as e:
                logger.error(f"降级分析失败: {e}")
                fallback_results.append({
                    "text": text,
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "predictions": [],
                    "fallback": True
                })
        
        return fallback_results
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "available": self.available,
            "api_configured": bool(self.api_token),
            "models": self.models,
            "features": {
                "sentiment_analysis": True,
                "topic_classification": self.available,
                "intent_detection": self.available,
                "comprehensive_analysis": True
            },
            "note": "如果API未配置，将使用本地VADER/TextBlob作为降级方案"
        }

# 全局实例
monkeylearn_service = MonkeyLearnService()