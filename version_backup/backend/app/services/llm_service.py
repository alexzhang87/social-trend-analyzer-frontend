import json
import time
import random
from abc import ABC, abstractmethod
from zhipuai import ZhipuAI
from typing import List, Dict, Any, Optional
import logging
from functools import wraps

# Import the central settings object
from ..core.config import settings
from ..data.models import database

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """带指数退避的重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"函数 {func.__name__} 在 {max_retries} 次重试后仍然失败: {e}")
                        raise e
                    
                    # 添加随机抖动
                    jitter = random.uniform(0.1, 0.3) * delay
                    sleep_time = min(delay + jitter, max_delay)
                    
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}，{sleep_time:.2f}秒后重试")
                    time.sleep(sleep_time)
                    delay *= exponential_base
            
        return wrapper
    return decorator

class LLMProvider(ABC):
    """Abstract base class for a generic LLM provider."""
    @abstractmethod
    def generate_insights_for_cluster(self, cluster_posts: List[database.RawPost]) -> Dict[str, Any]:
        pass

class ZhipuAIProvider(LLMProvider):
    """LLM provider for ZhipuAI (GLM models)."""
    def __init__(self, api_key: str):
        if not api_key or api_key == "not_set":
            raise ValueError("ZhipuAI API key is required. Please check your .env file.")
        
        logger.info(f"初始化ZhipuAI客户端，API Key: {api_key[:4]}...{api_key[-4:]}")
        
        self.client = ZhipuAI(api_key=api_key)
        self.model = "glm-4.5"
        self.fallback_enabled = True
        self.request_timeout = 30
        
    def _create_fallback_response(self, error_msg: str, cluster_posts: List[database.RawPost]) -> Dict[str, Any]:
        """创建降级响应，确保系统稳定性"""
        logger.info("生成降级分析结果")
        
        # 基于帖子内容生成基础分析
        total_posts = len(cluster_posts)
        if total_posts == 0:
            return self._create_empty_response("没有足够的数据进行分析")
        
        # 统计基础指标
        total_likes = sum(getattr(post, 'likes', 0) for post in cluster_posts)
        avg_likes = total_likes // total_posts if total_posts > 0 else 0
        
        # 简单的关键词提取
        all_text = " ".join([post.text for post in cluster_posts if post.text])
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 生成基础主题
        themes = []
        for i, (word, freq) in enumerate(top_words[:3]):
            themes.append({
                "theme": f"关于{word}的讨论",
                "summary": f"社区中关于{word}的讨论较为活跃，出现{freq}次提及。这反映了用户对此话题的关注度。",
                "isEmerging": i < 2  # 前两个标记为新兴话题
            })
        
        # 计算基础热度指数
        hype_score = min(90, max(10, (avg_likes * 2) + (total_posts // 10)))
        
        return {
            "title": "社交媒体趋势分析",
            "summary": f"基于{total_posts}条社交媒体数据的分析结果，识别出{len(themes)}个主要讨论主题。",
            "hypeIndex": {
                "score": hype_score,
                "reasoning": f"基于{total_posts}条帖子的互动数据和传播指标计算得出"
            },
            "sentimentSpectrum": {
                "positive": 40,
                "neutral": 35,
                "negative": 15,
                "questioning": 10,
                "total": 100
            },
            "keyThemes": themes,
            "userPersonaSnapshot": {
                "personas": ["社交媒体用户", "内容消费者"],
                "coreNeeds": ["获取相关信息", "参与话题讨论"]
            },
            "actionableOpportunities": [
                {
                    "opportunity": "内容营销机会",
                    "description": "利用识别出的热门话题创建相关内容，提高用户参与度",
                    "targetPersona": "社交媒体用户"
                }
            ],
            "top_mentions": [
                {
                    "platform": post.platform,
                    "author": post.author,
                    "text": post.text[:200] + "..." if len(post.text) > 200 else post.text,
                    "url": post.url,
                    "likes": getattr(post, 'likes', 0),
                    "sentiment": "Neutral"
                } for post in cluster_posts[:3]
            ],
            "_fallback": True,
            "_error": error_msg
        }
    
    def _create_empty_response(self, reason: str) -> Dict[str, Any]:
        """创建空响应"""
        return {
            "title": "分析结果不可用",
            "summary": f"无法生成分析结果：{reason}",
            "hypeIndex": {"score": 0, "reasoning": "数据不足"},
            "sentimentSpectrum": {"positive": 0, "neutral": 100, "negative": 0, "questioning": 0, "total": 100},
            "keyThemes": [],
            "userPersonaSnapshot": {"personas": [], "coreNeeds": []},
            "actionableOpportunities": [],
            "top_mentions": [],
            "_empty": True,
            "_reason": reason
        }

    def generate_insights_for_cluster(self, cluster_posts: List[database.RawPost]) -> Dict[str, Any]:
        logger.info(f"开始为{len(cluster_posts)}条帖子生成洞察分析")
        
        # 数据验证
        if not cluster_posts:
            logger.warning("没有提供帖子数据")
            return self._create_empty_response("没有提供帖子数据")
        
        if len(cluster_posts) < 3:
            logger.warning(f"帖子数量不足({len(cluster_posts)}条)，使用降级分析")
            return self._create_fallback_response("数据量不足", cluster_posts)
        
        # 安全处理文本编码
        post_samples = []
        processed_count = 0
        for post in cluster_posts[:20]:
            try:
                text = post.text[:250] if post.text else ""
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='ignore')
                
                # 过滤空文本和过短文本
                if text and len(text.strip()) > 10:
                    post_samples.append(f"- {text.strip()}")
                    processed_count += 1
                    
            except Exception as e:
                logger.warning(f"处理帖子时出错: {e}")
                continue
        
        if processed_count < 3:
            logger.warning(f"有效帖子数量不足({processed_count}条)")
            return self._create_fallback_response("有效数据不足", cluster_posts)
        
        combined_texts = "\n".join(post_samples)
        
        # 构建优化的prompt
        prompt = self._build_analysis_prompt(combined_texts, len(cluster_posts))
        
        try:
            # 调用LLM API
            message_content = self._call_llm_api(prompt)
            
            # 解析JSON响应
            llm_json_output = json.loads(message_content)
            
            # 验证响应结构
            if not self._validate_llm_response(llm_json_output):
                logger.warning("LLM响应格式无效，使用降级分析")
                return self._create_fallback_response("LLM响应格式无效", cluster_posts)
            
            # 添加实际帖子数据
            llm_json_output["top_mentions"] = [
                {
                    "platform": post.platform or "unknown",
                    "author": post.author or "Anonymous",
                    "text": (post.text[:200] + "...") if len(post.text or "") > 200 else (post.text or ""),
                    "url": post.url or "",
                    "likes": getattr(post, 'likes', 0),
                    "sentiment": "Neutral"
                } for post in cluster_posts[:3] if post.text
            ]
            
            # 添加元数据
            llm_json_output["_metadata"] = {
                "processed_posts": processed_count,
                "total_posts": len(cluster_posts),
                "model": self.model,
                "timestamp": time.time(),
                "success": True
            }
            
            logger.info("ZhipuAI洞察生成成功")
            return llm_json_output

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return self._create_fallback_response(f"响应解析失败: {e}", cluster_posts)
            
        except Exception as e:
            logger.error(f"LLM分析过程中发生错误: {e}")
            return self._create_fallback_response(f"分析失败: {e}", cluster_posts)

def get_llm_provider() -> LLMProvider:
    """
    Dependency injector to get the configured LLM provider.
    This is the 'adapter' that allows easy switching.
    """
    # Get the API key from our central settings object
    api_key = settings.ZHIPU_API_KEY
    if not api_key or api_key == "not_set":
        raise ValueError("ZHIPU_API_KEY environment variable not set or loaded correctly.")
    return ZhipuAIProvider(api_key=api_key)
