from typing import List, Dict, Any, Optional
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import json
from ..services.large_dataset_service import LargeDatasetService
from ..data.models.advanced_analytics import TimeSeriesAnalysis
from ..data.models.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger("trend-analyzer")

class TimeSeriesAnalysisService:
    """时间序列分析服务"""
    
    def __init__(self):
        self.dataset_service = LargeDatasetService()
        logger.info("TimeSeriesAnalysisService 已初始化")
    
    def analyze_trend_evolution(self, keywords: List[str], time_range: str, user_id: int) -> dict:
        """分析趋势演变"""
        logger.info(f"开始时间序列分析: {keywords}, 时间范围: {time_range}")
        
        try:
            # 获取历史数据
            posts = self.dataset_service.search_posts(keywords, limit=1000)
            if not posts:
                return self._get_empty_timeseries_result(keywords, time_range)
            
            # 构建时间序列数据
            time_series_data = self._build_time_series(posts, time_range)
            
            # 趋势分解
            trend_analysis = self._decompose_trend(time_series_data)
            
            # 季节性检测
            seasonality_analysis = self._detect_seasonality(time_series_data)
            
            # 变化点检测
            change_points = self._detect_change_points(time_series_data)
            
            # 计算趋势评分
            trend_score = self._calculate_trend_score(trend_analysis)
            
            # 生成分析结果
            result = {
                "keywords": keywords,
                "time_range": time_range,
                "trend_analysis": trend_analysis,
                "seasonality": seasonality_analysis,
                "change_points": change_points,
                "trend_score": trend_score,
                "data_points": len(time_series_data),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "insights": self._generate_trend_insights(trend_analysis, seasonality_analysis, change_points)
            }
            
            # 保存到数据库
            self._save_timeseries_analysis(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"时间序列分析失败: {e}")
            return self._get_empty_timeseries_result(keywords, time_range, str(e))
    
    def predict_future_trends(self, keywords: List[str], forecast_days: int, user_id: int) -> dict:
        """趋势预测"""
        logger.info(f"开始趋势预测: {keywords}, 预测天数: {forecast_days}")
        
        try:
            # 获取历史数据
            posts = self.dataset_service.search_posts(keywords, limit=1000)
            if not posts:
                return self._get_empty_forecast_result(keywords, forecast_days)
            
            # 构建时间序列数据
            time_series_data = self._build_time_series(posts, "30d")
            
            # 简单线性趋势预测
            forecast_data = self._simple_trend_forecast(time_series_data, forecast_days)
            
            # 计算置信区间
            confidence_intervals = self._calculate_confidence_intervals(time_series_data, forecast_data)
            
            # 生成预测结果
            result = {
                "keywords": keywords,
                "forecast_days": forecast_days,
                "forecast_data": forecast_data,
                "confidence_intervals": confidence_intervals,
                "prediction_accuracy": self._estimate_accuracy(time_series_data),
                "forecast_insights": self._generate_forecast_insights(forecast_data),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"趋势预测失败: {e}")
            return self._get_empty_forecast_result(keywords, forecast_days, str(e))
    
    def _build_time_series(self, posts: List[Dict], time_range: str) -> List[Dict]:
        """构建时间序列数据"""
        # 解析时间范围
        days = self._parse_time_range(time_range)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计
        daily_stats = defaultdict(lambda: {
            'date': None,
            'post_count': 0,
            'engagement_sum': 0,
            'sentiment_positive': 0,
            'sentiment_negative': 0,
            'sentiment_neutral': 0
        })
        
        for post in posts:
            # 模拟时间分布
            post_date = self._simulate_post_date(start_date, end_date)
            date_key = post_date.strftime('%Y-%m-%d')
            
            daily_stats[date_key]['date'] = date_key
            daily_stats[date_key]['post_count'] += 1
            daily_stats[date_key]['engagement_sum'] += post.get('engagement_score', 0)
            
            sentiment = post.get('sentiment', 'neutral')
            if sentiment == 'positive':
                daily_stats[date_key]['sentiment_positive'] += 1
            elif sentiment == 'negative':
                daily_stats[date_key]['sentiment_negative'] += 1
            else:
                daily_stats[date_key]['sentiment_neutral'] += 1
        
        # 填充缺失日期
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'post_count': 0,
                    'engagement_sum': 0,
                    'sentiment_positive': 0,
                    'sentiment_negative': 0,
                    'sentiment_neutral': 0
                }
            current_date += timedelta(days=1)
        
        # 转换为列表并排序
        time_series = list(daily_stats.values())
        time_series.sort(key=lambda x: x['date'])
        
        return time_series
    
    def _decompose_trend(self, time_series_data: List[Dict]) -> Dict:
        """趋势分解"""
        if len(time_series_data) < 7:
            return {"trend": "insufficient_data", "direction": "unknown", "strength": 0}
        
        # 提取数值序列
        values = [item['post_count'] for item in time_series_data]
        
        # 简单移动平均趋势
        window_size = min(7, len(values) // 3)
        trend_values = []
        
        for i in range(len(values)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(values), i + window_size // 2 + 1)
            trend_values.append(sum(values[start_idx:end_idx]) / (end_idx - start_idx))
        
        # 计算趋势方向
        first_half = sum(trend_values[:len(trend_values)//2])
        second_half = sum(trend_values[len(trend_values)//2:])
        
        if second_half > first_half * 1.1:
            direction = "increasing"
        elif second_half < first_half * 0.9:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # 计算趋势强度
        if len(trend_values) > 1:
            trend_variance = np.var(trend_values)
            mean_value = np.mean(trend_values)
            strength = min(1.0, trend_variance / (mean_value + 1)) if mean_value > 0 else 0
        else:
            strength = 0
        
        return {
            "trend": direction,
            "direction": direction,
            "strength": round(strength, 3),
            "trend_values": trend_values,
            "raw_values": values
        }
    
    def _detect_seasonality(self, time_series_data: List[Dict]) -> Dict:
        """季节性检测"""
        if len(time_series_data) < 14:
            return {"detected": False, "period": None, "strength": 0}
        
        values = [item['post_count'] for item in time_series_data]
        
        # 检测周期性模式（简化版）
        # 检查7天周期（周模式）
        weekly_pattern = self._check_periodicity(values, 7)
        
        return {
            "detected": weekly_pattern['strength'] > 0.3,
            "period": 7 if weekly_pattern['strength'] > 0.3 else None,
            "strength": weekly_pattern['strength'],
            "pattern_type": "weekly" if weekly_pattern['strength'] > 0.3 else "none"
        }
    
    def _detect_change_points(self, time_series_data: List[Dict]) -> List[Dict]:
        """变化点检测"""
        if len(time_series_data) < 10:
            return []
        
        values = [item['post_count'] for item in time_series_data]
        change_points = []
        
        # 简单的变化点检测：寻找显著的均值变化
        window_size = max(3, len(values) // 10)
        
        for i in range(window_size, len(values) - window_size):
            before_mean = np.mean(values[i-window_size:i])
            after_mean = np.mean(values[i:i+window_size])
            
            # 检测显著变化（超过50%的变化）
            if before_mean > 0 and abs(after_mean - before_mean) / before_mean > 0.5:
                change_points.append({
                    "date": time_series_data[i]['date'],
                    "index": i,
                    "before_value": round(before_mean, 2),
                    "after_value": round(after_mean, 2),
                    "change_magnitude": round((after_mean - before_mean) / before_mean * 100, 1),
                    "change_type": "increase" if after_mean > before_mean else "decrease"
                })
        
        return change_points
    
    def _simple_trend_forecast(self, time_series_data: List[Dict], forecast_days: int) -> List[Dict]:
        """简单趋势预测"""
        if len(time_series_data) < 3:
            return []
        
        values = [item['post_count'] for item in time_series_data]
        
        # 简单线性回归预测
        x = np.arange(len(values))
        y = np.array(values)
        
        # 计算线性趋势
        slope, intercept = np.polyfit(x, y, 1)
        
        # 生成预测值
        forecast_data = []
        last_date = datetime.strptime(time_series_data[-1]['date'], '%Y-%m-%d')
        
        for i in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=i)
            predicted_value = max(0, slope * (len(values) + i - 1) + intercept)
            
            forecast_data.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "predicted_value": round(predicted_value, 2),
                "day_offset": i
            })
        
        return forecast_data
    
    def _calculate_confidence_intervals(self, time_series_data: List[Dict], forecast_data: List[Dict]) -> Dict:
        """计算置信区间"""
        if len(time_series_data) < 3:
            return {"lower_bound": [], "upper_bound": [], "confidence_level": 0.95}
        
        values = [item['post_count'] for item in time_series_data]
        std_dev = np.std(values)
        
        lower_bound = []
        upper_bound = []
        
        for forecast_point in forecast_data:
            predicted = forecast_point['predicted_value']
            margin = 1.96 * std_dev  # 95% 置信区间
            
            lower_bound.append(max(0, predicted - margin))
            upper_bound.append(predicted + margin)
        
        return {
            "lower_bound": [round(x, 2) for x in lower_bound],
            "upper_bound": [round(x, 2) for x in upper_bound],
            "confidence_level": 0.95
        }
    
    def _generate_trend_insights(self, trend_analysis: Dict, seasonality: Dict, change_points: List[Dict]) -> List[str]:
        """生成趋势洞察"""
        insights = []
        
        # 趋势洞察
        if trend_analysis['direction'] == 'increasing':
            insights.append(f"关键词热度呈上升趋势，趋势强度为 {trend_analysis['strength']:.1%}")
        elif trend_analysis['direction'] == 'decreasing':
            insights.append(f"关键词热度呈下降趋势，趋势强度为 {trend_analysis['strength']:.1%}")
        else:
            insights.append("关键词热度保持相对稳定")
        
        # 季节性洞察
        if seasonality['detected']:
            insights.append(f"检测到{seasonality['pattern_type']}周期性模式，强度为 {seasonality['strength']:.1%}")
        
        # 变化点洞察
        if change_points:
            recent_change = change_points[-1]
            insights.append(f"在 {recent_change['date']} 检测到显著变化点，热度{recent_change['change_type']} {abs(recent_change['change_magnitude']):.1f}%")
        
        return insights
    
    def _generate_forecast_insights(self, forecast_data: List[Dict]) -> List[str]:
        """生成预测洞察"""
        if not forecast_data:
            return ["预测数据不足"]
        
        insights = []
        
        # 预测趋势
        first_value = forecast_data[0]['predicted_value']
        last_value = forecast_data[-1]['predicted_value']
        
        if last_value > first_value * 1.1:
            insights.append("预测显示未来热度将持续上升")
        elif last_value < first_value * 0.9:
            insights.append("预测显示未来热度可能下降")
        else:
            insights.append("预测显示未来热度将保持稳定")
        
        # 预测值范围
        max_value = max(item['predicted_value'] for item in forecast_data)
        min_value = min(item['predicted_value'] for item in forecast_data)
        insights.append(f"预测期间热度范围：{min_value:.1f} - {max_value:.1f}")
        
        return insights
    
    def _save_timeseries_analysis(self, user_id: int, result: Dict):
        """保存时间序列分析结果到数据库"""
        try:
            db = next(get_db())
            
            analysis = TimeSeriesAnalysis(
                user_id=user_id,
                keywords=result['keywords'],
                time_range=result['time_range'],
                forecast_data=result.get('trend_analysis', {}),
                trend_score=result.get('trend_score', 0),
                seasonality_detected=result.get('seasonality', {}).get('detected', False),
                status="completed"
            )
            
            db.add(analysis)
            db.commit()
            logger.info(f"时间序列分析结果已保存到数据库")
            
        except Exception as e:
            logger.error(f"保存时间序列分析结果失败: {e}")
    
    def get_user_timeseries_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取用户时间序列分析历史"""
        try:
            db = next(get_db())
            
            analyses = db.query(TimeSeriesAnalysis).filter(
                TimeSeriesAnalysis.user_id == user_id
            ).order_by(TimeSeriesAnalysis.created_at.desc()).limit(limit).all()
            
            return [{
                "id": analysis.id,
                "keywords": analysis.keywords,
                "time_range": analysis.time_range,
                "trend_score": analysis.trend_score,
                "seasonality_detected": analysis.seasonality_detected,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat()
            } for analysis in analyses]
            
        except Exception as e:
            logger.error(f"获取时间序列分析历史失败: {e}")
            return []
    
    # 辅助方法
    def _parse_time_range(self, time_range: str) -> int:
        """解析时间范围字符串"""
        if time_range == "7d":
            return 7
        elif time_range == "30d":
            return 30
        elif time_range == "90d":
            return 90
        elif time_range == "1y":
            return 365
        else:
            return 30  # 默认30天
    
    def _simulate_post_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """模拟帖子发布日期"""
        time_diff = end_date - start_date
        random_days = np.random.randint(0, time_diff.days + 1)
        return start_date + timedelta(days=random_days)
    
    def _check_periodicity(self, values: List[float], period: int) -> Dict:
        """检查周期性"""
        if len(values) < period * 2:
            return {"strength": 0}
        
        # 简单的周期性检测
        correlations = []
        for offset in range(1, min(len(values) // period, 4)):
            correlation = np.corrcoef(
                values[:-offset*period], 
                values[offset*period:]
            )[0, 1]
            if not np.isnan(correlation):
                correlations.append(abs(correlation))
        
        strength = np.mean(correlations) if correlations else 0
        return {"strength": strength}
    
    def _calculate_trend_score(self, trend_analysis: Dict) -> float:
        """计算趋势评分"""
        direction_score = {
            "increasing": 0.8,
            "decreasing": 0.3,
            "stable": 0.5
        }.get(trend_analysis.get('direction', 'stable'), 0.5)
        
        strength = trend_analysis.get('strength', 0)
        return round(direction_score * (1 + strength), 2)
    
    def _estimate_accuracy(self, time_series_data: List[Dict]) -> float:
        """估算预测准确度"""
        if len(time_series_data) < 5:
            return 0.5
        
        values = [item['post_count'] for item in time_series_data]
        variance = np.var(values)
        mean_value = np.mean(values)
        
        # 基于数据稳定性估算准确度
        if mean_value > 0:
            stability = 1 / (1 + variance / mean_value)
            return min(0.95, max(0.3, stability))
        else:
            return 0.5
    
    def _get_empty_timeseries_result(self, keywords: List[str], time_range: str, error: str = None) -> Dict:
        """获取空的时间序列分析结果"""
        return {
            "keywords": keywords,
            "time_range": time_range,
            "trend_analysis": {"trend": "no_data", "direction": "unknown", "strength": 0},
            "seasonality": {"detected": False, "period": None, "strength": 0},
            "change_points": [],
            "trend_score": 0,
            "data_points": 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "insights": ["数据不足，无法进行时间序列分析"],
            "error": error
        }
    
    def _get_empty_forecast_result(self, keywords: List[str], forecast_days: int, error: str = None) -> Dict:
        """获取空的预测结果"""
        return {
            "keywords": keywords,
            "forecast_days": forecast_days,
            "forecast_data": [],
            "confidence_intervals": {"lower_bound": [], "upper_bound": [], "confidence_level": 0.95},
            "prediction_accuracy": 0,
            "forecast_insights": ["数据不足，无法进行趋势预测"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "error": error
        }