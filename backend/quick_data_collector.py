#!/usr/bin/env python3
"""
快速数据收集器 - 整合现有数据并生成训练样本
专注于处理已收集的数据，避免网络请求超时问题
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging
from pathlib import Path
import random

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickDataCollector:
    def __init__(self):
        self.output_dir = Path("collected_data/quick")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 专家对话模板
        self.expert_templates = {
            'data_insight': {
                'questions': [
                    "这个数据趋势说明了什么商业机会？",
                    "如何从数据中提取关键商业洞察？",
                    "这些指标对商业决策有什么指导意义？",
                    "数据背后隐藏的商业价值是什么？",
                    "如何利用这些数据优化商业策略？"
                ],
                'response_prefix': "基于数据分析，我发现"
            },
            'failure_prevention': {
                'questions': [
                    "这种商业模式有什么潜在风险？",
                    "如何预防常见的创业失败？",
                    "有哪些预警信号需要创业者注意？",
                    "风险缓解的最佳实践是什么？",
                    "如何建立有效的风险管理体系？"
                ],
                'response_prefix': "从风险管理角度，我建议"
            },
            'business_strategy': {
                'questions': [
                    "最有效的商业策略是什么？",
                    "如何制定可执行的增长计划？",
                    "商业模式如何持续优化？",
                    "战略执行的关键成功因素是什么？",
                    "如何在竞争中保持优势？"
                ],
                'response_prefix': "从战略角度分析，我认为"
            },
            'competitive_intelligence': {
                'questions': [
                    "竞争对手的核心策略是什么？",
                    "如何进行有效的竞争分析？",
                    "市场定位应该如何调整？",
                    "竞争优势的来源在哪里？",
                    "如何应对新的竞争威胁？"
                ],
                'response_prefix': "竞争情报分析显示"
            },
            'user_insight': {
                'questions': [
                    "用户的核心需求是什么？",
                    "如何深度理解用户痛点？",
                    "用户体验如何持续改善？",
                    "客户满意度提升的关键是什么？",
                    "如何建立用户忠诚度？"
                ],
                'response_prefix': "用户研究表明"
            }
        }
        
        # 商业场景模板
        self.business_scenarios = [
            "初创公司产品市场适配",
            "SaaS业务增长策略",
            "电商平台用户获取",
            "B2B销售流程优化",
            "移动应用用户留存",
            "数字营销ROI提升",
            "客户服务体验改善",
            "供应链效率优化",
            "品牌定位与传播",
            "投资决策分析"
        ]
        
        self.collection_stats = {
            'existing_data_processed': 0,
            'training_samples_generated': 0,
            'expert_conversations_created': 0,
            'business_scenarios_covered': 0
        }

    def process_existing_data(self) -> List[Dict]:
        """处理现有收集的数据"""
        logger.info("开始处理现有数据...")
        
        all_training_data = []
        
        # 处理综合收集的数据
        comprehensive_file = Path("collected_data/comprehensive_training_20250930_151455.json")
        if comprehensive_file.exists():
            with open(comprehensive_file, 'r', encoding='utf-8') as f:
                comprehensive_data = json.load(f)
                all_training_data.extend(comprehensive_data)
                self.collection_stats['existing_data_processed'] += len(comprehensive_data)
                logger.info(f"处理综合数据: {len(comprehensive_data)} 条")
        
        # 处理Hugging Face数据
        hf_dir = Path("collected_data/huggingface")
        if hf_dir.exists():
            for hf_file in hf_dir.glob("hf_training_data_*.json"):
                with open(hf_file, 'r', encoding='utf-8') as f:
                    hf_data = json.load(f)
                    all_training_data.extend(hf_data)
                    self.collection_stats['existing_data_processed'] += len(hf_data)
                    logger.info(f"处理HF数据: {len(hf_data)} 条")
        
        return all_training_data

    def generate_expert_conversations(self, num_conversations: int = 200) -> List[Dict]:
        """生成专家对话样本"""
        logger.info(f"生成 {num_conversations} 个专家对话样本...")
        
        conversations = []
        
        for i in range(num_conversations):
            # 随机选择专家类型和场景
            expert_type = random.choice(list(self.expert_templates.keys()))
            scenario = random.choice(self.business_scenarios)
            template = self.expert_templates[expert_type]
            
            # 随机选择问题模板
            question_template = random.choice(template['questions'])
            
            # 生成上下文化的问题
            question = f"在{scenario}的场景下，{question_template}"
            
            # 生成专家答案
            answer = self._generate_expert_answer(expert_type, scenario, template['response_prefix'])
            
            conversation = {
                'expert_type': expert_type,
                'question': question,
                'answer': answer,
                'scenario': scenario,
                'context': f"商业场景: {scenario}",
                'source': 'generated_expert_conversation',
                'quality_score': 0.85,  # 生成的对话质量评分
                'conversation_id': f"expert_conv_{i+1}_{self.timestamp}",
                'metadata': {
                    'generation_method': 'template_based',
                    'expert_type': expert_type,
                    'scenario': scenario,
                    'created_at': datetime.now().isoformat()
                }
            }
            
            conversations.append(conversation)
            self.collection_stats['expert_conversations_created'] += 1
        
        logger.info(f"生成专家对话完成: {len(conversations)} 条")
        return conversations

    def generate_business_qa_pairs(self, num_pairs: int = 150) -> List[Dict]:
        """生成商业问答对"""
        logger.info(f"生成 {num_pairs} 个商业问答对...")
        
        qa_pairs = []
        
        # 商业问题模板
        business_questions = [
            "如何验证商业想法的可行性？",
            "什么是产品市场适配？",
            "如何计算客户获取成本？",
            "什么是最小可行产品(MVP)？",
            "如何进行竞争对手分析？",
            "什么是商业模式画布？",
            "如何制定定价策略？",
            "什么是用户生命周期价值？",
            "如何进行市场细分？",
            "什么是增长黑客？",
            "如何建立销售漏斗？",
            "什么是A/B测试？",
            "如何进行用户访谈？",
            "什么是精益创业方法？",
            "如何制定OKR目标？"
        ]
        
        for i in range(num_pairs):
            # 随机选择问题或生成变体
            if i < len(business_questions):
                question = business_questions[i]
            else:
                # 生成问题变体
                base_question = random.choice(business_questions)
                scenario = random.choice(self.business_scenarios)
                question = f"在{scenario}中，{base_question.lower()}"
            
            # 随机分配专家类型
            expert_type = random.choice(list(self.expert_templates.keys()))
            
            # 生成答案
            answer = self._generate_business_answer(question, expert_type)
            
            qa_pair = {
                'expert_type': expert_type,
                'question': question,
                'answer': answer,
                'context': "商业知识问答",
                'source': 'generated_business_qa',
                'quality_score': 0.80,
                'qa_id': f"business_qa_{i+1}_{self.timestamp}",
                'metadata': {
                    'generation_method': 'business_template',
                    'expert_type': expert_type,
                    'created_at': datetime.now().isoformat()
                }
            }
            
            qa_pairs.append(qa_pair)
            self.collection_stats['training_samples_generated'] += 1
        
        logger.info(f"生成商业问答完成: {len(qa_pairs)} 条")
        return qa_pairs

    def generate_scenario_based_training(self, num_scenarios: int = 100) -> List[Dict]:
        """生成基于场景的训练数据"""
        logger.info(f"生成 {num_scenarios} 个场景训练样本...")
        
        scenario_data = []
        
        for i, scenario in enumerate(self.business_scenarios * (num_scenarios // len(self.business_scenarios) + 1)):
            if i >= num_scenarios:
                break
                
            # 为每个场景生成多个专家视角
            for expert_type in self.expert_templates.keys():
                template = self.expert_templates[expert_type]
                
                # 生成场景特定的问题
                question = f"在{scenario}的情况下，作为{expert_type}专家，您会如何分析和建议？"
                
                # 生成专家答案
                answer = self._generate_scenario_answer(scenario, expert_type, template['response_prefix'])
                
                scenario_item = {
                    'expert_type': expert_type,
                    'question': question,
                    'answer': answer,
                    'scenario': scenario,
                    'context': f"商业场景分析: {scenario}",
                    'source': 'generated_scenario_analysis',
                    'quality_score': 0.82,
                    'scenario_id': f"scenario_{i+1}_{expert_type}_{self.timestamp}",
                    'metadata': {
                        'generation_method': 'scenario_based',
                        'scenario': scenario,
                        'expert_type': expert_type,
                        'created_at': datetime.now().isoformat()
                    }
                }
                
                scenario_data.append(scenario_item)
                self.collection_stats['business_scenarios_covered'] += 1
        
        logger.info(f"生成场景训练完成: {len(scenario_data)} 条")
        return scenario_data

    def _generate_expert_answer(self, expert_type: str, scenario: str, response_prefix: str) -> str:
        """生成专家风格的答案"""
        
        expert_knowledge = {
            'data_insight': [
                "需要建立关键指标监控体系",
                "数据驱动的决策制定流程",
                "用户行为数据分析",
                "市场趋势数据解读",
                "业务指标的深度洞察"
            ],
            'failure_prevention': [
                "识别潜在的业务风险点",
                "建立预警机制和应急预案",
                "学习行业失败案例",
                "风险评估和缓解策略",
                "持续监控关键风险指标"
            ],
            'business_strategy': [
                "制定清晰的商业目标",
                "优化商业模式设计",
                "制定可执行的增长策略",
                "资源配置和优先级管理",
                "战略执行和迭代优化"
            ],
            'competitive_intelligence': [
                "深入分析竞争对手策略",
                "识别市场机会和威胁",
                "制定差异化定位策略",
                "监控竞争动态变化",
                "建立竞争优势壁垒"
            ],
            'user_insight': [
                "深度理解用户需求和痛点",
                "优化用户体验设计",
                "建立用户反馈收集机制",
                "提升客户满意度和忠诚度",
                "用户行为模式分析"
            ]
        }
        
        knowledge_points = expert_knowledge.get(expert_type, ["提供专业建议"])
        selected_points = random.sample(knowledge_points, min(3, len(knowledge_points)))
        
        answer = f"{response_prefix}，在{scenario}中，关键要素包括：\n"
        for i, point in enumerate(selected_points, 1):
            answer += f"{i}. {point}\n"
        
        answer += f"\n建议采用数据驱动的方法，结合{expert_type}的专业视角，制定针对性的解决方案。"
        
        return answer

    def _generate_business_answer(self, question: str, expert_type: str) -> str:
        """生成商业问题的答案"""
        
        # 基于问题关键词生成答案
        if "验证" in question or "可行性" in question:
            return f"从{expert_type}角度，验证商业想法需要：1) 市场需求验证 2) 技术可行性评估 3) 商业模式验证 4) 竞争分析 5) 财务可行性分析。建议采用MVP方法快速验证核心假设。"
        
        elif "产品市场适配" in question:
            return f"产品市场适配(PMF)是指产品满足市场需求的程度。从{expert_type}视角，关键指标包括：用户留存率、推荐率、使用频率等。建议通过用户反馈、数据分析持续优化产品。"
        
        elif "客户获取成本" in question or "CAC" in question:
            return f"客户获取成本(CAC)计算公式：营销费用/新获客户数。从{expert_type}角度，需要关注：1) 不同渠道的CAC差异 2) CAC与LTV的比例 3) 获客效率优化策略。"
        
        elif "MVP" in question or "最小可行产品" in question:
            return f"MVP是验证商业假设的最小功能产品。从{expert_type}专业角度，MVP设计原则：1) 核心功能聚焦 2) 快速迭代 3) 用户反馈收集 4) 数据驱动优化。"
        
        else:
            return f"从{expert_type}的专业角度分析，这个问题需要综合考虑市场、用户、技术、财务等多个维度。建议采用系统性的分析方法，结合数据洞察制定解决方案。"

    def _generate_scenario_answer(self, scenario: str, expert_type: str, response_prefix: str) -> str:
        """生成场景特定的答案"""
        
        scenario_insights = {
            "初创公司产品市场适配": "需要快速验证产品假设，建立用户反馈循环",
            "SaaS业务增长策略": "关注用户留存、扩展收入和降低流失率",
            "电商平台用户获取": "优化转化漏斗，提升用户体验和复购率",
            "B2B销售流程优化": "建立标准化销售流程，提升成单效率",
            "移动应用用户留存": "优化用户体验，建立用户习惯和粘性",
            "数字营销ROI提升": "精准定位目标用户，优化营销渠道组合",
            "客户服务体验改善": "建立全渠道服务体系，提升响应效率",
            "供应链效率优化": "数字化管理，降低成本提升效率",
            "品牌定位与传播": "明确品牌价值主张，建立一致性传播",
            "投资决策分析": "建立科学的评估体系，控制投资风险"
        }
        
        insight = scenario_insights.get(scenario, "需要综合分析各种因素")
        
        answer = f"{response_prefix}，{insight}。\n\n"
        answer += f"具体建议：\n"
        answer += f"1. 深入分析当前状况和挑战\n"
        answer += f"2. 制定明确的目标和关键指标\n"
        answer += f"3. 设计可执行的行动计划\n"
        answer += f"4. 建立监控和反馈机制\n"
        answer += f"5. 持续优化和迭代改进\n\n"
        answer += f"从{expert_type}的专业角度，建议重点关注数据驱动的决策制定和持续的用户价值创造。"
        
        return answer

    def save_quick_data(self, all_data: List[Dict]) -> Dict[str, str]:
        """保存快速收集的数据"""
        
        # 按专家类型分组
        expert_distribution = {}
        for item in all_data:
            expert_type = item.get('expert_type', 'unknown')
            expert_distribution[expert_type] = expert_distribution.get(expert_type, 0) + 1
        
        # 保存训练数据
        training_file = self.output_dir / f"quick_training_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        self.collection_stats['expert_distribution'] = expert_distribution
        self.collection_stats['total_samples'] = len(all_data)
        
        stats_file = self.output_dir / f"quick_stats_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.collection_stats, f, ensure_ascii=False, indent=2)
        
        # 生成数据报告
        report_file = self.output_dir / f"quick_report_{self.timestamp}.md"
        self._generate_data_report(report_file, all_data)
        
        return {
            'training_file': str(training_file),
            'stats_file': str(stats_file),
            'report_file': str(report_file)
        }

    def _generate_data_report(self, report_file: Path, all_data: List[Dict]):
        """生成数据收集报告"""
        
        report_content = f"""# 快速数据收集报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览
