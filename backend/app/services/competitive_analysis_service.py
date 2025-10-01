from typing import List, Dict, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ..services.analysis_service import AnalysisService
from ..services.large_dataset_service import LargeDatasetService
from ..data.models.advanced_analytics import CompetitiveAnalysis
from ..data.models.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger("trend-analyzer")

class CompetitiveAnalysisService:
    """竞品对比分析服务"""
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.dataset_service = LargeDatasetService()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        logger.info("CompetitiveAnalysisService 已初始化")
    
    def compare_brands(self, brand_keywords: List[List[str]], user_id: int) -> dict:
        """
        多品牌对比分析
        
        Args:
            brand_keywords: 品牌关键词列表，如 [["Apple", "iPhone"], ["Samsung", "Galaxy"]]
            user_id: 用户ID
            
        Returns:
            dict: 对比分析结果
        """
        logger.info(f"开始多品牌对比分析: {brand_keywords}")
        
        try:
            # 并行分析每个品牌
            brand_analyses = []
            with ThreadPoolExecutor(max_workers=len(brand_keywords)) as executor:
                futures = {
                    executor.submit(self.analysis_service.analyze, keywords): keywords 
                    for keywords in brand_keywords
                }
                
                for future in futures:
                    keywords = futures[future]
                    try:
                        result = future.result(timeout=30)
                        brand_analyses.append({
                            'brand_keywords': keywords,
                            'analysis': result
                        })
                    except Exception as e:
                        logger.error(f"品牌 {keywords} 分析失败: {e}")
                        brand_analyses.append({
                            'brand_keywords': keywords,
                            'analysis': None,
                            'error': str(e)
                        })
            
            # 生成对比报告
            comparison_result = self._generate_comparison_report(brand_analyses)
            
            # 保存到数据库
            self._save_competitive_analysis(user_id, brand_keywords, comparison_result)
            
            logger.info("多品牌对比分析完成")
            return comparison_result
            
        except Exception as e:
            logger.error(f"多品牌对比分析失败: {e}")
            return {
                'error': str(e),
                'brands': brand_keywords,
                'status': 'failed'
            }
    
    def _generate_comparison_report(self, brand_analyses: List[dict]) -> dict:
        """生成对比报告"""
        valid_analyses = [ba for ba in brand_analyses if ba.get('analysis')]
        
        if not valid_analyses:
            return {
                'error': '所有品牌分析都失败了',
                'comparison': None
            }
        
        # 提取关键指标进行对比
        comparison_metrics = {
            'hype_scores': {},
            'sentiment_comparison': {},
            'theme_analysis': {},
            'market_positioning': {},
            'competitive_advantages': {},
            'recommendations': []
        }
        
        for brand_analysis in valid_analyses:
            brand_name = ' + '.join(brand_analysis['brand_keywords'])
            analysis = brand_analysis['analysis']
            
            # 热度对比
            hype_score = analysis.get('hypeIndex', {}).get('score', 0)
            comparison_metrics['hype_scores'][brand_name] = hype_score
            
            # 情感对比
            sentiment = analysis.get('sentimentSpectrum', {})
            comparison_metrics['sentiment_comparison'][brand_name] = sentiment
            
            # 主题分析
            themes = analysis.get('keyThemes', [])
            comparison_metrics['theme_analysis'][brand_name] = themes
        
        # 生成竞争优势分析
        comparison_metrics['competitive_advantages'] = self._analyze_competitive_advantages(valid_analyses)
        
        # 生成市场定位分析
        comparison_metrics['market_positioning'] = self._analyze_market_positioning(valid_analyses)
        
        # 生成建议
        comparison_metrics['recommendations'] = self._generate_competitive_recommendations(valid_analyses)
        
        return {
            'comparison_type': 'multi_brand',
            'brands_analyzed': len(valid_analyses),
            'analysis_timestamp': 'just_now',
            'metrics': comparison_metrics,
            'summary': self._generate_comparison_summary(comparison_metrics)
        }
    
    def _analyze_competitive_advantages(self, analyses: List[dict]) -> dict:
        """分析竞争优势"""
        advantages = {}
        
        for brand_analysis in analyses:
            brand_name = ' + '.join(brand_analysis['brand_keywords'])
            analysis = brand_analysis['analysis']
            
            # 基于热度和情感分析竞争优势
            hype_score = analysis.get('hypeIndex', {}).get('score', 0)
            sentiment = analysis.get('sentimentSpectrum', {})
            positive_ratio = sentiment.get('positive', 0)
            
            advantages[brand_name] = {
                'market_buzz': 'high' if hype_score > 70 else 'medium' if hype_score > 40 else 'low',
                'user_sentiment': 'positive' if positive_ratio > 50 else 'neutral' if positive_ratio > 30 else 'negative',
                'key_strengths': self._extract_strengths(analysis),
                'potential_weaknesses': self._extract_weaknesses(analysis)
            }
        
        return advantages
    
    def _analyze_market_positioning(self, analyses: List[dict]) -> dict:
        """分析市场定位"""
        positioning = {}
        
        # 计算相对位置
        hype_scores = []
        sentiment_scores = []
        
        for brand_analysis in analyses:
            analysis = brand_analysis['analysis']
            hype_scores.append(analysis.get('hypeIndex', {}).get('score', 0))
            sentiment = analysis.get('sentimentSpectrum', {})
            sentiment_scores.append(sentiment.get('positive', 0) - sentiment.get('negative', 0))
        
        avg_hype = sum(hype_scores) / len(hype_scores) if hype_scores else 0
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        for i, brand_analysis in enumerate(analyses):
            brand_name = ' + '.join(brand_analysis['brand_keywords'])
            
            positioning[brand_name] = {
                'market_position': self._determine_market_position(hype_scores[i], sentiment_scores[i], avg_hype, avg_sentiment),
                'differentiation_opportunities': self._identify_differentiation_opportunities(brand_analysis, analyses)
            }
        
        return positioning
    
    def _generate_competitive_recommendations(self, analyses: List[dict]) -> List[dict]:
        """生成竞争建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        for brand_analysis in analyses:
            brand_name = ' + '.join(brand_analysis['brand_keywords'])
            analysis = brand_analysis['analysis']
            
            # 基于情感分析生成建议
            sentiment = analysis.get('sentimentSpectrum', {})
            if sentiment.get('negative', 0) > 30:
                recommendations.append({
                    'type': 'reputation_management',
                    'brand': brand_name,
                    'priority': 'high',
                    'description': f'{brand_name} 需要关注负面情感，建议加强声誉管理和用户沟通'
                })
            
            # 基于热度分析生成建议
            hype_score = analysis.get('hypeIndex', {}).get('score', 0)
            if hype_score < 40:
                recommendations.append({
                    'type': 'marketing_boost',
                    'brand': brand_name,
                    'priority': 'medium',
                    'description': f'{brand_name} 市场热度较低，建议加强营销推广和品牌曝光'
                })
        
        return recommendations
    
    def _extract_strengths(self, analysis: dict) -> List[str]:
        """提取品牌优势"""
        strengths = []
        
        # 基于主题和情感提取优势
        themes = analysis.get('keyThemes', [])
        for theme in themes:
            if theme.get('isEmerging', False):
                strengths.append(f"在{theme.get('theme', '新兴领域')}方面具有创新优势")
        
        sentiment = analysis.get('sentimentSpectrum', {})
        if sentiment.get('positive', 0) > 60:
            strengths.append("用户满意度高，品牌形象良好")
        
        return strengths[:3]  # 返回前3个优势
    
    def _extract_weaknesses(self, analysis: dict) -> List[str]:
        """提取潜在弱点"""
        weaknesses = []
        
        sentiment = analysis.get('sentimentSpectrum', {})
        if sentiment.get('negative', 0) > 25:
            weaknesses.append("存在一定程度的负面反馈")
        
        if sentiment.get('questioning', 0) > 20:
            weaknesses.append("用户对产品存在疑虑，需要更好的教育和沟通")
        
        return weaknesses[:2]  # 返回前2个弱点
    
    def _determine_market_position(self, hype: float, sentiment: float, avg_hype: float, avg_sentiment: float) -> str:
        """确定市场位置"""
        if hype > avg_hype and sentiment > avg_sentiment:
            return "市场领导者"
        elif hype > avg_hype and sentiment <= avg_sentiment:
            return "高曝光挑战者"
        elif hype <= avg_hype and sentiment > avg_sentiment:
            return "口碑优势者"
        else:
            return "市场跟随者"
    
    def _identify_differentiation_opportunities(self, brand_analysis: dict, all_analyses: List[dict]) -> List[str]:
        """识别差异化机会"""
        opportunities = []
        
        # 分析其他品牌的弱点，找到差异化机会
        brand_themes = set()
        for theme in brand_analysis['analysis'].get('keyThemes', []):
            brand_themes.add(theme.get('theme', ''))
        
        # 找到其他品牌没有涉及的主题
        other_themes = set()
        for other_analysis in all_analyses:
            if other_analysis != brand_analysis:
                for theme in other_analysis['analysis'].get('keyThemes', []):
                    other_themes.add(theme.get('theme', ''))
        
        unique_themes = brand_themes - other_themes
        for theme in list(unique_themes)[:2]:
            opportunities.append(f"在{theme}领域具有独特优势，可进一步强化")
        
        return opportunities
    
    def _generate_comparison_summary(self, metrics: dict) -> str:
        """生成对比总结"""
        hype_scores = metrics.get('hype_scores', {})
        if not hype_scores:
            return "对比分析完成，但缺少有效数据"
        
        # 找到热度最高的品牌
        top_brand = max(hype_scores.items(), key=lambda x: x[1])
        
        summary = f"在本次对比分析中，{top_brand[0]} 以 {top_brand[1]} 分的热度指数领先。"
        
        # 添加情感分析总结
        sentiment_data = metrics.get('sentiment_comparison', {})
        if sentiment_data:
            positive_brands = []
            for brand, sentiment in sentiment_data.items():
                if sentiment.get('positive', 0) > 50:
                    positive_brands.append(brand)
            
            if positive_brands:
                summary += f" {', '.join(positive_brands)} 在用户情感方面表现积极。"
        
        return summary
    
    def _save_competitive_analysis(self, user_id: int, brands: List[List[str]], result: dict):
        """保存竞品分析结果到数据库"""
        try:
            db = next(get_db())
            analysis = CompetitiveAnalysis(
                user_id=user_id,
                brands=brands,
                analysis_result=result,
                status="completed"
            )
            db.add(analysis)
            db.commit()
            logger.info(f"竞品分析结果已保存，用户ID: {user_id}")
        except Exception as e:
            logger.error(f"保存竞品分析结果失败: {e}")
    
    def get_user_analyses(self, user_id: int, limit: int = 10) -> List[dict]:
        """获取用户的竞品分析历史"""
        try:
            db = next(get_db())
            analyses = db.query(CompetitiveAnalysis).filter(
                CompetitiveAnalysis.user_id == user_id
            ).order_by(CompetitiveAnalysis.created_at.desc()).limit(limit).all()
            
            return [{
                'id': analysis.id,
                'brands': analysis.brands,
                'status': analysis.status,
                'created_at': analysis.created_at.isoformat(),
                'result_summary': self._extract_summary(analysis.analysis_result)
            } for analysis in analyses]
            
        except Exception as e:
            logger.error(f"获取用户竞品分析历史失败: {e}")
            return []
    
    def _extract_summary(self, result: dict) -> str:
        """提取分析结果摘要"""
        if not result:
            return "分析失败"
        
        return result.get('summary', '竞品对比分析已完成')