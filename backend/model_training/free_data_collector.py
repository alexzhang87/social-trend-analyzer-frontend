#!/usr/bin/env python3
"""
免费数据源自动收集系统
用于从多个免费渠道收集AI专家顾问训练数据
"""

import json
import time
import random
import requests
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import re
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeDataCollector:
    def __init__(self):
        self.collected_data = []
        self.expert_types = [
            'data_insight',
            'business_strategy', 
            'user_insight',
            'competitive_intelligence',
            'failure_prevention'
        ]
        
        # 数据源配置
        self.data_sources = {
            'github_issues': {
                'enabled': True,
                'repos': [
                    'microsoft/vscode',
                    'facebook/react',
                    'tensorflow/tensorflow',
                    'pytorch/pytorch',
                    'kubernetes/kubernetes'
                ]
            },
            'stackoverflow': {
                'enabled': True,
                'tags': ['business-intelligence', 'data-analysis', 'strategy', 'user-experience', 'analytics']
            },
            'reddit': {
                'enabled': True,
                'subreddits': ['entrepreneur', 'datascience', 'analytics', 'business', 'startups']
            },
            'synthetic_generation': {
                'enabled': True,
                'templates_per_type': 500
            }
        }
    
    def generate_synthetic_data(self, target_count: int = 2000) -> List[Dict]:
        """生成合成训练数据"""
        logger.info(f"开始生成 {target_count} 条合成数据...")
        
        # 数据模板
        templates = {
            'data_insight': [
                {
                    'input': '如何分析{metric}数据来发现{insight_type}？',
                    'context': '我们有{data_source}的数据，想要了解{business_goal}',
                    'output': '分析{metric}数据的关键步骤包括：1) 数据清洗和预处理 2) 探索性数据分析 3) 统计建模 4) 可视化展示 5) 洞察提取和验证',
                    'quality_score': 0.8
                },
                {
                    'input': '{data_source}数据显示{trend}，这意味着什么？',
                    'context': '我们观察到{specific_metric}在{time_period}期间的变化',
                    'output': '这个趋势表明{interpretation}。建议采取以下行动：{recommendations}',
                    'quality_score': 0.75
                }
            ],
            'business_strategy': [
                {
                    'input': '如何制定{business_area}的战略规划？',
                    'context': '我们是一家{company_type}，目标是{business_goal}',
                    'output': '制定{business_area}战略需要：1) 市场分析 2) 竞争对手研究 3) SWOT分析 4) 目标设定 5) 执行计划',
                    'quality_score': 0.85
                },
                {
                    'input': '面对{challenge}，我们应该采取什么策略？',
                    'context': '当前市场环境是{market_condition}，我们的资源有{resources}',
                    'output': '建议采用{strategy_type}策略，具体包括：{specific_actions}',
                    'quality_score': 0.8
                }
            ],
            'user_insight': [
                {
                    'input': '用户{behavior}行为说明了什么？',
                    'context': '我们观察到用户在{scenario}中表现出{specific_behavior}',
                    'output': '这种行为反映了用户的{need_type}需求。建议优化{improvement_area}来提升用户体验',
                    'quality_score': 0.78
                },
                {
                    'input': '如何提升{user_segment}的{metric}？',
                    'context': '目前{user_segment}的{metric}为{current_value}，目标是{target_value}',
                    'output': '提升策略包括：1) 用户调研 2) 痛点分析 3) 解决方案设计 4) A/B测试 5) 持续优化',
                    'quality_score': 0.82
                }
            ],
            'competitive_intelligence': [
                {
                    'input': '竞争对手{competitor}在{area}方面有什么优势？',
                    'context': '我们发现{competitor}在{specific_metric}上表现更好',
                    'output': '分析显示{competitor}的优势在于{advantage_areas}。我们可以通过{counter_strategies}来应对',
                    'quality_score': 0.77
                },
                {
                    'input': '如何监控{market}市场的竞争动态？',
                    'context': '我们需要了解{market}中主要竞争对手的{focus_areas}',
                    'output': '建立竞争监控体系：1) 定期市场调研 2) 产品功能对比 3) 价格策略分析 4) 营销活动跟踪',
                    'quality_score': 0.8
                }
            ],
            'failure_prevention': [
                {
                    'input': '如何预防{failure_type}失败？',
                    'context': '我们担心在{scenario}中可能出现{risk_type}风险',
                    'output': '预防措施包括：1) 风险识别 2) 影响评估 3) 预警机制 4) 应急预案 5) 定期检查',
                    'quality_score': 0.83
                },
                {
                    'input': '项目{project_type}失败的主要原因是什么？',
                    'context': '我们正在规划{project_type}，想要避免常见的失败陷阱',
                    'output': '常见失败原因：{failure_reasons}。建议采取{prevention_strategies}来降低风险',
                    'quality_score': 0.79
                }
            ]
        }
        
        # 变量池
        variables = {
            'metric': ['转化率', '留存率', '活跃度', '满意度', '收入', '成本', '效率'],
            'insight_type': ['用户行为模式', '市场趋势', '业务机会', '风险点', '增长驱动因素'],
            'data_source': ['用户行为数据', '销售数据', '市场调研数据', '产品使用数据', '财务数据'],
            'business_goal': ['提升用户体验', '增加收入', '降低成本', '扩大市场份额', '提高效率'],
            'trend': ['上升趋势', '下降趋势', '波动模式', '季节性变化', '异常峰值'],
            'business_area': ['产品开发', '市场营销', '销售', '客户服务', '运营管理'],
            'company_type': ['科技公司', '电商平台', '制造企业', '服务公司', '初创公司'],
            'challenge': ['市场竞争加剧', '用户流失', '成本上升', '技术变革', '监管变化'],
            'behavior': ['购买', '浏览', '分享', '评价', '流失'],
            'user_segment': ['新用户', '活跃用户', '付费用户', '流失用户', '高价值用户'],
            'competitor': ['主要竞争对手', '新兴竞争者', '行业领导者', '细分市场竞争者'],
            'failure_type': ['产品', '项目', '营销活动', '战略', '运营'],
            'project_type': ['新产品开发', '市场扩张', '数字化转型', '成本优化', '团队重组']
        }
        
        synthetic_data = []
        per_type = target_count // len(self.expert_types)
        
        for expert_type in self.expert_types:
            for i in range(per_type):
                template = random.choice(templates[expert_type])
                
                # 填充模板变量
                filled_template = {}
                for key, value in template.items():
                    if isinstance(value, str):
                        filled_value = value
                        # 查找并替换变量
                        for var_name, var_values in variables.items():
                            pattern = f'{{{var_name}}}'
                            if pattern in filled_value:
                                filled_value = filled_value.replace(pattern, random.choice(var_values))
                        filled_template[key] = filled_value
                    else:
                        filled_template[key] = value
                
                # 创建数据样本
                sample = {
                    'expert_type': expert_type,
                    'input': filled_template['input'],
                    'output': filled_template['output'],
                    'context': filled_template['context'],
                    'quality_score': filled_template['quality_score'] + random.uniform(-0.1, 0.1),
                    'metadata': {
                        'source': 'synthetic',
                        'generated_at': datetime.now().isoformat(),
                        'template_id': hashlib.md5(str(template).encode()).hexdigest()[:8]
                    }
                }
                
                synthetic_data.append(sample)
        
        logger.info(f"生成了 {len(synthetic_data)} 条合成数据")
        return synthetic_data
    
    def collect_github_data(self, max_samples: int = 1000) -> List[Dict]:
        """从GitHub Issues收集数据"""
        logger.info("开始从GitHub收集数据...")
        github_data = []
        
        try:
            for repo in self.data_sources['github_issues']['repos']:
                logger.info(f"收集 {repo} 的issues...")
                
                # GitHub API (无需认证的公开数据)
                url = f"https://api.github.com/repos/{repo}/issues"
                params = {
                    'state': 'closed',
                    'per_page': 50,
                    'sort': 'updated'
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    issues = response.json()
                    
                    for issue in issues[:20]:  # 限制每个repo的数量
                        if issue.get('body') and len(issue['body']) > 50:
                            # 根据issue内容分类专家类型
                            expert_type = self._classify_github_issue(issue)
                            
                            sample = {
                                'expert_type': expert_type,
                                'input': issue['title'],
                                'output': self._extract_solution_from_issue(issue),
                                'context': issue['body'][:500],  # 限制长度
                                'quality_score': self._calculate_github_quality(issue),
                                'metadata': {
                                    'source': 'github',
                                    'repo': repo,
                                    'issue_id': issue['id'],
                                    'created_at': issue['created_at']
                                }
                            }
                            github_data.append(sample)
                
                time.sleep(1)  # 避免API限制
                
                if len(github_data) >= max_samples:
                    break
                    
        except Exception as e:
            logger.warning(f"GitHub数据收集出错: {e}")
        
        logger.info(f"从GitHub收集了 {len(github_data)} 条数据")
        return github_data
    
    def _classify_github_issue(self, issue: Dict) -> str:
        """根据issue内容分类专家类型"""
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        text = f"{title} {body}"
        
        keywords = {
            'data_insight': ['data', 'analytics', 'metrics', 'statistics', 'analysis'],
            'business_strategy': ['strategy', 'roadmap', 'planning', 'business', 'market'],
            'user_insight': ['user', 'ux', 'ui', 'experience', 'usability', 'feedback'],
            'competitive_intelligence': ['competitor', 'comparison', 'benchmark', 'alternative'],
            'failure_prevention': ['bug', 'error', 'fail', 'crash', 'issue', 'problem']
        }
        
        scores = {}
        for expert_type, words in keywords.items():
            scores[expert_type] = sum(1 for word in words if word in text)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'business_strategy'
    
    def _extract_solution_from_issue(self, issue: Dict) -> str:
        """从issue中提取解决方案"""
        # 简化的解决方案提取
        body = issue.get('body', '')
        if len(body) > 100:
            return f"针对 '{issue['title']}' 的解决方案包括分析问题根因、制定解决策略、实施改进措施并验证效果。"
        return "需要进一步分析具体情况来制定合适的解决方案。"
    
    def _calculate_github_quality(self, issue: Dict) -> float:
        """计算GitHub issue的质量分数"""
        score = 0.5  # 基础分数
        
        # 根据评论数量调整
        comments = issue.get('comments', 0)
        if comments > 5:
            score += 0.2
        elif comments > 0:
            score += 0.1
        
        # 根据标签调整
        labels = issue.get('labels', [])
        if len(labels) > 0:
            score += 0.1
        
        # 根据内容长度调整
        body_length = len(issue.get('body', ''))
        if body_length > 200:
            score += 0.1
        
        return min(score, 1.0)
    
    def collect_all_data(self, target_total: int = 10000) -> List[Dict]:
        """收集所有数据源的数据"""
        logger.info(f"开始收集总计 {target_total} 条训练数据...")
        
        all_data = []
        
        # 1. 生成合成数据 (占70%)
        synthetic_count = int(target_total * 0.7)
        synthetic_data = self.generate_synthetic_data(synthetic_count)
        all_data.extend(synthetic_data)
        
        # 2. 收集GitHub数据 (占30%)
        github_count = target_total - len(all_data)
        if self.data_sources['github_issues']['enabled']:
            github_data = self.collect_github_data(github_count)
            all_data.extend(github_data)
        
        # 确保数据平衡
        balanced_data = self._balance_data(all_data, target_total)
        
        logger.info(f"总共收集了 {len(balanced_data)} 条数据")
        return balanced_data
    
    def _balance_data(self, data: List[Dict], target_total: int) -> List[Dict]:
        """平衡各专家类型的数据"""
        logger.info("开始平衡数据...")
        
        # 按专家类型分组
        grouped_data = {expert_type: [] for expert_type in self.expert_types}
        for item in data:
            expert_type = item['expert_type']
            if expert_type in grouped_data:
                grouped_data[expert_type].append(item)
        
        # 计算每种类型的目标数量
        per_type_target = target_total // len(self.expert_types)
        
        balanced_data = []
        for expert_type in self.expert_types:
            type_data = grouped_data[expert_type]
            
            if len(type_data) >= per_type_target:
                # 随机选择
                selected = random.sample(type_data, per_type_target)
            else:
                # 数据不足，重复采样
                selected = type_data.copy()
                while len(selected) < per_type_target:
                    selected.extend(random.choices(type_data, k=min(len(type_data), per_type_target - len(selected))))
            
            balanced_data.extend(selected[:per_type_target])
        
        # 打乱数据
        random.shuffle(balanced_data)
        
        logger.info(f"平衡后数据分布:")
        for expert_type in self.expert_types:
            count = sum(1 for item in balanced_data if item['expert_type'] == expert_type)
            logger.info(f"  {expert_type}: {count} 条")
        
        return balanced_data
    
    def save_data(self, data: List[Dict], filename: str = None) -> str:
        """保存收集的数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_train_data_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    collector = FreeDataCollector()
    
    # 收集10000条数据
    data = collector.collect_all_data(target_total=10000)
    
    # 保存数据
    filepath = collector.save_data(data)
    
    # 生成统计报告
    print("\n" + "="*60)
    print("数据收集完成报告")
    print("="*60)
    print(f"总数据量: {len(data)} 条")
    print(f"数据文件: {filepath}")
    
    # 统计各类型数量
    type_counts = {}
    for item in data:
        expert_type = item['expert_type']
        type_counts[expert_type] = type_counts.get(expert_type, 0) + 1
    
    print("\n专家类型分布:")
    for expert_type, count in type_counts.items():
        percentage = (count / len(data)) * 100
        print(f"  {expert_type}: {count} 条 ({percentage:.1f}%)")
    
    # 质量分数统计
    quality_scores = [item['quality_score'] for item in data]
    avg_quality = sum(quality_scores) / len(quality_scores)
    print(f"\n平均质量分数: {avg_quality:.3f}")
    
    print("\n🎉 数据收集完成！可以开始训练优化后的模型。")

if __name__ == "__main__":
    main()