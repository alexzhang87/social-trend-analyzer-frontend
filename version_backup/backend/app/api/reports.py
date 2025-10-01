from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from typing import List
import tempfile
import os
from ..services.report_service import ReportService
from ..utils.logger import logger

router = APIRouter()
report_service = ReportService()

@router.post("/generate-pdf-report")
async def generate_pdf_report(
    analysis_data: dict,
    keywords: List[str]
):
    """生成专业级PDF报告"""
    try:
        logger.info(f"开始生成PDF报告，关键词: {keywords}")
        
        # 生成PDF报告
        pdf_data = report_service.generate_professional_report(analysis_data, keywords)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_data)
            tmp_file_path = tmp_file.name
        
        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"social_media_analysis_report_{timestamp}.pdf"
        
        logger.info(f"PDF报告生成成功: {filename}")
        
        # 返回文件响应
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            background=lambda: os.unlink(tmp_file_path)  # 下载后删除临时文件
        )
        
    except Exception as e:
        logger.error(f"生成PDF报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")

@router.get("/sample-report")
async def get_sample_report():
    """生成示例报告用于测试"""
    try:
        # 使用模拟数据生成示例报告
        sample_data = {
            "summary": "基于1000条社交媒体数据的综合分析，显示该话题具有较高的用户关注度和积极的市场反响。",
            "hypeIndex": {
                "score": 78,
                "reasoning": "基于高互动率、广泛传播和积极情感分析得出的综合热度评分"
            },
            "sentimentSpectrum": {
                "positive": 65,
                "neutral": 25,
                "negative": 8,
                "questioning": 2
            },
            "keyThemes": [
                {
                    "theme": "产品创新",
                    "summary": "用户对新产品功能和技术创新表现出强烈兴趣",
                    "isEmerging": True
                },
                {
                    "theme": "用户体验",
                    "summary": "关于产品易用性和用户界面的讨论较为活跃",
                    "isEmerging": False
                },
                {
                    "theme": "市场竞争",
                    "summary": "与竞争对手的比较和市场定位分析",
                    "isEmerging": True
                }
            ],
            "userPersonaSnapshot": {
                "personas": [
                    "科技爱好者 (35%)",
                    "早期采用者 (28%)",
                    "行业专家 (22%)",
                    "普通消费者 (15%)"
                ],
                "coreNeeds": [
                    "获取最新技术信息",
                    "了解产品性能对比",
                    "寻找解决方案",
                    "参与社区讨论"
                ]
            },
            "actionableOpportunities": [
                {
                    "opportunity": "Content Marketing Opportunity",
                    "description": "Leverage users' interest in technological innovation to create in-depth technical analysis content",
                     "targetPersona": "Tech Enthusiasts"
                },
                {
                    "opportunity": "Community Building",
                    "description": "Build a professional user community to promote experience sharing among users",
                     "targetPersona": "Industry Experts"
                },
                {
                    "opportunity": "Product Optimization",
                    "description": "Optimize product experience based on user feedback, especially interface design",
                     "targetPersona": "General Consumers"
                }
            ],
            "top_mentions": [
                {
                    "platform": "twitter",
                    "author": "tech_guru_2024",
                    "text": "这个新功能真的很棒！完全改变了我的工作流程，效率提升了至少30%。强烈推荐给所有同行！",
                    "likes": 245,
                    "sentiment": "positive"
                },
                {
                    "platform": "reddit",
                    "author": "early_adopter",
                    "text": "刚试用了一周，整体感觉不错。界面设计很直观，但还有一些小bug需要修复。期待后续更新。",
                    "likes": 189,
                    "sentiment": "neutral"
                },
                {
                    "platform": "twitter",
                    "author": "industry_analyst",
                    "text": "从市场角度看，这个产品填补了一个重要空白。虽然竞争激烈，但差异化明显。看好长期发展。",
                    "likes": 156,
                    "sentiment": "positive"
                },
                {
                    "platform": "reddit",
                    "author": "power_user",
                    "text": "功能很强大，但学习曲线有点陡峭。希望能有更多的教程和文档支持。",
                    "likes": 134,
                    "sentiment": "neutral"
                },
                {
                    "platform": "twitter",
                    "author": "startup_founder",
                    "text": "正在考虑为我们团队采购这个工具。价格合理，功能符合需求。已经开始试用期了。",
                    "likes": 98,
                    "sentiment": "positive"
                }
            ],
            "stats": {
                "total_posts": 1000,
                "platform_distribution": {
                    "twitter": 500,
                    "reddit": 500
                }
            }
        }
        
        sample_keywords = ["AI工具", "生产力", "技术创新"]
        
        # 生成PDF报告
        pdf_data = report_service.generate_professional_report(sample_data, sample_keywords)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_data)
            tmp_file_path = tmp_file.name
        
        filename = "sample_social_media_analysis_report.pdf"
        
        logger.info("示例PDF报告生成成功")
        
        # 返回文件响应
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            background=lambda: os.unlink(tmp_file_path)
        )
        
    except Exception as e:
        logger.error(f"生成示例报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成示例报告失败: {str(e)}")