"""
Google Data Studio (Looker Studio) 集成服务

通过Google Sheets作为数据桥梁，将趋势分析结果导出到Looker Studio进行可视化

集成方案：
1. 数据导出：Python → Google Sheets API → Google Sheets
2. 数据可视化：Google Sheets → Looker Studio → 专业仪表盘

优势：
- 完全免费
- 专业的可视化效果
- 实时数据更新
- 易于分享和协作
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

# Google APIs
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    gspread = None
    Credentials = None

logger = logging.getLogger("trend-analyzer")

class GoogleDataStudioService:
    """Google Data Studio集成服务"""
    
    def __init__(self):
        self.service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
        self.spreadsheet_id = os.getenv("LOOKER_STUDIO_SPREADSHEET_ID")
        self.available = GOOGLE_SHEETS_AVAILABLE and bool(self.service_account_path)
        
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self.gc = None
        self.worksheet_mapping = {
            "sentiment_analysis": "情感分析数据",
            "keyword_analysis": "关键词分析数据", 
            "platform_comparison": "平台对比数据",
            "trend_scores": "趋势评分数据",
            "time_series": "时间序列数据"
        }
        
        if self.available:
            self._initialize_client()
            logger.info("Google Data Studio服务已启用")
        else:
            logger.info("Google Data Studio服务未配置")
    
    def _initialize_client(self):
        """初始化Google Sheets客户端"""
        try:
            if os.path.exists(self.service_account_path):
                credentials = Credentials.from_service_account_file(
                    self.service_account_path, scopes=self.scopes
                )
                self.gc = gspread.authorize(credentials)
                logger.info("Google Sheets客户端初始化成功")
            else:
                logger.warning(f"Google服务账号文件不存在: {self.service_account_path}")
                self.available = False
        except Exception as e:
            logger.error(f"Google Sheets客户端初始化失败: {e}")
            self.available = False
    
    async def export_analysis_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将分析结果导出到Google Sheets
        
        Args:
            analysis_result: 综合分析结果
            
        Returns:
            导出结果信息
        """
        if not self.available:
            return {
                "success": False,
                "error": "Google Sheets服务不可用",
                "note": "请配置Google服务账号和Spreadsheet ID"
            }
        
        try:
            # 获取或创建工作表
            spreadsheet = await self._get_or_create_spreadsheet()
            
            export_results = {}
            
            # 导出情感分析数据
            sentiment_data = self._prepare_sentiment_data(analysis_result)
            if sentiment_data:
                export_results["sentiment"] = await self._export_to_worksheet(
                    spreadsheet, "sentiment_analysis", sentiment_data
                )
            
            # 导出关键词数据
            keyword_data = self._prepare_keyword_data(analysis_result)
            if keyword_data:
                export_results["keywords"] = await self._export_to_worksheet(
                    spreadsheet, "keyword_analysis", keyword_data
                )
            
            # 导出平台对比数据
            platform_data = self._prepare_platform_data(analysis_result)
            if platform_data:
                export_results["platforms"] = await self._export_to_worksheet(
                    spreadsheet, "platform_comparison", platform_data
                )
            
            # 导出趋势评分数据
            trend_data = self._prepare_trend_data(analysis_result)
            if trend_data:
                export_results["trends"] = await self._export_to_worksheet(
                    spreadsheet, "trend_scores", trend_data
                )
            
            return {
                "success": True,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
                "looker_studio_template": self._generate_looker_studio_template_url(),
                "export_results": export_results,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_or_create_spreadsheet(self):
        """获取或创建Google Sheets工作表"""
        try:
            if self.spreadsheet_id:
                # 尝试打开现有工作表
                spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
                logger.info(f"使用现有工作表: {spreadsheet.title}")
                return spreadsheet
            else:
                # 创建新工作表
                spreadsheet = self.gc.create("趋势分析数据 - Looker Studio")
                logger.info(f"创建新工作表: {spreadsheet.title}")
                
                # 分享给所有人（仅查看）
                spreadsheet.share('', perm_type='anyone', role='reader')
                
                return spreadsheet
                
        except Exception as e:
            logger.error(f"工作表操作失败: {e}")
            raise
    
    async def _export_to_worksheet(self, spreadsheet, worksheet_type: str, data: List[List]) -> Dict[str, Any]:
        """导出数据到指定工作表"""
        try:
            worksheet_name = self.worksheet_mapping.get(worksheet_type, worksheet_type)
            
            # 获取或创建工作表
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                # 清空现有数据
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            
            # 写入数据
            if data:
                worksheet.update('A1', data)
                
                # 设置表头格式
                if len(data) > 0:
                    worksheet.format('A1:Z1', {
                        "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 1.0},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                    })
            
            return {
                "worksheet_name": worksheet_name,
                "rows_exported": len(data),
                "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit#gid={worksheet.id}"
            }
            
        except Exception as e:
            logger.error(f"工作表 {worksheet_type} 导出失败: {e}")
            return {"error": str(e)}
    
    def _prepare_sentiment_data(self, analysis_result: Dict[str, Any]) -> List[List]:
        """准备情感分析数据"""
        try:
            sentiment_analysis = analysis_result.get("sentiment_analysis", {})
            platform_breakdown = sentiment_analysis.get("platform_breakdown", {})
            
            data = [
                ["平台", "正面情感", "负面情感", "中性情感", "总分析数", "平均置信度", "主导情感"]
            ]
            
            for platform, stats in platform_breakdown.items():
                sentiment_dist = stats.get("sentiment_distribution", {})
                row = [
                    platform,
                    sentiment_dist.get("positive", 0),
                    sentiment_dist.get("negative", 0), 
                    sentiment_dist.get("neutral", 0),
                    stats.get("total_analyzed", 0),
                    stats.get("average_confidence", 0),
                    stats.get("dominant_sentiment", "neutral")
                ]
                data.append(row)
            
            # 添加总体统计
            overall_dist = sentiment_analysis.get("sentiment_distribution", {})
            data.append([
                "总体",
                overall_dist.get("positive", 0),
                overall_dist.get("negative", 0),
                overall_dist.get("neutral", 0),
                sentiment_analysis.get("total_analyzed", 0),
                sentiment_analysis.get("overall_confidence", 0),
                sentiment_analysis.get("overall_sentiment", "neutral")
            ])
            
            return data
            
        except Exception as e:
            logger.error(f"情感数据准备失败: {e}")
            return []
    
    def _prepare_keyword_data(self, analysis_result: Dict[str, Any]) -> List[List]:
        """准备关键词数据"""
        try:
            keyword_analysis = analysis_result.get("keyword_analysis", {})
            top_keywords = keyword_analysis.get("top_keywords", [])
            
            data = [
                ["关键词", "频率", "出现平台", "平台数量"]
            ]
            
            for keyword_info in top_keywords[:50]:  # 限制前50个
                platforms = keyword_info.get("platforms", [])
                row = [
                    keyword_info.get("word", ""),
                    keyword_info.get("frequency", 0),
                    ", ".join(platforms),
                    len(platforms)
                ]
                data.append(row)
            
            return data
            
        except Exception as e:
            logger.error(f"关键词数据准备失败: {e}")
            return []
    
    def _prepare_platform_data(self, analysis_result: Dict[str, Any]) -> List[List]:
        """准备平台对比数据"""
        try:
            platform_comparison = analysis_result.get("platform_comparison", {})
            platform_stats = analysis_result.get("platform_stats", {})
            
            data = [
                ["平台", "帖子数量", "平均分数", "最高分数", "平均参与度", "总参与度", "数据点数"]
            ]
            
            for platform, stats in platform_comparison.items():
                platform_stat = platform_stats.get(platform, {})
                
                row = [
                    platform,
                    stats.get("posts_count", platform_stat.get("posts_count", 0)),
                    stats.get("average_score", 0),
                    stats.get("max_score", 0),
                    stats.get("average_engagement", 0),
                    stats.get("total_engagement", 0),
                    platform_stat.get("data_points", 0)
                ]
                data.append(row)
            
            return data
            
        except Exception as e:
            logger.error(f"平台数据准备失败: {e}")
            return []
    
    def _prepare_trend_data(self, analysis_result: Dict[str, Any]) -> List[List]:
        """准备趋势数据"""
        try:
            data = [
                ["指标", "值", "分析时间", "关键词"]
            ]
            
            # 趋势评分
            trend_score = analysis_result.get("trend_score", 0)
            keywords = ", ".join(analysis_result.get("keywords", []))
            analyzed_at = analysis_result.get("analyzed_at", datetime.now().isoformat())
            
            data.append(["趋势评分", trend_score, analyzed_at, keywords])
            data.append(["总分析内容数", analysis_result.get("total_posts_analyzed", 0), analyzed_at, keywords])
            data.append(["处理时间(秒)", analysis_result.get("processing_time", 0), analyzed_at, keywords])
            
            # 洞察
            insights = analysis_result.get("insights", [])
            for i, insight in enumerate(insights):
                data.append([f"洞察{i+1}", insight, analyzed_at, keywords])
            
            return data
            
        except Exception as e:
            logger.error(f"趋势数据准备失败: {e}")
            return []
    
    def _generate_looker_studio_template_url(self) -> str:
        """生成Looker Studio模板URL"""
        if self.spreadsheet_id:
            # 这是一个示例URL，实际使用时需要预先创建Looker Studio模板
            return f"https://lookerstudio.google.com/u/0/reporting/create?c.reportId=trend-analysis-template&ds.ds0.connector=GOOGLE_SHEETS&ds.ds0.datasourceId={self.spreadsheet_id}"
        else:
            return "https://lookerstudio.google.com/u/0/navigation/reporting"
    
    async def create_looker_studio_template(self) -> Dict[str, Any]:
        """
        创建Looker Studio仪表盘模板
        
        Returns:
            模板信息和使用指南
        """
        return {
            "template_name": "社交媒体趋势分析仪表盘",
            "description": "基于Twitter、Reddit、Product Hunt、Google Trends的综合趋势分析",
            "suggested_charts": [
                {
                    "type": "scorecard",
                    "title": "趋势评分",
                    "data_source": "trend_scores",
                    "metric": "趋势评分"
                },
                {
                    "type": "pie_chart", 
                    "title": "整体情感分布",
                    "data_source": "sentiment_analysis",
                    "dimension": "情感类型",
                    "metric": "数量"
                },
                {
                    "type": "bar_chart",
                    "title": "平台对比",
                    "data_source": "platform_comparison", 
                    "dimension": "平台",
                    "metric": "帖子数量"
                },
                {
                    "type": "word_cloud",
                    "title": "热门关键词",
                    "data_source": "keyword_analysis",
                    "dimension": "关键词",
                    "metric": "频率"
                },
                {
                    "type": "table",
                    "title": "平台详细数据",
                    "data_source": "platform_comparison",
                    "columns": ["平台", "帖子数量", "平均分数", "平均参与度"]
                }
            ],
            "setup_instructions": [
                "1. 确保Google Sheets数据源已正确连接",
                "2. 在Looker Studio中添加数据源（Google Sheets）",
                "3. 创建以上建议的图表类型",
                "4. 设置自动刷新（建议每小时或每天）",
                "5. 配置分享权限和访问控制"
            ],
            "looker_studio_url": "https://lookerstudio.google.com/"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "available": self.available,
            "google_sheets_library": GOOGLE_SHEETS_AVAILABLE,
            "service_account_configured": bool(self.service_account_path),
            "spreadsheet_id_configured": bool(self.spreadsheet_id),
            "features": {
                "data_export": self.available,
                "real_time_update": self.available,
                "template_creation": True,
                "visualization_templates": True
            },
            "setup_required": [
                "安装gspread库: pip install gspread google-auth",
                "配置Google服务账号JSON文件",
                "设置环境变量GOOGLE_SERVICE_ACCOUNT_PATH",
                "可选：设置LOOKER_STUDIO_SPREADSHEET_ID"
            ] if not self.available else [],
            "cost": "完全免费",
            "documentation": "https://developers.google.com/sheets/api"
        }

# 全局实例
google_data_studio_service = GoogleDataStudioService()