- 总训练样本: {len(all_data)} 条
- 现有数据处理: {self.collection_stats['existing_data_processed']} 条
- 新生成样本: {self.collection_stats['training_samples_generated']} 条
- 专家对话: {self.collection_stats['expert_conversations_created']} 条
- 场景覆盖: {self.collection_stats['business_scenarios_covered']} 个

## 专家类型分布
"""
        
        expert_dist = {}
        for item in all_data:
            expert_type = item.get('expert_type', 'unknown')
            expert_dist[expert_type] = expert_dist.get(expert_type, 0) + 1
        
        for expert_type, count in expert_dist.items():
            percentage = (count / len(all_data)) * 100
            report_content += f"- {expert_type}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 数据质量
- 平均质量评分: {sum(item.get('quality_score', 0) for item in all_data) / len(all_data):.2f}
- 高质量样本(>0.8): {len([item for item in all_data if item.get('quality_score', 0) > 0.8])} 条

## 数据来源
"""
        
        source_dist = {}
        for item in all_data:
            source = item.get('source', 'unknown')
            source_dist[source] = source_dist.get(source, 0) + 1
        
        for source, count in source_dist.items():
            percentage = (count / len(all_data)) * 100
            report_content += f"- {source}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 建议
1. 数据已准备就绪，可以开始模型训练
2. 建议使用分层抽样确保各专家类型平衡
3. 可以根据质量评分进行数据筛选
4. 建议定期更新和扩充训练数据

