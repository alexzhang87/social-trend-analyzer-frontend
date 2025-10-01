from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
import re
from collections import Counter
from sqlalchemy.orm import Session
from ..data.models.database import SessionLocal
from ..data.models.advanced_analytics import SemanticAnalysis
from .llm_service import get_llm_provider
from .large_dataset_service import LargeDatasetService

logger = logging.getLogger("trend-analyzer")

class SemanticAnalysisService:
    """语义分析服务 - 主题提取、实体识别、内容质量分析"""
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.dataset_service = LargeDatasetService()
        logger.info("SemanticAnalysisService 已初始化")
    
    def analyze_semantic_content(self, keywords: List[str], user_id: int) -> Dict[str, Any]:
        """执行完整的语义分析"""
        logger.info(f"开始语义分析，关键词: {keywords}")
        
        try:
            # 获取相关帖子数据
            posts = self.dataset_service.search_posts(keywords, limit=500)
            
            if not posts:
                logger.warning("未找到相关帖子数据")
                return self._get_empty_semantic_result(keywords)
            
            # 执行各项语义分析
            topics_result = self.extract_topics(posts)
            entities_result = self.extract_entities(posts)
            quality_result = self.analyze_content_quality(posts)
            similarity_result = self.analyze_semantic_similarity(posts)
            
            # 综合分析结果
            analysis_result = {
                "keywords": keywords,
                "topics": topics_result,
                "entities": entities_result,
                "content_quality": quality_result,
                "semantic_similarity": similarity_result,
                "summary": self._generate_semantic_summary(topics_result, entities_result, quality_result),
                "analyzed_posts_count": len(posts),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # 保存分析结果到数据库
            self._save_semantic_analysis(user_id, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"语义分析失败: {e}")
            return self._get_empty_semantic_result(keywords)
    
    def extract_topics(self, posts: List[dict]) -> Dict[str, Any]:
        """主题提取和建模"""
        try:
            # 提取文本内容
            texts = [post.get('text', '') for post in posts if post.get('text')]
            
            if not texts:
                return {"topics": [], "topic_distribution": {}, "word_cloud_data": []}
            
            # 使用LLM进行主题聚类
            topics_prompt = f"""
请分析以下社交媒体内容，提取主要主题和关键词。

内容样本（前20条）:
{json.dumps(texts[:20], ensure_ascii=False, indent=2)}

请以JSON格式返回分析结果：
{{
  "main_topics": [
    {{
      "topic_name": "主题名称",
      "keywords": ["关键词1", "关键词2"],
      "description": "主题描述",
      "relevance_score": 0.85,
      "post_count": 15
    }}
  ],
  "topic_distribution": {{
    "主题1": 35.5,
    "主题2": 28.3
  }},
  "emerging_themes": ["新兴主题1", "新兴主题2"],
  "word_frequency": {{
    "词汇1": 45,
    "词汇2": 32
  }}
}}

只返回JSON格式的结果。
"""
            
            llm_result = self.llm_provider.generate_insights_for_cluster(posts[:50])
            
            # 解析LLM结果或使用备用方法
            if isinstance(llm_result, dict) and 'main_topics' in str(llm_result):
                return self._parse_topics_from_llm(llm_result)
            else:
                return self._extract_topics_fallback(texts)
                
        except Exception as e:
            logger.error(f"主题提取失败: {e}")
            return self._extract_topics_fallback(texts if 'texts' in locals() else [])
    
    def extract_entities(self, posts: List[dict]) -> Dict[str, Any]:
        """实体识别和分析"""
        try:
            texts = [post.get('text', '') for post in posts if post.get('text')]
            
            if not texts:
                return {"entities": [], "entity_types": {}, "entity_network": {}}
            
            # 使用简单的正则表达式进行实体识别
            entities = {
                "persons": self._extract_persons(texts),
                "organizations": self._extract_organizations(texts),
                "products": self._extract_products(texts),
                "locations": self._extract_locations(texts),
                "hashtags": self._extract_hashtags(texts),
                "mentions": self._extract_mentions(texts)
            }
            
            # 统计实体频率
            entity_frequency = {}
            for entity_type, entity_list in entities.items():
                entity_frequency[entity_type] = dict(Counter(entity_list).most_common(10))
            
            return {
                "entities": entities,
                "entity_frequency": entity_frequency,
                "entity_types": {k: len(v) for k, v in entities.items()},
                "total_entities": sum(len(v) for v in entities.values())
            }
            
        except Exception as e:
            logger.error(f"实体识别失败: {e}")
            return {"entities": [], "entity_types": {}, "entity_network": {}}
    
    def analyze_content_quality(self, posts: List[dict]) -> Dict[str, Any]:
        """内容质量分析"""
        try:
            if not posts:
                return {"overall_score": 0, "quality_metrics": {}, "recommendations": []}
            
            quality_metrics = {
                "average_length": self._calculate_average_length(posts),
                "engagement_rate": self._calculate_engagement_rate(posts),
                "sentiment_consistency": self._calculate_sentiment_consistency(posts),
                "information_density": self._calculate_information_density(posts),
                "originality_score": self._calculate_originality_score(posts)
            }
            
            # 计算综合质量评分
            overall_score = (
                quality_metrics["engagement_rate"] * 0.3 +
                quality_metrics["sentiment_consistency"] * 0.2 +
                quality_metrics["information_density"] * 0.3 +
                quality_metrics["originality_score"] * 0.2
            )
            
            # 生成改进建议
            recommendations = self._generate_quality_recommendations(quality_metrics)
            
            return {
                "overall_score": round(overall_score, 2),
                "quality_metrics": quality_metrics,
                "recommendations": recommendations,
                "quality_level": self._get_quality_level(overall_score)
            }
            
        except Exception as e:
            logger.error(f"内容质量分析失败: {e}")
            return {"overall_score": 0, "quality_metrics": {}, "recommendations": []}
    
    def analyze_semantic_similarity(self, posts: List[dict]) -> Dict[str, Any]:
        """语义相似度分析"""
        try:
            texts = [post.get('text', '') for post in posts[:100] if post.get('text')]
            
            if len(texts) < 2:
                return {"similarity_matrix": [], "clusters": [], "diversity_score": 0}
            
            # 简化的相似度计算（基于词汇重叠）
            similarity_data = self._calculate_text_similarity(texts)
            
            return {
                "similarity_matrix": similarity_data["matrix"],
                "clusters": similarity_data["clusters"],
                "diversity_score": similarity_data["diversity_score"],
                "content_uniqueness": similarity_data["uniqueness"]
            }
            
        except Exception as e:
            logger.error(f"语义相似度分析失败: {e}")
            return {"similarity_matrix": [], "clusters": [], "diversity_score": 0}
    
    def get_user_semantic_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户语义分析历史"""
        try:
            db = SessionLocal()
            analyses = db.query(SemanticAnalysis).filter(
                SemanticAnalysis.user_id == user_id
            ).order_by(SemanticAnalysis.created_at.desc()).limit(limit).all()
            
            return [{
                "id": analysis.id,
                "keywords": analysis.keywords,
                "content_quality_score": analysis.content_quality_score,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat(),
                "topics_count": len(analysis.topics_data.get("topics", [])) if analysis.topics_data else 0
            } for analysis in analyses]
            
        except Exception as e:
            logger.error(f"获取语义分析历史失败: {e}")
            return []
        finally:
            db.close()
    
    # 辅助方法
    def _get_empty_semantic_result(self, keywords: List[str]) -> Dict[str, Any]:
        """返回空的语义分析结果"""
        return {
            "keywords": keywords,
            "topics": {"topics": [], "topic_distribution": {}},
            "entities": {"entities": [], "entity_types": {}},
            "content_quality": {"overall_score": 0, "quality_metrics": {}},
            "semantic_similarity": {"similarity_matrix": [], "clusters": []},
            "summary": "未找到足够的数据进行语义分析",
            "analyzed_posts_count": 0,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _parse_topics_from_llm(self, llm_result: dict) -> Dict[str, Any]:
        """解析LLM返回的主题分析结果"""
        try:
            return {
                "topics": llm_result.get("main_topics", []),
                "topic_distribution": llm_result.get("topic_distribution", {}),
                "emerging_themes": llm_result.get("emerging_themes", []),
                "word_frequency": llm_result.get("word_frequency", {})
            }
        except Exception as e:
            logger.error(f"解析LLM主题结果失败: {e}")
            return {"topics": [], "topic_distribution": {}}
    
    def _extract_topics_fallback(self, texts: List[str]) -> Dict[str, Any]:
        """备用主题提取方法"""
        if not texts:
            return {"topics": [], "topic_distribution": {}}
        
        # 简单的关键词频率分析
        all_words = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            all_words.extend([w for w in words if len(w) > 3])
        
        word_freq = Counter(all_words).most_common(20)
        
        return {
            "topics": [{
                "topic_name": f"主题-{word}",
                "keywords": [word],
                "relevance_score": freq / len(all_words),
                "post_count": freq
            } for word, freq in word_freq[:5]],
            "topic_distribution": {word: freq for word, freq in word_freq[:10]},
            "word_frequency": dict(word_freq)
        }
    
    def _extract_persons(self, texts: List[str]) -> List[str]:
        """提取人名"""
        persons = []
        for text in texts:
            # 简单的人名识别（以@开头的用户名）
            mentions = re.findall(r'@(\w+)', text)
            persons.extend(mentions)
        return persons
    
    def _extract_organizations(self, texts: List[str]) -> List[str]:
        """提取组织机构名"""
        orgs = []
        common_orgs = ['Apple', 'Google', 'Microsoft', 'Tesla', 'Amazon', 'Meta', 'OpenAI']
        for text in texts:
            for org in common_orgs:
                if org.lower() in text.lower():
                    orgs.append(org)
        return orgs
    
    def _extract_products(self, texts: List[str]) -> List[str]:
        """提取产品名"""
        products = []
        common_products = ['iPhone', 'ChatGPT', 'Tesla', 'iPad', 'Android', 'Windows']
        for text in texts:
            for product in common_products:
                if product.lower() in text.lower():
                    products.append(product)
        return products
    
    def _extract_locations(self, texts: List[str]) -> List[str]:
        """提取地点"""
        locations = []
        common_locations = ['美国', '中国', '日本', '欧洲', '硅谷', '北京', '上海']
        for text in texts:
            for location in common_locations:
                if location in text:
                    locations.append(location)
        return locations
    
    def _extract_hashtags(self, texts: List[str]) -> List[str]:
        """提取话题标签"""
        hashtags = []
        for text in texts:
            tags = re.findall(r'#(\w+)', text)
            hashtags.extend(tags)
        return hashtags
    
    def _extract_mentions(self, texts: List[str]) -> List[str]:
        """提取用户提及"""
        mentions = []
        for text in texts:
            users = re.findall(r'@(\w+)', text)
            mentions.extend(users)
        return mentions
    
    def _calculate_average_length(self, posts: List[dict]) -> float:
        """计算平均内容长度"""
        lengths = [len(post.get('text', '')) for post in posts if post.get('text')]
        return sum(lengths) / len(lengths) if lengths else 0
    
    def _calculate_engagement_rate(self, posts: List[dict]) -> float:
        """计算参与度"""
        total_engagement = 0
        total_posts = len(posts)
        
        for post in posts:
            likes = post.get('likes', 0)
            retweets = post.get('retweets', 0)
            comments = post.get('comments', 0)
            total_engagement += likes + retweets + comments
        
        return (total_engagement / total_posts) / 100 if total_posts > 0 else 0
    
    def _calculate_sentiment_consistency(self, posts: List[dict]) -> float:
        """计算情感一致性"""
        sentiments = [post.get('sentiment', 'neutral') for post in posts]
        sentiment_counts = Counter(sentiments)
        max_sentiment_ratio = max(sentiment_counts.values()) / len(sentiments) if sentiments else 0
        return max_sentiment_ratio
    
    def _calculate_information_density(self, posts: List[dict]) -> float:
        """计算信息密度"""
        total_words = 0
        unique_words = set()
        
        for post in posts:
            text = post.get('text', '')
            words = re.findall(r'\b\w+\b', text.lower())
            total_words += len(words)
            unique_words.update(words)
        
        return len(unique_words) / total_words if total_words > 0 else 0
    
    def _calculate_originality_score(self, posts: List[dict]) -> float:
        """计算原创性评分"""
        texts = [post.get('text', '') for post in posts]
        unique_texts = set(texts)
        return len(unique_texts) / len(texts) if texts else 0
    
    def _generate_quality_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        
        if metrics.get("engagement_rate", 0) < 0.3:
            recommendations.append("提高内容互动性，增加问题和讨论话题")
        
        if metrics.get("information_density", 0) < 0.3:
            recommendations.append("增加内容的信息量和深度")
        
        if metrics.get("originality_score", 0) < 0.7:
            recommendations.append("提高内容原创性，避免重复发布")
        
        return recommendations
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.8:
            return "优秀"
        elif score >= 0.6:
            return "良好"
        elif score >= 0.4:
            return "一般"
        else:
            return "需要改进"
    
    def _calculate_text_similarity(self, texts: List[str]) -> Dict[str, Any]:
        """计算文本相似度"""
        # 简化的相似度计算
        similarity_matrix = []
        for i, text1 in enumerate(texts[:10]):  # 限制计算量
            row = []
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            for j, text2 in enumerate(texts[:10]):
                if i == j:
                    row.append(1.0)
                else:
                    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
                    intersection = len(words1 & words2)
                    union = len(words1 | words2)
                    similarity = intersection / union if union > 0 else 0
                    row.append(round(similarity, 3))
            similarity_matrix.append(row)
        
        # 计算多样性评分
        avg_similarity = sum(sum(row) for row in similarity_matrix) / (len(similarity_matrix) ** 2) if similarity_matrix else 0
        diversity_score = 1 - avg_similarity
        
        return {
            "matrix": similarity_matrix,
            "clusters": [],  # 简化实现
            "diversity_score": round(diversity_score, 3),
            "uniqueness": round(diversity_score * 100, 1)
        }
    
    def _generate_semantic_summary(self, topics: Dict, entities: Dict, quality: Dict) -> str:
        """生成语义分析摘要"""
        try:
            topic_count = len(topics.get("topics", []))
            entity_count = entities.get("total_entities", 0)
            quality_score = quality.get("overall_score", 0)
            
            return f"本次语义分析识别出{topic_count}个主要主题，{entity_count}个实体，内容质量评分为{quality_score}分。" + \
                   f"主要讨论话题包括：{', '.join([t.get('topic_name', '') for t in topics.get('topics', [])[:3]])}。"
        except Exception as e:
            logger.error(f"生成语义摘要失败: {e}")
            return "语义分析完成，详细结果请查看各项指标。"
    
    def _save_semantic_analysis(self, user_id: int, analysis_result: Dict[str, Any]):
        """保存语义分析结果到数据库"""
        try:
            db = SessionLocal()
            
            semantic_analysis = SemanticAnalysis(
                user_id=user_id,
                keywords=analysis_result["keywords"],
                topics_data=analysis_result["topics"],
                entities_data=analysis_result["entities"],
                content_quality_score=analysis_result["content_quality"].get("overall_score", 0),
                semantic_similarity=analysis_result["semantic_similarity"],
                status="completed"
            )
            
            db.add(semantic_analysis)
            db.commit()
            logger.info(f"语义分析结果已保存，用户ID: {user_id}")
            
        except Exception as e:
            logger.error(f"保存语义分析结果失败: {e}")
            db.rollback()
        finally:
            db.close()