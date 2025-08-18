from ..utils.logger import logger

class AnalysisService:
    """
    一个简单的服务，用于对文本进行情感分析。
    """

    def __init__(self):
        # 定义简单的关键词列表用于情感判断
        self.positive_keywords = [
            "great", "excellent", "amazing", "love", "recommend", "future", 
            "gains", "powerful", "saved", "happy", "success", "awesome"
        ]
        self.negative_keywords = [
            "bad", "terrible", "disappointing", "hate", "avoid", "problem",
            "long way", "bugs", "end of", "can't handle", "failed", "error"
        ]
        logger.info("情感分析服务已初始化。")

    def analyze_sentiment(self, text: str) -> str:
        """
        对给定的文本进行情感分析。

        - **text**: 需要分析的文本。
        - **返回**: 'positive', 'negative', 或 'neutral'。
        """
        text_lower = text.lower()
        
        # 计算积极和消极词汇的得分
        positive_score = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_score = sum(1 for word in self.negative_keywords if word in text_lower)
        
        logger.debug(f"文本: '{text[:50]}...' | 积极得分: {positive_score}, 消极得分: {negative_score}")

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"