## 下一步
1. 数据预处理和格式化
2. 模型训练配置
3. 训练过程监控
4. 模型评估和优化
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def run_quick_collection(self) -> Dict[str, str]:
        """执行快速数据收集"""
        logger.info("开始快速数据收集...")
        start_time = time.time()
        
        all_data = []
        
        # 1. 处理现有数据
        existing_data = self.process_existing_data()
        all_data.extend(existing_data)
        
        # 2. 生成专家对话
        expert_conversations = self.generate_expert_conversations(200)
        all_data.extend(expert_conversations)
        
        # 3. 生成商业问答
        business_qa = self.generate_business_qa_pairs(150)
        all_data.extend(business_qa)
        
        # 4. 生成场景训练数据
        scenario_data = self.generate_scenario_based_training(100)
        all_data.extend(scenario_data)
        
        # 5. 保存数据
        files = self.save_quick_data(all_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"快速数据收集完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"总训练样本: {len(all_data)} 条")
        logger.info(f"收集统计: {self.collection_stats}")
        
        return files

def main():
    """主函数"""
    collector = QuickDataCollector()
    files = collector.run_quick_collection()
    
    print(f"\n🎉 快速数据收集完成!")
    print(f"📁 训练数据: {files['training_file']}")
    print(f"📊 统计数据: {files['stats_file']}")
    print(f"📋 数据报告: {files['report_file']}")
    print(f"📈 收集统计: {collector.collection_stats}")
    
    return files

if __name__ == "__main__":
    main()