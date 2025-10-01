"""
Google Data Studio (Looker Studio) API 路由
提供数据可视化和仪表盘集成功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from ..services.google_data_studio_service import google_data_studio_service
from ..services.comprehensive_analysis_service import comprehensive_analysis_service
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class DataExportRequest(BaseModel):
    keywords: List[str] = Field(..., description="分析关键词")
    platforms: List[str] = Field(default=["twitter", "reddit", "product_hunt", "google_trends"], description="分析平台")
    time_filter: str = Field(default="week", description="时间过滤器")
    auto_refresh: bool = Field(default=False, description="是否启用自动刷新")

class LookerStudioResponse(BaseModel):
    success: bool
    spreadsheet_url: str = None
    looker_studio_template: str = None
    message: str

@router.get("/status")
async def get_data_studio_status() -> Dict[str, Any]:
    """获取Google Data Studio服务状态"""
    return google_data_studio_service.get_status()

@router.post("/export-analysis")
async def export_analysis_to_sheets(
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
) -> LookerStudioResponse:
    """
    将趋势分析结果导出到Google Sheets，用于Looker Studio可视化
    
    需要配置Google服务账号文件和相关环境变量
    """
    try:
        if not google_data_studio_service.available:
            raise HTTPException(
                status_code=503,
                detail="Google Data Studio服务不可用，请检查配置"
            )
        
        # 执行综合分析
        logger.info(f"开始为用户 {current_user.username} 执行趋势分析")
        analysis_result = await comprehensive_analysis_service.analyze_trends_comprehensive(
            keywords=request.keywords,
            platforms=request.platforms,
            time_filter=request.time_filter
        )
        
        # 导出到Google Sheets
        export_result = await google_data_studio_service.export_analysis_data(analysis_result)
        
        if export_result.get("success"):
            return LookerStudioResponse(
                success=True,
                spreadsheet_url=export_result.get("spreadsheet_url"),
                looker_studio_template=export_result.get("looker_studio_template"),
                message="数据已成功导出到Google Sheets，可以在Looker Studio中创建仪表盘"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"数据导出失败: {export_result.get('error', '未知错误')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据导出异常: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/template")
async def get_looker_studio_template() -> Dict[str, Any]:
    """获取Looker Studio仪表盘模板信息"""
    return await google_data_studio_service.create_looker_studio_template()

@router.post("/create-dashboard")
async def create_dashboard_guide(
    request: DataExportRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    创建Looker Studio仪表盘的指导信息
    """
    try:
        template_info = await google_data_studio_service.create_looker_studio_template()
        status = google_data_studio_service.get_status()
        
        return {
            "dashboard_name": f"趋势分析 - {', '.join(request.keywords)}",
            "template_info": template_info,
            "setup_guide": {
                "step1": {
                    "title": "数据准备",
                    "description": "首先使用 /export-analysis 端点将分析数据导出到Google Sheets"
                },
                "step2": {
                    "title": "连接数据源", 
                    "description": "在Looker Studio中添加Google Sheets作为数据源",
                    "url": "https://lookerstudio.google.com/"
                },
                "step3": {
                    "title": "创建图表",
                    "description": "根据模板建议创建各种可视化图表",
                    "suggested_charts": template_info["suggested_charts"]
                },
                "step4": {
                    "title": "设置自动刷新",
                    "description": "配置数据源自动刷新，保持仪表盘数据最新"
                },
                "step5": {
                    "title": "分享和协作",
                    "description": "设置仪表盘访问权限，与团队分享分析结果"
                }
            },
            "service_status": status,
            "estimated_setup_time": "15-30分钟",
            "cost": "完全免费"
        }
        
    except Exception as e:
        logger.error(f"创建仪表盘指导失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指导信息失败: {str(e)}")

