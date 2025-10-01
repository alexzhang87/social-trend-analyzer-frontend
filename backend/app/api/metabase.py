"""
Metabase开源BI工具 API 路由
提供专业的商业智能和数据可视化解决方案
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from ..services.metabase_service import metabase_service
from ..services.comprehensive_analysis_service import comprehensive_analysis_service
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class MetabaseDeploymentRequest(BaseModel):
    target_directory: str = Field(default="./metabase-deployment", description="部署目录")
    custom_ports: Optional[Dict[str, int]] = Field(default=None, description="自定义端口配置")

class MetabaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.get("/status")
async def get_metabase_status() -> Dict[str, Any]:
    """获取Metabase服务状态和功能介绍"""
    return metabase_service.get_status()

@router.post("/create-deployment")
async def create_metabase_deployment(
    request: MetabaseDeploymentRequest,
    current_user = Depends(get_current_user)
) -> MetabaseResponse:
    """
    创建Metabase部署文件包
    
    生成完整的Docker Compose部署方案，包括：
    - docker-compose.yml配置文件
    - 环境变量配置
    - 启动和停止脚本
    - 完整的部署文档
    """
    try:
        logger.info(f"用户 {current_user.username} 请求创建Metabase部署")
        
        # 应用自定义端口配置
        if request.custom_ports:
            if "metabase" in request.custom_ports:
                metabase_service.metabase_port = str(request.custom_ports["metabase"])
            if "postgres" in request.custom_ports:
                metabase_service.postgres_port = str(request.custom_ports["postgres"])
            
            # 重新生成配置
            metabase_service.docker_compose_template = metabase_service._generate_docker_compose()
        
        # 创建部署文件
        deployment_result = await metabase_service.create_deployment_files(request.target_directory)
        
        if deployment_result.get("success"):
            return MetabaseResponse(
                success=True,
                message=f"Metabase部署文件创建成功",
                data={
                    "deployment_info": deployment_result,
                    "next_steps": [
                        "1. 进入部署目录",
                        "2. 运行 ./start.sh 或 docker-compose up -d",
                        "3. 等待服务启动（约1-2分钟）",
                        f"4. 访问 http://localhost:{metabase_service.metabase_port}",
                        "5. 完成Metabase初始设置",
                        "6. 连接数据源创建仪表盘"
                    ],
                    "estimated_setup_time": "10-15分钟",
                    "requirements": [
                        "Docker和Docker Compose已安装",
                        "端口可用（默认3001和5433）",
                        "至少2GB可用内存"
                    ]
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"部署文件创建失败: {deployment_result.get('error', '未知错误')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metabase部署创建失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")

@router.get("/dashboard-templates")
async def get_dashboard_templates() -> Dict[str, Any]:
    """获取预配置的仪表盘模板"""
    return metabase_service.get_dashboard_templates()

@router.get("/sample-data-script")
async def get_sample_data_script() -> Dict[str, Any]:
    """获取示例数据库脚本"""
    try:
        script = await metabase_service.generate_sample_data_script()
        
        return {
            "script": script,
            "description": "用于创建示例数据库表和数据的SQL脚本",
            "usage": [
                "1. 连接到PostgreSQL数据库",
                "2. 执行此SQL脚本创建表和示例数据", 
                "3. 在Metabase中连接到此数据库",
                "4. 根据模板创建仪表盘和图表"
            ],
            "tables_created": [
                "trend_analysis - 趋势分析主表",
                "sentiment_data - 情感数据表",
                "keyword_analysis - 关键词分析表",
                "platform_stats - 平台统计表"
            ]
        }
        
    except Exception as e:
        logger.error(f"生成示例数据脚本失败: {e}")
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")

@router.get("/integration-guide")
async def get_integration_guide() -> Dict[str, Any]:
    """获取完整的Metabase集成指南"""
    return {
        "title": "Metabase开源BI工具集成指南",
        "overview": "部署专业的开源商业智能工具，实现高级数据可视化和分析",
        "advantages": [
            "💰 完全免费开源，无license费用",
            "🚀 Docker一键部署，简单快速",
            "📊 40+种专业图表类型",
            "🔍 SQL查询编辑器和自助分析",
            "📱 响应式设计，支持移动端",
            "🔔 数据警报和通知功能",
            "👥 团队协作和权限管理",
            "🔗 REST API和嵌入式分析"
        ],
        "vs_competitors": {
            "vs_tableau": {
                "cost": "Metabase免费 vs Tableau $70/月",
                "deployment": "Docker自部署 vs 云端托管",
                "customization": "开源可定制 vs 商业封闭"
            },
            "vs_power_bi": {
                "cost": "Metabase免费 vs Power BI $10/月",
                "platform": "跨平台 vs 主要Windows",
                "data_sources": "广泛支持 vs 微软生态"
            },
            "vs_looker": {
                "cost": "Metabase免费 vs Looker $5000/月",
                "complexity": "简单易用 vs 企业复杂",
                "target": "中小企业 vs 大型企业"
            }
        },
        "deployment_options": [
            {
                "method": "Docker Compose（推荐）",
                "pros": ["一键部署", "包含数据库", "易于维护"],
                "cons": ["需要Docker基础知识"],
                "suitable_for": "开发和小型生产环境"
            },
            {
                "method": "云服务器部署",
                "pros": ["高可用", "扩展性好", "专业运维"],
                "cons": ["需要服务器费用", "运维复杂"],
                "suitable_for": "生产环境和团队使用"
            },
            {
                "method": "Kubernetes部署",
                "pros": ["自动扩展", "高可用", "容器编排"],
                "cons": ["复杂度高", "需要K8s知识"],
                "suitable_for": "大型企业和微服务架构"
            }
        ],
        "setup_timeline": {
            "preparation": "5分钟 - 检查Docker环境",
            "deployment": "3分钟 - 运行部署脚本",
            "initialization": "2分钟 - Metabase初始化",
            "configuration": "5分钟 - 连接数据源",
            "dashboard_creation": "10分钟 - 创建第一个仪表盘",
            "total": "25分钟完成完整部署和配置"
        },
        "best_practices": [
            "🔐 修改默认数据库密码",
            "📊 定期备份Metabase配置和数据",
            "⚡ 使用Redis缓存提升性能",
            "🔍 创建数据库索引优化查询",
            "👥 设置适当的用户权限",
            "📈 监控系统资源使用情况",
            "🔄 定期更新Metabase版本"
        ]
    }

@router.get("/comparison")
async def get_tool_comparison() -> Dict[str, Any]:
    """获取可视化工具对比"""
    return {
        "comparison_matrix": {
            "Google Data Studio": {
                "cost": "免费",
                "setup_time": "15分钟",
                "chart_types": "15+种",
                "customization": "中等",
                "data_sources": "Google生态",
                "collaboration": "优秀",
                "mobile": "良好",
                "api": "有限",
                "best_for": "快速原型、Google用户"
            },
            "Metabase": {
                "cost": "免费",
                "setup_time": "25分钟",
                "chart_types": "40+种",
                "customization": "高",
                "data_sources": "广泛支持",
                "collaboration": "优秀",
                "mobile": "优秀",
                "api": "完整",
                "best_for": "专业分析、企业使用"
            },
            "Tableau Public": {
                "cost": "免费（公开）",
                "setup_time": "60分钟",
                "chart_types": "50+种",
                "customization": "极高",
                "data_sources": "广泛支持",
                "collaboration": "中等",
                "mobile": "良好",
                "api": "商业版",
                "best_for": "专业分析师、公开数据"
            }
        },
        "selection_guide": {
            "choose_google_data_studio_if": [
                "你主要使用Google服务（Sheets、Analytics）",
                "需要快速创建简单的仪表盘",
                "团队已经在Google生态系统中",
                "预算极其有限",
                "不需要复杂的数据建模"
            ],
            "choose_metabase_if": [
                "需要专业的BI功能",
                "有多种数据源需要整合",
                "需要SQL查询和自助分析",
                "要求高度定制化",
                "计划长期使用和扩展",
                "需要完整的API支持"
            ],
            "choose_both_if": [
                "不同团队有不同需求",
                "想要低风险试验不同方案",
                "有充足的开发资源",
                "需要覆盖不同的使用场景"
            ]
        },
        "migration_path": [
            "阶段1: 使用Google Data Studio快速启动",
            "阶段2: 并行部署Metabase进行深度分析",
            "阶段3: 根据使用情况选择主要工具",
            "阶段4: 优化和扩展选定的解决方案"
        ]
    }

@router.post("/deploy-test")
async def deploy_test_environment(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
) -> MetabaseResponse:
    """
    部署测试环境（仅创建文件，不实际启动Docker）
    """
    try:
        logger.info(f"用户 {current_user.username} 请求部署Metabase测试环境")
        
        # 创建测试环境文件
        test_deployment = await metabase_service.create_deployment_files("./metabase-test")
        
        if test_deployment.get("success"):
            return MetabaseResponse(
                success=True,
                message="测试环境文件创建成功",
                data={
                    "deployment_path": test_deployment["deployment_path"],
                    "files_created": test_deployment["files_created"],
                    "test_instructions": [
                        "1. 检查生成的文件是否完整",
                        "2. 验证Docker Compose配置",
                        "3. 确认端口配置正确",
                        "4. 可选：运行 docker-compose config 验证",
                        "5. 准备就绪后运行 ./start.sh"
                    ],
                    "access_urls": {
                        "metabase": f"http://localhost:{metabase_service.metabase_port}",
                        "postgres": f"localhost:{metabase_service.postgres_port}"
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"测试环境创建失败: {test_deployment.get('error')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试环境部署失败: {e}")
        raise HTTPException(status_code=500, detail=f"部署失败: {str(e)}")