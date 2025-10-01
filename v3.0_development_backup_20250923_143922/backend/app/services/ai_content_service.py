"""
AI内容生成服务
使用智谱AI GLM-4.5生成专业化的商业分析内容
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)

class AIContentService:
    """AI内容生成服务"""
    
    def __init__(self):
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.client = None
        # 如果API密钥是mock值或未配置，则使用fallback数据
        self.available = bool(self.api_key) and self.api_key not in ["your_zhipu_api_key_here", "mock_key_for_testing"]
        
        if self.available:
            try:
                self.client = ZhipuAI(api_key=self.api_key)
                logger.info("智谱AI服务已初始化")
            except Exception as e:
                logger.error(f"智谱AI初始化失败: {e}")
                self.available = False
        else:
            logger.warning("智谱AI API密钥未配置或为mock值，将使用增强mock数据")
    
    async def generate_enhanced_overview(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强的市场概览"""
        if not self.available:
            return self._get_fallback_overview(keyword, context)
        
        try:
            prompt = f"""
作为一名资深商业分析师，请为关键词"{keyword}"生成详细的市场概览分析。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}
- 预算范围：{context.get('budget', '10万以下')}
- 时间线：{context.get('timeline', '3-6个月')}

请提供以下结构化分析（请以JSON格式返回）：
{{
    "industry_overview": {{
        "primary_industry": "主要行业分类",
        "market_maturity": "Growth/Mature/Emerging",
        "key_trends": ["趋势1", "趋势2", "趋势3"],
        "regulatory_environment": "监管环境描述"
    }},
    "market_analysis": {{
        "total_addressable_market": {{
            "size": "市场规模（数字）",
            "unit": "billion USD",
            "growth_projection": "增长预测百分比"
        }},
        "serviceable_addressable_market": {{
            "size": "可服务市场规模",
            "penetration_rate": "渗透率百分比"
        }}
    }},
    "key_metrics": {{
        "market_maturity": "Growth",
        "competitive_intensity": "Medium",
        "entry_barriers": "Medium",
        "technology_adoption": "High"
    }}
}}

请确保分析基于真实市场数据和行业洞察，提供具体可行的商业建议。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # 尝试解析JSON响应
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的市场概览")
                return result
            except json.JSONDecodeError:
                logger.warning("AI响应不是有效JSON，使用fallback数据")
                return self._get_fallback_overview(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成市场概览失败: {e}")
            return self._get_fallback_overview(keyword, context)
    
    async def generate_enhanced_competitors(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成增强的竞争对手分析"""
        if not self.available:
            return self._get_fallback_competitors(keyword, context)
        
        try:
            prompt = f"""
作为竞争情报分析师，请为"{keyword}"相关业务分析主要竞争对手。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}

请分析3-5个主要竞争对手，以JSON格式返回：
{{
    "competitors": [
        {{
            "name": "公司名称",
            "market_share": 数字（百分比），
            "market_position": "Market Leader/Strong Competitor/Niche Player",
            "founded": 年份,
            "headquarters": "总部位置",
            "funding": "融资情况",
            "employees": "员工数量",
            "strengths": ["优势1", "优势2", "优势3"],
            "weaknesses": ["劣势1", "劣势2", "劣势3"],
            "pricing_model": "定价模式",
            "competitive_advantage": "核心竞争优势",
            "technology_stack": ["技术1", "技术2", "技术3"],
            "customer_segments": ["客户群体1", "客户群体2"],
            "financial_metrics": {{
                "annual_revenue": "年收入",
                "growth_rate": "增长率",
                "valuation": "估值",
                "burn_rate": "烧钱率或盈利状态",
                "funding_stage": "融资阶段"
            }},
            "recent_developments": ["最新发展1", "最新发展2"]
        }}
    ]
}}

请确保分析真实准确，基于公开可获得的信息。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的竞争对手分析")
                return result.get("competitors", [])
            except json.JSONDecodeError:
                logger.warning("AI竞争对手分析响应不是有效JSON，使用fallback数据")
                return self._get_fallback_competitors(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成竞争对手分析失败: {e}")
            return self._get_fallback_competitors(keyword, context)
    
    async def generate_enhanced_personas(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成增强的用户画像"""
        if not self.available:
            return self._get_fallback_personas(keyword, context)
        
        try:
            prompt = f"""
作为用户研究专家，请为"{keyword}"相关产品/服务分析目标用户画像。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}

请创建3-4个详细的用户画像，以JSON格式返回：
{{
    "personas": [
        {{
            "name": "画像名称",
            "description": "画像描述",
            "demographics": {{
                "age": "年龄范围",
                "income": "收入范围",
                "location": "地理位置",
                "education": "教育背景",
                "company_size": "公司规模（如适用）",
                "job_titles": ["职位1", "职位2", "职位3"]
            }},
            "psychographics": {{
                "personality_traits": ["特质1", "特质2", "特质3"],
                "values": ["价值观1", "价值观2", "价值观3"],
                "lifestyle": "生活方式描述",
                "technology_comfort": "技术接受度"
            }},
            "pain_points": ["痛点1", "痛点2", "痛点3"],
            "goals": ["目标1", "目标2", "目标3"],
            "preferred_channels": ["渠道1", "渠道2", "渠道3"],
            "content_preferences": ["内容偏好1", "内容偏好2", "内容偏好3"]
        }}
    ]
}}

请确保画像真实可信，基于实际市场研究和用户行为数据。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的用户画像")
                return result.get("personas", [])
            except json.JSONDecodeError:
                logger.warning("AI用户画像响应不是有效JSON，使用fallback数据")
                return self._get_fallback_personas(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成用户画像失败: {e}")
            return self._get_fallback_personas(keyword, context)
    
    async def generate_enhanced_opportunities(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成增强的市场机会分析"""
        if not self.available:
            return self._get_fallback_opportunities(keyword, context)
        
        try:
            prompt = f"""
作为战略咨询师，请为"{keyword}"相关业务识别关键市场机会。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}
- 预算范围：{context.get('budget', '10万以下')}
- 时间线：{context.get('timeline', '3-6个月')}

请识别4-6个具体的市场机会，按类别组织，以JSON格式返回：
{{
    "opportunity_categories": [
        {{
            "category": "类别名称",
            "opportunities": [
                {{
                    "title": "机会标题",
                    "description": "详细描述",
                    "market_size": "市场规模",
                    "timeline": "实现时间线",
                    "investment_required": "所需投资",
                    "risk_level": "High/Medium/Low",
                    "success_probability": "成功概率范围",
                    "market_drivers": ["驱动因素1", "驱动因素2"],
                    "competitive_advantages": ["优势1", "优势2"],
                    "revenue_streams": ["收入来源1", "收入来源2"],
                    "key_metrics": {{
                        "market_growth_rate": "市场增长率",
                        "customer_acquisition_cost": "获客成本",
                        "lifetime_value": "客户生命周期价值",
                        "gross_margin": "毛利率"
                    }},
                    "strategic_recommendations": ["建议1", "建议2"]
                }}
            ]
        }}
    ]
}}

请确保机会分析具体可行，符合当前市场趋势和技术发展。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的市场机会分析")
                return result.get("opportunity_categories", [])
            except json.JSONDecodeError:
                logger.warning("AI市场机会响应不是有效JSON，使用fallback数据")
                return self._get_fallback_opportunities(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成市场机会分析失败: {e}")
            return self._get_fallback_opportunities(keyword, context)
    
    async def generate_enhanced_risk_analysis(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强的风险分析"""
        if not self.available:
            return self._get_fallback_risk_analysis(keyword, context)
        
        try:
            prompt = f"""
作为风险管理专家，请为"{keyword}"相关业务进行全面风险评估。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}
- 预算范围：{context.get('budget', '10万以下')}

请提供详细的风险分析，以JSON格式返回：
{{
    "overall": "High/Medium/Low",
    "risk_score": 数字（1-100），
    "confidence_level": "百分比",
    "last_updated": "当前日期",
    "factors": [
        {{
            "factor": "风险因素名称",
            "level": "High/Medium/Low",
            "description": "详细描述",
            "probability": "发生概率百分比",
            "impact_score": 数字（1-10），
            "time_horizon": "短期/中期/长期",
            "indicators": ["预警指标1", "预警指标2"],
            "mitigation_strategies": ["缓解策略1", "缓解策略2"],
            "contingency_plans": ["应急计划1", "应急计划2"]
        }}
    ],
    "risk_matrix": {{
        "high_probability_high_impact": ["风险1", "风险2"],
        "high_probability_low_impact": ["风险3", "风险4"],
        "low_probability_high_impact": ["风险5", "风险6"],
        "low_probability_low_impact": ["风险7", "风险8"]
    }},
    "monitoring_schedule": {{
        "daily": ["每日监控项1", "每日监控项2"],
        "weekly": ["每周监控项1", "每周监控项2"],
        "monthly": ["每月监控项1", "每月监控项2"],
        "quarterly": ["季度监控项1", "季度监控项2"]
    }}
}}

请确保风险评估全面准确，包含具体可执行的缓解措施。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的风险分析")
                return result
            except json.JSONDecodeError:
                logger.warning("AI风险分析响应不是有效JSON，使用fallback数据")
                return self._get_fallback_risk_analysis(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成风险分析失败: {e}")
            return self._get_fallback_risk_analysis(keyword, context)
    
    async def generate_enhanced_financials(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强的财务预测"""
        if not self.available:
            return self._get_fallback_financials(keyword, context)
        
        try:
            prompt = f"""
作为财务分析师，请为"{keyword}"相关业务制定详细的财务预测模型。

背景信息：
- 目标市场：{context.get('target_market', '大众市场')}
- 商业模式：{context.get('business_model', 'B2C')}
- 发展阶段：{context.get('stage', '概念阶段')}
- 预算范围：{context.get('budget', '10万以下')}
- 时间线：{context.get('timeline', '3-6个月')}

请提供5年财务预测，以JSON格式返回：
{{
    "revenue": [
        {{
            "year": 2024,
            "conservative": 数字,
            "optimistic": 数字,
            "customers": 数字,
            "arpu": 数字,
            "growth_rate": "百分比"
        }}
    ],
    "costs": [
        {{
            "category": "成本类别",
            "percentage": 数字,
            "amount": 数字,
            "breakdown": {{
                "fixed": 数字,
                "variable": 数字,
                "one_time": 数字
            }}
        }}
    ],
    "investment_requirements": {{
        "seed_funding": {{
            "amount": "金额",
            "timeline": "时间线",
            "use_of_funds": ["用途1", "用途2", "用途3"]
        }},
        "series_a": {{
            "amount": "金额",
            "timeline": "时间线",
            "milestones": ["里程碑1", "里程碑2"]
        }}
    }},
    "profitability_analysis": {{
        "break_even_point": "盈亏平衡点",
        "gross_margin_trend": ["年份1: 百分比", "年份2: 百分比"],
        "operating_margin_trend": ["年份1: 百分比", "年份2: 百分比"],
        "cash_flow_positive": "现金流转正时间"
    }},
    "key_metrics": {{
        "customer_acquisition_cost": 数字,
        "lifetime_value": 数字,
        "ltv_cac_ratio": 数字,
        "monthly_recurring_revenue": 数字,
        "churn_rate": "百分比"
    }},
    "roi_analysis": {{
        "scenarios": {{
            "conservative": {{
                "roi": "百分比",
                "payback_period": "时间",
                "irr": "百分比"
            }},
            "optimistic": {{
                "roi": "百分比",
                "payback_period": "时间",
                "irr": "百分比"
            }}
        }},
        "sensitivity_factors": ["因素1", "因素2", "因素3"]
    }}
}}

请确保财务预测基于合理假设和行业基准数据。
"""
            
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                logger.info(f"成功生成{keyword}的财务预测")
                return result
            except json.JSONDecodeError:
                logger.warning("AI财务预测响应不是有效JSON，使用fallback数据")
                return self._get_fallback_financials(keyword, context)
                
        except Exception as e:
            logger.error(f"AI生成财务预测失败: {e}")
            return self._get_fallback_financials(keyword, context)
    
    # Fallback方法 - 当AI不可用时使用增强的mock数据
    def _get_fallback_overview(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取fallback市场概览数据"""
        return {
            "industry_overview": {
                "primary_industry": f"{keyword}相关技术服务",
                "market_maturity": "Growth",
                "key_trends": [
                    f"{keyword}技术快速发展和普及",
                    "数字化转型加速推进",
                    "用户体验要求不断提升",
                    "监管环境逐步完善"
                ],
                "regulatory_environment": "监管框架正在建立，合规要求日益严格"
            },
            "market_analysis": {
                "total_addressable_market": {
                    "value": "850",
                    "unit": "billion USD",
                    "growth_projection": "28%"
                },
                "serviceable_addressable_market": {
                    "value": "120",
                    "unit": "billion USD",
                    "penetration_rate": "15%"
                },
                "serviceable_obtainable_market": {
                    "value": "25",
                    "unit": "billion USD",
                    "penetration_rate": "3%"
                }
            },
            "key_metrics": {
                "market_maturity": "Growth",
                "competitive_intensity": "Medium",
                "entry_barriers": "Medium",
                "technology_adoption": "High"
            }
        }
    
    def _get_fallback_competitors(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取fallback竞争对手数据"""
        return [
            {
                "name": f"{keyword} Market Leader",
                "market_share": 35,
                "market_position": "Market Leader",
                "founded": 2018,
                "headquarters": "San Francisco, CA",
                "funding": "$500M Series C",
                "employees": "1000+",
                "strengths": [
                    "强大的技术团队和研发能力",
                    "广泛的客户基础和品牌认知",
                    "完善的产品生态系统"
                ],
                "weaknesses": [
                    "高昂的运营成本",
                    "产品复杂度较高",
                    "客户服务响应速度有待提升"
                ],
                "pricing_model": "订阅制 + 按使用量计费",
                "competitive_advantage": "技术领先和生态完整性",
                "technology_stack": ["React", "Node.js", "PostgreSQL", "Redis", "AWS"],
                "customer_segments": ["企业客户", "中小企业", "开发者"],
                "financial_metrics": {
                    "annual_revenue": "$150M",
                    "growth_rate": "120% YoY",
                    "valuation": "$2.5B",
                    "burn_rate": "$8M/month",
                    "funding_stage": "Series C"
                },
                "recent_developments": [
                    f"推出新一代{keyword}解决方案",
                    "完成重要战略合作伙伴关系",
                    "扩展到新的地理市场"
                ]
            }
        ]
    
    def _get_fallback_personas(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取fallback用户画像数据"""
        return [
            {
                "name": f"{keyword}技术决策者",
                "description": f"负责{keyword}相关技术选型和实施的企业决策者",
                "demographics": {
                    "age": "35-50",
                    "income": "$100k-300k",
                    "location": "一线城市",
                    "education": "本科及以上学历",
                    "company_size": "100-1000人",
                    "job_titles": ["技术总监", "CTO", "产品负责人"]
                },
                "psychographics": {
                    "personality_traits": ["理性决策", "注重效率", "技术敏感"],
                    "values": ["技术创新", "团队协作", "持续学习"],
                    "lifestyle": "工作繁忙的技术专业人士",
                    "technology_comfort": "专家级"
                },
                "pain_points": [
                    "技术选型决策压力大",
                    "需要平衡成本和效果",
                    "团队技能提升需求"
                ],
                "goals": [
                    "提升团队技术能力",
                    "优化产品性能和用户体验",
                    "控制技术成本和风险"
                ],
                "preferred_channels": [
                    "技术会议和研讨会",
                    "行业报告和白皮书",
                    "同行推荐和案例分享"
                ],
                "content_preferences": [
                    "技术深度分析",
                    "实施案例研究",
                    "ROI和成本效益分析"
                ]
            }
        ]
    
    def _get_fallback_opportunities(self, keyword: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取fallback市场机会数据"""
        return [
            {
                "category": "技术创新机会",
                "opportunities": [
                    {
                        "title": f"下一代{keyword}平台",
                        "description": f"开发更智能、更高效的{keyword}解决方案",
                        "market_size": "$50-200M",
                        "timeline": "12-18个月",
                        "investment_required": "$2-8M",
                        "risk_level": "Medium",
                        "success_probability": "70-80%",
                        "market_drivers": [
                            "技术成熟度提升",
                            "市场需求增长",
                            "竞争格局变化"
                        ],
                        "competitive_advantages": [
                            "技术领先性",
                            "用户体验优化",
                            "成本效益提升"
                        ],
                        "revenue_streams": [
                            "SaaS订阅收入",
                            "专业服务收入",
                            "API调用费用"
                        ],
                        "key_metrics": {
                            "market_growth_rate": "35% CAGR",
                            "customer_acquisition_cost": "$5,000",
                            "lifetime_value": "$50,000",
                            "gross_margin": "75%"
                        },
                        "strategic_recommendations": [
                            "专注核心技术差异化",
                            "建立强大的合作伙伴生态",
                            "投资用户体验和客户成功"
                        ]
                    }
                ]
            }
        ]
    
    def _get_fallback_risk_analysis(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取fallback风险分析数据"""
        return {
            "overall": "Medium",
            "risk_score": 65,
            "confidence_level": "80%",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "factors": [
                {
                    "factor": "市场竞争风险",
                    "level": "High",
                    "description": "市场竞争激烈，新进入者不断涌现",
                    "probability": "75%",
                    "impact_score": 8,
                    "time_horizon": "短期",
                    "indicators": ["竞争对手融资动态", "市场份额变化", "价格战趋势"],
                    "mitigation_strategies": ["差异化定位", "技术护城河建设", "客户关系深化"],
                    "contingency_plans": ["快速产品迭代", "价格策略调整", "市场重新定位"]
                },
                {
                    "factor": "技术风险",
                    "level": "Medium",
                    "description": "技术发展快速，存在技术路线选择风险",
                    "probability": "50%",
                    "impact_score": 7,
                    "time_horizon": "中期",
                    "indicators": ["技术趋势变化", "研发进度", "技术团队稳定性"],
                    "mitigation_strategies": ["技术路线多样化", "持续技术投入", "人才梯队建设"],
                    "contingency_plans": ["技术架构重构", "外部技术合作", "人才引进计划"]
                }
            ],
            "risk_matrix": {
                "high_probability_high_impact": ["市场竞争加剧", "关键人才流失"],
                "high_probability_low_impact": ["小幅成本上升", "监管政策调整"],
                "low_probability_high_impact": ["重大技术变革", "经济环境恶化"],
                "low_probability_low_impact": ["供应商变更", "办公成本波动"]
            },
            "monitoring_schedule": {
                "daily": ["竞争对手动态", "技术指标监控"],
                "weekly": ["市场趋势分析", "团队状态评估"],
                "monthly": ["财务指标审查", "客户满意度调研"],
                "quarterly": ["战略目标评估", "风险矩阵更新"]
            }
        }
    
    def _get_fallback_financials(self, keyword: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取fallback财务预测数据"""
        return {
            "revenue": [
                {"year": 2024, "conservative": 500000, "optimistic": 800000, "customers": 50, "arpu": 10000, "growth_rate": "0%"},
                {"year": 2025, "conservative": 1200000, "optimistic": 2000000, "customers": 120, "arpu": 10000, "growth_rate": "140%"},
                {"year": 2026, "conservative": 2800000, "optimistic": 5000000, "customers": 280, "arpu": 10000, "growth_rate": "133%"},
                {"year": 2027, "conservative": 5600000, "optimistic": 10000000, "customers": 560, "arpu": 10000, "growth_rate": "100%"},
                {"year": 2028, "conservative": 10000000, "optimistic": 18000000, "customers": 1000, "arpu": 10000, "growth_rate": "79%"}
            ],
            "costs": [
                {"category": "研发", "percentage": 35, "amount": 350000, "breakdown": {"fixed": 200000, "variable": 150000, "one_time": 0}},
                {"category": "销售与市场", "percentage": 25, "amount": 250000, "breakdown": {"fixed": 100000, "variable": 150000, "one_time": 0}},
                {"category": "运营", "percentage": 20, "amount": 200000, "breakdown": {"fixed": 150000, "variable": 50000, "one_time": 0}},
                {"category": "管理", "percentage": 15, "amount": 150000, "breakdown": {"fixed": 120000, "variable": 30000, "one_time": 0}},
                {"category": "其他", "percentage": 5, "amount": 50000, "breakdown": {"fixed": 30000, "variable": 20000, "one_time": 0}}
            ],
            "funding_requirements": {
                "seed_round": {
                    "amount": "$1-3M",
                    "timeline": "6-12个月",
                    "use_of_funds": ["产品开发", "团队建设", "市场验证"]
                },
                "series_a": {
                    "amount": "$5-15M",
                    "timeline": "18-24个月",
                    "milestones": ["产品市场契合", "收入增长验证"]
                }
            },
            "profitability_analysis": {
                "break_even_point": "第3年第2季度",
                "gross_margin_trend": ["2024: 60%", "2025: 65%", "2026: 70%", "2027: 72%", "2028: 75%"],
                "operating_margin_trend": ["2024: -40%", "2025: -15%", "2026: 5%", "2027: 15%", "2028: 25%"],
                "cash_flow_positive": "第3年第1季度"
            },
            "key_metrics": {
                "customer_acquisition_cost": 2500,
                "lifetime_value": 25000,
                "ltv_cac_ratio": 10,
                "monthly_recurring_revenue": 83333,
                "churn_rate": "5%"
            },
            "roi_analysis": {
                "scenarios": {
                    "conservative": {
                        "roi": "300%",
                        "payback_period": "4年",
                        "irr": "35%"
                    },
                    "optimistic": {
                        "roi": "600%",
                        "payback_period": "3年",
                        "irr": "55%"
                    }
                },
                "sensitivity_factors": ["客户获取成本", "客户流失率", "平均客单价"]
            }
        }

# 全局实例
ai_content_service = AIContentService()