@router.get("/examples")
async def get_dashboard_examples() -> Dict[str, Any]:
    """获取仪表盘示例和最佳实践"""
    return {
        "example_dashboards": [
            {
                "name": "社交媒体情感监控",
                "description": "实时监控品牌或产品在各社交平台的情感变化",
                "key_metrics": ["情感评分", "平台分布", "趋势变化"],
                "update_frequency": "每小时",
                "use_case": "品牌监控、危机管理"
            },
            {
                "name": "竞品分析仪表盘",
                "description": "对比分析竞争对手在不同平台的表现",
                "key_metrics": ["关键词对比", "参与度对比", "热门话题"],
                "update_frequency": "每日",
                "use_case": "市场研究、竞品分析"
            },
            {
                "name": "产品发布效果追踪",
                "description": "追踪新产品发布后的市场反应和讨论热度",
                "key_metrics": ["讨论热度", "情感变化", "关键反馈"],
                "update_frequency": "每4小时",
                "use_case": "产品管理、市场营销"
            }
        ],
        "best_practices": [
            "使用清晰的图表标题和说明",
            "设置合适的颜色主题（推荐使用品牌色）",
            "添加数据更新时间戳",
            "为关键指标设置警报阈值",
            "提供数据来源说明",
            "定期审查和优化仪表盘布局"
        ],
        "chart_recommendations": {
            "sentiment_analysis": {
                "primary": "饼图 - 情感分布",
                "secondary": "时间序列 - 情感趋势"
            },
            "platform_comparison": {
                "primary": "柱状图 - 平台对比",
                "secondary": "表格 - 详细数据"
            },
            "keyword_analysis": {
                "primary": "词云图 - 热门关键词",
                "secondary": "条形图 - 关键词频率"
            },
            "trend_tracking": {
                "primary": "记分卡 - 趋势评分",
                "secondary": "折线图 - 趋势变化"
            }
        }
    }

@router.get("/integration-guide")
async def get_integration_guide() -> Dict[str, Any]:
    """获取完整的集成指南"""
    return {
        "title": "Google Data Studio (Looker Studio) 集成指南",
        "overview": "通过Google Sheets作为数据桥梁，实现趋势分析数据的专业可视化",
        "prerequisites": [
            "Google账号（Gmail）",
            "Google Cloud项目（免费）",
            "服务账号密钥文件",
            "趋势分析系统访问权限"
        ],
        "setup_steps": [
            {
                "step": 1,
                "title": "创建Google Cloud项目",
                "description": "在Google Cloud Console创建新项目",
                "url": "https://console.cloud.google.com/",
                "estimated_time": "5分钟"
            },
            {
                "step": 2,
                "title": "启用Google Sheets API",
                "description": "在项目中启用Google Sheets和Drive API",
                "estimated_time": "2分钟"
            },
            {
                "step": 3,
                "title": "创建服务账号",
                "description": "创建服务账号并下载JSON密钥文件",
                "estimated_time": "3分钟"
            },
            {
                "step": 4,
                "title": "配置环境变量",
                "description": "设置GOOGLE_SERVICE_ACCOUNT_PATH环境变量",
                "estimated_time": "1分钟"
            },
            {
                "step": 5,
                "title": "导出数据",
                "description": "使用API导出趋势分析数据到Google Sheets",
                "estimated_time": "2分钟"
            },
            {
                "step": 6,
                "title": "创建Looker Studio仪表盘",
                "description": "连接Google Sheets数据源并创建可视化",
                "estimated_time": "15分钟"
            }
        ],
        "troubleshooting": [
            {
                "issue": "服务账号权限不足",
                "solution": "确保服务账号有Sheets和Drive编辑权限"
            },
            {
                "issue": "数据导出失败",
                "solution": "检查Google API配额和网络连接"
            },
            {
                "issue": "Looker Studio无法连接Sheets",
                "solution": "确保Sheets已设置为可被Looker Studio访问"
            }
        ],
        "costs": {
            "google_sheets_api": "免费（每天100个请求限额）",
            "looker_studio": "完全免费",
            "google_drive_storage": "15GB免费存储空间",
            "total": "完全免费的解决方案"
        }
    }