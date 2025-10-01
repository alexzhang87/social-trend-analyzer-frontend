import json
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from ..utils.logger import logger

class ReportService:
    """专业级PDF报告生成服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()
        logger.info("ReportService 已初始化")
    
    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册系统中文字体
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows系统字体路径
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                    "C:/Windows/Fonts/simsun.ttc",  # 宋体
                    "C:/Windows/Fonts/simhei.ttf",  # 黑体
                ]
            elif system == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc",
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]
            
            # 尝试注册第一个可用的字体
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.chinese_font = 'ChineseFont'
                        logger.info(f"成功注册中文字体: {font_path}")
                        return
                    except Exception as e:
                        logger.warning(f"注册字体失败 {font_path}: {e}")
                        continue
            
            # 如果没有找到中文字体，使用默认字体
            self.chinese_font = 'Helvetica'
            logger.warning("未找到中文字体，使用默认字体")
            
        except Exception as e:
            logger.error(f"字体注册过程出错: {e}")
            self.chinese_font = 'Helvetica'

    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1f2937'),
            alignment=TA_CENTER,
            fontName=self.chinese_font
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=HexColor('#374151'),
            leftIndent=0,
            fontName=self.chinese_font
        ))
        
        # 小标题样式
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#4b5563'),
            leftIndent=0,
            fontName=self.chinese_font
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#374151'),
            leftIndent=0,
            rightIndent=0,
            fontName=self.chinese_font
        ))
        
        # 重点文本样式
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#dc2626'),
            leftIndent=20,
            fontName=self.chinese_font
        ))

    def generate_professional_report(self, analysis_data: Dict[str, Any], keywords: List[str]) -> bytes:
        """生成专业级分析报告"""
        logger.info(f"开始生成专业级报告，关键词: {keywords}")
        
        # 创建内存缓冲区
        buffer = io.BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # 构建报告内容
        story = []
        
        # 1. 封面页
        story.extend(self._create_cover_page(keywords, analysis_data))
        story.append(PageBreak())
        
        # 2. 执行摘要
        story.extend(self._create_executive_summary(analysis_data))
        story.append(PageBreak())
        
        # 3. 数据概览
        story.extend(self._create_data_overview(analysis_data))
        story.append(Spacer(1, 20))
        
        # 4. 热度分析
        story.extend(self._create_hype_analysis(analysis_data))
        story.append(Spacer(1, 20))
        
        # 5. 情感分析
        story.extend(self._create_sentiment_analysis(analysis_data))
        story.append(PageBreak())
        
        # 6. 核心主题分析
        story.extend(self._create_themes_analysis(analysis_data))
        story.append(Spacer(1, 20))
        
        # 7. 用户画像分析
        story.extend(self._create_persona_analysis(analysis_data))
        story.append(PageBreak())
        
        # 8. 商业机会分析
        story.extend(self._create_opportunities_analysis(analysis_data))
        story.append(Spacer(1, 20))
        
        # 9. 热门内容分析
        story.extend(self._create_top_mentions_analysis(analysis_data))
        story.append(PageBreak())
        
        # 10. 结论与建议
        story.extend(self._create_conclusions(analysis_data, keywords))
        
        # 生成PDF
        doc.build(story)
        
        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()
        
        logger.info("专业级报告生成完成")
        return pdf_data

    def _create_cover_page(self, keywords: List[str], analysis_data: Dict[str, Any]) -> List:
        """创建封面页"""
        story = []
        
        # 主标题
        story.append(Spacer(1, 100))
        story.append(Paragraph("社交媒体趋势分析报告", self.styles['CustomTitle']))
        story.append(Spacer(1, 30))
        
        # 关键词
        keywords_text = f"关键词：{', '.join(keywords)}"
        story.append(Paragraph(keywords_text, self.styles['CustomHeading1']))
        story.append(Spacer(1, 50))
        
        # 报告信息
        report_info = [
            f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            f"数据来源：Twitter & Reddit",
            f"分析帖子数量：{analysis_data.get('stats', {}).get('total_posts', 'N/A')} 条",
            f"热度指数：{analysis_data.get('hypeIndex', {}).get('score', 'N/A')} 分"
        ]
        
        for info in report_info:
            story.append(Paragraph(info, self.styles['CustomBody']))
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 100))
        
        # 免责声明
        disclaimer = """
        <b>免责声明：</b><br/>
        本报告基于公开的社交媒体数据进行分析，仅供参考。
        分析结果不构成投资建议或商业决策依据。
        """
        story.append(Paragraph(disclaimer, self.styles['CustomBody']))
        
        return story

    def _create_executive_summary(self, analysis_data: Dict[str, Any]) -> List:
        """创建执行摘要"""
        story = []
        
        story.append(Paragraph("执行摘要", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        # 核心发现
        summary_text = analysis_data.get('summary', '基于社交媒体数据的综合分析结果。')
        story.append(Paragraph("<b>核心发现：</b>", self.styles['CustomHeading2']))
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # 关键指标
        hype_score = analysis_data.get('hypeIndex', {}).get('score', 0)
        sentiment = analysis_data.get('sentimentSpectrum', {})
        
        key_metrics = f"""
        <b>关键指标：</b><br/>
        • 热度指数：{hype_score}/100<br/>
        • 积极情感占比：{sentiment.get('positive', 0)}%<br/>
        • 中性情感占比：{sentiment.get('neutral', 0)}%<br/>
        • 消极情感占比：{sentiment.get('negative', 0)}%<br/>
        """
        
        story.append(Paragraph(key_metrics, self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # 主要建议
        opportunities = analysis_data.get('actionableOpportunities', [])
        if opportunities:
            story.append(Paragraph("<b>主要建议：</b>", self.styles['CustomHeading2']))
            for i, opp in enumerate(opportunities[:3], 1):
                opp_text = f"{i}. {opp.get('opportunity', '商业机会')}: {opp.get('description', '详细描述')}"
                story.append(Paragraph(opp_text, self.styles['CustomBody']))
                story.append(Spacer(1, 5))
        
        return story

    def _create_data_overview(self, analysis_data: Dict[str, Any]) -> List:
        """创建数据概览"""
        story = []
        
        story.append(Paragraph("数据概览", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        stats = analysis_data.get('stats', {})
        platform_dist = stats.get('platform_distribution', {})
        
        # 数据统计表格
        data_table_data = [
            ['指标', '数值'],
            ['总帖子数量', f"{stats.get('total_posts', 0)} 条"],
            ['Twitter 帖子', f"{platform_dist.get('twitter', 0)} 条"],
            ['Reddit 帖子', f"{platform_dist.get('reddit', 0)} 条"],
            ['分析时间范围', '过去30天'],
            ['数据更新时间', datetime.now().strftime('%Y-%m-%d %H:%M')]
        ]
        
        data_table = Table(data_table_data, colWidths=[2*inch, 2*inch])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
        ]))
        
        story.append(data_table)
        
        return story

    def _create_hype_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建热度分析"""
        story = []
        
        story.append(Paragraph("热度指数分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        hype_data = analysis_data.get('hypeIndex', {})
        score = hype_data.get('score', 0)
        reasoning = hype_data.get('reasoning', '基于综合数据分析得出')
        
        # 热度等级判断
        if score >= 80:
            level = "极高热度"
            color = "#dc2626"
        elif score >= 60:
            level = "高热度"
            color = "#ea580c"
        elif score >= 40:
            level = "中等热度"
            color = "#ca8a04"
        else:
            level = "低热度"
            color = "#65a30d"
        
        hype_text = f"""
        <b>热度指数：{score}/100</b><br/>
        <b>热度等级：</b><font color="{color}">{level}</font><br/><br/>
        <b>分析说明：</b><br/>
        {reasoning}
        """
        
        story.append(Paragraph(hype_text, self.styles['CustomBody']))
        
        return story

    def _create_sentiment_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建情感分析"""
        story = []
        
        story.append(Paragraph("情感光谱分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        sentiment = analysis_data.get('sentimentSpectrum', {})
        
        # 情感分布表格
        sentiment_data = [
            ['情感类型', '占比', '解读'],
            ['积极情感', f"{sentiment.get('positive', 0)}%", '用户对话题持正面态度'],
            ['中性情感', f"{sentiment.get('neutral', 0)}%", '用户保持客观中立态度'],
            ['消极情感', f"{sentiment.get('negative', 0)}%", '用户对话题存在负面看法'],
            ['疑问情感', f"{sentiment.get('questioning', 0)}%", '用户对话题存在疑虑']
        ]
        
        sentiment_table = Table(sentiment_data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
        sentiment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
        ]))
        
        story.append(sentiment_table)
        story.append(Spacer(1, 15))
        
        # 情感分析结论
        positive_pct = sentiment.get('positive', 0)
        if positive_pct > 50:
            conclusion = "整体情感倾向积极，用户对该话题持正面态度，有利于品牌传播和产品推广。"
        elif positive_pct > 30:
            conclusion = "情感分布相对均衡，用户态度较为理性，需要针对性的沟通策略。"
        else:
            conclusion = "需要关注负面情感，建议深入了解用户关切点，制定改善策略。"
        
        story.append(Paragraph(f"<b>分析结论：</b>{conclusion}", self.styles['CustomBody']))
        
        return story

    def _create_themes_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建核心主题分析"""
        story = []
        
        story.append(Paragraph("核心主题分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        themes = analysis_data.get('keyThemes', [])
        
        if themes:
            for i, theme in enumerate(themes, 1):
                theme_title = theme.get('theme', f'主题 {i}')
                theme_summary = theme.get('summary', '暂无描述')
                is_emerging = theme.get('isEmerging', False)
                
                emerging_text = "🔥 新兴主题" if is_emerging else "📊 常规主题"
                
                theme_text = f"""
                <b>{i}. {theme_title}</b> {emerging_text}<br/>
                {theme_summary}<br/>
                """
                
                story.append(Paragraph(theme_text, self.styles['CustomBody']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("暂无明确的主题分类数据。", self.styles['CustomBody']))
        
        return story

    def _create_persona_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建用户画像分析"""
        story = []
        
        story.append(Paragraph("用户画像分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        persona_data = analysis_data.get('userPersonaSnapshot', {})
        personas = persona_data.get('personas', [])
        core_needs = persona_data.get('coreNeeds', [])
        
        # 用户类型
        if personas:
            story.append(Paragraph("<b>主要用户类型：</b>", self.styles['CustomHeading2']))
            for i, persona in enumerate(personas, 1):
                story.append(Paragraph(f"{i}. {persona}", self.styles['CustomBody']))
            story.append(Spacer(1, 15))
        
        # 核心需求
        if core_needs:
            story.append(Paragraph("<b>用户核心需求：</b>", self.styles['CustomHeading2']))
            for i, need in enumerate(core_needs, 1):
                story.append(Paragraph(f"{i}. {need}", self.styles['CustomBody']))
        
        return story

    def _create_opportunities_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建商业机会分析"""
        story = []
        
        story.append(Paragraph("商业机会分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        opportunities = analysis_data.get('actionableOpportunities', [])
        
        if opportunities:
            for i, opp in enumerate(opportunities, 1):
                opp_title = opp.get('opportunity', f'机会 {i}')
                opp_desc = opp.get('description', '暂无描述')
                target_persona = opp.get('targetPersona', '目标用户')
                
                opp_text = f"""
                <b>{i}. {opp_title}</b><br/>
                <b>目标用户：</b>{target_persona}<br/>
                <b>机会描述：</b>{opp_desc}<br/>
                """
                
                story.append(Paragraph(opp_text, self.styles['CustomBody']))
                story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("基于当前数据分析，暂未发现明确的商业机会。", self.styles['CustomBody']))
        
        return story

    def _create_top_mentions_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """创建热门内容分析"""
        story = []
        
        story.append(Paragraph("热门内容分析", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        top_mentions = analysis_data.get('top_mentions', [])
        
        if top_mentions:
            for i, mention in enumerate(top_mentions[:5], 1):
                platform = mention.get('platform', 'unknown').upper()
                author = mention.get('author', 'anonymous')
                text = mention.get('text', '')[:200] + ('...' if len(mention.get('text', '')) > 200 else '')
                likes = mention.get('likes', 0)
                sentiment = mention.get('sentiment', 'neutral')
                
                sentiment_emoji = {'positive': '😊', 'negative': '😞', 'neutral': '😐'}.get(sentiment, '😐')
                
                mention_text = f"""
                <b>{i}. {platform} - @{author}</b> {sentiment_emoji}<br/>
                "{text}"<br/>
                <b>互动数：</b>{likes} | <b>情感：</b>{sentiment}<br/>
                """
                
                story.append(Paragraph(mention_text, self.styles['CustomBody']))
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("暂无热门内容数据。", self.styles['CustomBody']))
        
        return story

    def _create_conclusions(self, analysis_data: Dict[str, Any], keywords: List[str]) -> List:
        """创建结论与建议"""
        story = []
        
        story.append(Paragraph("结论与建议", self.styles['CustomHeading1']))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        # 总体结论
        hype_score = analysis_data.get('hypeIndex', {}).get('score', 0)
        sentiment = analysis_data.get('sentimentSpectrum', {})
        positive_pct = sentiment.get('positive', 0)
        
        if hype_score >= 70 and positive_pct >= 50:
            conclusion = f"Social media discussions about {', '.join(keywords)} show positive trends with high business value and market opportunities."
        elif hype_score >= 50:
            conclusion = f"Topics about {', '.join(keywords)} have moderate popularity, recommend continuous monitoring and developing appropriate market strategies."
        else:
            conclusion = f"Discussion popularity about {', '.join(keywords)} is relatively low, requiring further market education and promotion."
        
        story.append(Paragraph(f"<b>Overall Conclusion:</b> {conclusion}", self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Action recommendations
        recommendations = [
            "Continuously monitor social media trend changes",
            "Strengthen interaction with positive sentiment users",
            "Pay attention to negative feedback and respond promptly",
            "Leverage popular content for content marketing",
            "Regularly update analysis reports to track changes"
        ]
        
        story.append(Paragraph("<b>Action Recommendations:</b>", self.styles['CustomHeading2']))
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 30))
        
        # 报告结尾
        footer_text = f"""
        <b>报告生成信息：</b><br/>
        生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}<br/>
        报告版本：v1.0<br/>
        技术支持：社交媒体趋势分析工具
        """
        
        story.append(Paragraph(footer_text, self.styles['CustomBody']))
        
        return story

    def save_report_to_file(self, pdf_data: bytes, filename: str = None) -> str:
        """保存报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"social_media_analysis_report_{timestamp}.pdf"
        
        try:
            with open(filename, 'wb') as f:
                f.write(pdf_data)
            logger.info(f"报告已保存到: {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None