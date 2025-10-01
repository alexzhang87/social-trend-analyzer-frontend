#!/usr/bin/env python3
"""
数据质量验证器
对最终训练数据集进行深度质量检查和验证
"""

import os
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path
from collections import defaultdict, Counter
import statistics

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityValidator:
    def __init__(self):
        self.final_data_dir = Path("final_training_data")
        self.validation_dir = Path("validation_results")
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 质量检查标准
        self.quality_checks = {
            'content_diversity': {
                'min_unique_words_ratio': 0.3,  # 最小独特词汇比例
                'max_repetition_ratio': 0.7     # 最大重复内容比例
            },
            'language_quality': {
                'min_sentence_length': 5,       # 最小句子长度
                'max_sentence_length': 200,     # 最大句子长度
                'min_sentences_per_answer': 2   # 答案最少句子数
            },
            'expert_consistency': {
                'min_expert_specific_terms': 2,  # 最少专业术语数量
                'context_relevance_threshold': 0.7  # 上下文相关性阈值
            },
            'format_compliance': {
                'required_fields': ['expert_type', 'question', 'answer', 'context', 'source'],
                'field_completeness_threshold': 0.95  # 字段完整性阈值
            }
        }
        
        # 专家类型关键词
        self.expert_keywords = {
            'data_insight': [
                '数据分析', '数据挖掘', '统计', '指标', '趋势', '预测', '模型', 
                '算法', '机器学习', '可视化', '报表', '洞察', '分析', '数据'
            ],
            'business_strategy': [
                '战略', '策略', '商业模式', '竞争', '市场', '增长', '盈利', 
                '运营', '管理', '决策', '规划', '目标', '执行', '优化'
            ],
            'user_insight': [
                '用户', '客户', '体验', '需求', '痛点', '行为', '反馈', 
                '满意度', '留存', '转化', '画像', '调研', '访谈', '观察'
            ],
            'competitive_intelligence': [
                '竞争对手', '市场分析', '竞争优势', '差异化', '定位', '威胁', 
                '机会', '行业', '市场份额', '竞争策略', '对标', '分析'
            ],
            'failure_prevention': [
                '风险', '失败', '预防', '规避', '控制', '管理', '识别', 
                '评估', '应对', '缓解', '监控', '预警', '危机', '问题'
            ]
        }
        
        # 验证结果
        self.validation_results = {
            'total_samples': 0,
            'passed_samples': 0,
            'failed_samples': 0,
            'quality_scores': [],
            'expert_type_quality': defaultdict(list),
            'source_quality': defaultdict(list),
            'detailed_issues': defaultdict(list),
            'recommendations': []
        }

    def load_training_data(self) -> List[Dict]:
        """加载最终训练数据"""
        logger.info("加载最终训练数据...")
        
        # 查找最新的训练数据文件
        training_files = list(self.final_data_dir.glob("final_training_data_*.json"))
        if not training_files:
            raise FileNotFoundError("未找到最终训练数据文件")
        
        # 选择最新的文件
        latest_file = max(training_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"加载文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"加载数据: {len(data)} 条")
        return data

    def validate_content_diversity(self, data_list: List[Dict]) -> Dict[str, Any]:
        """验证内容多样性"""
        logger.info("验证内容多样性...")
        
        diversity_results = {
            'unique_words_ratios': [],
            'repetition_ratios': [],
            'vocabulary_size': 0,
            'average_content_length': 0,
            'diversity_score': 0
        }
        
        all_words = set()
        total_words = 0
        content_lengths = []
        
        for item in data_list:
            # 分析问题和答案的词汇多样性
            question = item.get('question', '')
            answer = item.get('answer', '')
            content = f"{question} {answer}"
            
            words = re.findall(r'\b\w+\b', content.lower())
            unique_words = set(words)
            
            if len(words) > 0:
                unique_ratio = len(unique_words) / len(words)
                diversity_results['unique_words_ratios'].append(unique_ratio)
            
            all_words.update(unique_words)
            total_words += len(words)
            content_lengths.append(len(content))
        
        diversity_results['vocabulary_size'] = len(all_words)
        diversity_results['average_content_length'] = statistics.mean(content_lengths) if content_lengths else 0
        diversity_results['diversity_score'] = len(all_words) / total_words if total_words > 0 else 0
        
        return diversity_results

    def validate_language_quality(self, data_list: List[Dict]) -> Dict[str, Any]:
        """验证语言质量"""
        logger.info("验证语言质量...")
        
        language_results = {
            'sentence_length_distribution': [],
            'sentences_per_answer': [],
            'grammar_issues': 0,
            'clarity_score': 0,
            'readability_score': 0
        }
        
        for item in data_list:
            question = item.get('question', '')
            answer = item.get('answer', '')
            
            # 分析句子长度
            question_sentences = re.split(r'[.!?。！？]', question)
            answer_sentences = re.split(r'[.!?。！？]', answer)
            
            for sentence in question_sentences + answer_sentences:
                if sentence.strip():
                    length = len(sentence.strip())
                    language_results['sentence_length_distribution'].append(length)
            
            # 统计答案句子数
            valid_answer_sentences = [s for s in answer_sentences if s.strip()]
            language_results['sentences_per_answer'].append(len(valid_answer_sentences))
            
            # 简单的语法检查（检查是否有基本的标点符号）
            if not re.search(r'[.!?。！？]', answer):
                language_results['grammar_issues'] += 1
        
        # 计算平均分数
        if language_results['sentence_length_distribution']:
            avg_length = statistics.mean(language_results['sentence_length_distribution'])
            language_results['clarity_score'] = min(1.0, avg_length / 50)  # 标准化到0-1
        
        if language_results['sentences_per_answer']:
            avg_sentences = statistics.mean(language_results['sentences_per_answer'])
            language_results['readability_score'] = min(1.0, avg_sentences / 5)  # 标准化到0-1
        
        return language_results

    def validate_expert_consistency(self, data_list: List[Dict]) -> Dict[str, Any]:
        """验证专家一致性"""
        logger.info("验证专家一致性...")
        
        consistency_results = {
            'expert_term_coverage': defaultdict(int),
            'context_relevance_scores': [],
            'misclassified_samples': [],
            'consistency_score': 0
        }
        
        for item in data_list:
            expert_type = item.get('expert_type', '')
            question = item.get('question', '').lower()
            answer = item.get('answer', '').lower()
            context = item.get('context', '').lower()
            
            content = f"{question} {answer} {context}"
            
            # 检查专家类型相关关键词
            if expert_type in self.expert_keywords:
                keywords = self.expert_keywords[expert_type]
                found_keywords = sum(1 for keyword in keywords if keyword in content)
                consistency_results['expert_term_coverage'][expert_type] += found_keywords
                
                # 计算相关性得分
                relevance_score = found_keywords / len(keywords)
                consistency_results['context_relevance_scores'].append(relevance_score)
                
                # 检查是否可能分类错误
                if relevance_score < self.quality_checks['expert_consistency']['context_relevance_threshold']:
                    consistency_results['misclassified_samples'].append({
                        'id': item.get('id', ''),
                        'expert_type': expert_type,
                        'relevance_score': relevance_score,
                        'found_keywords': found_keywords
                    })
        
        # 计算整体一致性得分
        if consistency_results['context_relevance_scores']:
            consistency_results['consistency_score'] = statistics.mean(consistency_results['context_relevance_scores'])
        
        return consistency_results

    def validate_format_compliance(self, data_list: List[Dict]) -> Dict[str, Any]:
        """验证格式合规性"""
        logger.info("验证格式合规性...")
        
        format_results = {
            'field_completeness': defaultdict(int),
            'missing_fields': [],
            'invalid_formats': [],
            'compliance_score': 0
        }
        
        required_fields = self.quality_checks['format_compliance']['required_fields']
        
        for item in data_list:
            item_issues = []
            
            # 检查必需字段
            for field in required_fields:
                if field in item and item[field]:
                    format_results['field_completeness'][field] += 1
                else:
                    item_issues.append(f"缺失字段: {field}")
            
            # 检查数据类型
            if 'quality_score' in item:
                try:
                    score = float(item['quality_score'])
                    if not (0 <= score <= 1):
                        item_issues.append("质量评分超出范围 [0,1]")
                except (ValueError, TypeError):
                    item_issues.append("质量评分格式错误")
            
            # 检查专家类型是否有效
            expert_type = item.get('expert_type', '')
            if expert_type not in self.expert_keywords:
                item_issues.append(f"无效的专家类型: {expert_type}")
            
            if item_issues:
                format_results['invalid_formats'].append({
                    'id': item.get('id', ''),
                    'issues': item_issues
                })
        
        # 计算合规性得分
        total_samples = len(data_list)
        if total_samples > 0:
            completeness_scores = []
            for field in required_fields:
                completeness = format_results['field_completeness'][field] / total_samples
                completeness_scores.append(completeness)
            
            format_results['compliance_score'] = statistics.mean(completeness_scores)
        
        return format_results

    def calculate_overall_quality_score(self, item: Dict, diversity_results: Dict, 
                                      language_results: Dict, consistency_results: Dict) -> float:
        """计算单个样本的综合质量评分"""
        
        scores = []
        
        # 内容多样性得分 (25%)
        content = f"{item.get('question', '')} {item.get('answer', '')}"
        words = re.findall(r'\b\w+\b', content.lower())
        if words:
            unique_ratio = len(set(words)) / len(words)
            diversity_score = min(1.0, unique_ratio / 0.5)  # 标准化
            scores.append(diversity_score * 0.25)
        
        # 语言质量得分 (25%)
        answer = item.get('answer', '')
        sentences = re.split(r'[.!?。！？]', answer)
        valid_sentences = [s for s in sentences if s.strip()]
        if valid_sentences:
            avg_sentence_length = statistics.mean([len(s.strip()) for s in valid_sentences])
            language_score = min(1.0, avg_sentence_length / 50)
            scores.append(language_score * 0.25)
        
        # 专家一致性得分 (30%)
        expert_type = item.get('expert_type', '')
        if expert_type in self.expert_keywords:
            content_lower = content.lower()
            keywords = self.expert_keywords[expert_type]
            found_keywords = sum(1 for keyword in keywords if keyword in content_lower)
            consistency_score = min(1.0, found_keywords / len(keywords) * 2)
            scores.append(consistency_score * 0.30)
        
        # 原始质量评分 (20%)
        original_score = item.get('quality_score', 0.7)
        scores.append(original_score * 0.20)
        
        return sum(scores)

    def generate_recommendations(self, validation_results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于多样性结果的建议
        diversity = validation_results.get('diversity', {})
        if diversity.get('diversity_score', 0) < 0.3:
            recommendations.append("建议增加内容多样性，扩充词汇表和表达方式")
        
        # 基于语言质量的建议
        language = validation_results.get('language', {})
        if language.get('grammar_issues', 0) > len(validation_results.get('data', [])) * 0.1:
            recommendations.append("建议改进语言质量，检查语法和标点符号")
        
        # 基于专家一致性的建议
        consistency = validation_results.get('consistency', {})
        if consistency.get('consistency_score', 0) < 0.7:
            recommendations.append("建议提高专家类型一致性，确保内容与专家类型匹配")
        
        # 基于格式合规性的建议
        format_compliance = validation_results.get('format', {})
        if format_compliance.get('compliance_score', 0) < 0.95:
            recommendations.append("建议完善数据格式，确保所有必需字段完整")
        
        # 基于质量分布的建议
        quality_scores = validation_results.get('quality_scores', [])
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            if avg_quality < 0.8:
                recommendations.append("建议提高整体数据质量，筛选更高质量的训练样本")
        
        return recommendations

    def run_validation(self) -> Dict[str, Any]:
        """执行完整的数据质量验证"""
        logger.info("开始执行数据质量验证...")
        start_time = time.time()
        
        # 加载数据
        data_list = self.load_training_data()
        self.validation_results['total_samples'] = len(data_list)
        
        # 执行各项验证
        diversity_results = self.validate_content_diversity(data_list)
        language_results = self.validate_language_quality(data_list)
        consistency_results = self.validate_expert_consistency(data_list)
        format_results = self.validate_format_compliance(data_list)
        
        # 计算每个样本的质量评分
        for item in data_list:
            quality_score = self.calculate_overall_quality_score(
                item, diversity_results, language_results, consistency_results
            )
            self.validation_results['quality_scores'].append(quality_score)
            
            # 按专家类型和来源分组统计
            expert_type = item.get('expert_type', 'unknown')
            source = item.get('source', 'unknown')
            self.validation_results['expert_type_quality'][expert_type].append(quality_score)
            self.validation_results['source_quality'][source].append(quality_score)
            
            # 判断是否通过验证
            if quality_score >= 0.7:  # 质量阈值
                self.validation_results['passed_samples'] += 1
            else:
                self.validation_results['failed_samples'] += 1
        
        # 生成改进建议
        validation_summary = {
            'diversity': diversity_results,
            'language': language_results,
            'consistency': consistency_results,
            'format': format_results,
            'quality_scores': self.validation_results['quality_scores'],
            'data': data_list
        }
        
        self.validation_results['recommendations'] = self.generate_recommendations(validation_summary)
        
        # 保存验证结果
        self.save_validation_results(validation_summary)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"数据质量验证完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"通过验证: {self.validation_results['passed_samples']}/{self.validation_results['total_samples']}")
        
        return self.validation_results

    def save_validation_results(self, validation_summary: Dict):
        """保存验证结果"""
        
        # 保存详细验证结果
        results_file = self.validation_dir / f"validation_results_{self.timestamp}.json"
        
        # 准备可序列化的结果
        serializable_results = {
            'validation_summary': {
                'diversity': validation_summary['diversity'],
                'language': validation_summary['language'],
                'consistency': dict(validation_summary['consistency']),  # 转换defaultdict
                'format': dict(validation_summary['format'])
            },
            'validation_results': {
                'total_samples': self.validation_results['total_samples'],
                'passed_samples': self.validation_results['passed_samples'],
                'failed_samples': self.validation_results['failed_samples'],
                'quality_scores': self.validation_results['quality_scores'],
                'expert_type_quality': dict(self.validation_results['expert_type_quality']),
                'source_quality': dict(self.validation_results['source_quality']),
                'recommendations': self.validation_results['recommendations']
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        # 生成验证报告
        report_file = self.validation_dir / f"validation_report_{self.timestamp}.md"
        self.generate_validation_report(report_file, validation_summary)
        
        logger.info(f"验证结果已保存: {results_file}")
        logger.info(f"验证报告已生成: {report_file}")

    def generate_validation_report(self, report_file: Path, validation_summary: Dict):
        """生成验证报告"""
        
        quality_scores = self.validation_results['quality_scores']
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0
        
        report_content = f"""# 数据质量验证报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 验证概览
- 总样本数: {self.validation_results['total_samples']}
- 通过验证: {self.validation_results['passed_samples']} ({self.validation_results['passed_samples']/self.validation_results['total_samples']*100:.1f}%)
- 未通过验证: {self.validation_results['failed_samples']} ({self.validation_results['failed_samples']/self.validation_results['total_samples']*100:.1f}%)
- 平均质量评分: {avg_quality:.3f}

## 内容多样性分析
- 词汇表大小: {validation_summary['diversity']['vocabulary_size']}
- 平均内容长度: {validation_summary['diversity']['average_content_length']:.1f} 字符
- 多样性得分: {validation_summary['diversity']['diversity_score']:.3f}

## 语言质量分析
- 语法问题数量: {validation_summary['language']['grammar_issues']}
- 清晰度得分: {validation_summary['language']['clarity_score']:.3f}
- 可读性得分: {validation_summary['language']['readability_score']:.3f}

## 专家一致性分析
- 一致性得分: {validation_summary['consistency']['consistency_score']:.3f}
- 可能分类错误样本: {len(validation_summary['consistency']['misclassified_samples'])}

## 格式合规性分析
- 合规性得分: {validation_summary['format']['compliance_score']:.3f}
- 格式错误样本: {len(validation_summary['format']['invalid_formats'])}

## 专家类型质量分布
"""
        
        for expert_type, scores in self.validation_results['expert_type_quality'].items():
            if scores:
                avg_score = statistics.mean(scores)
                report_content += f"- {expert_type}: {avg_score:.3f} (样本数: {len(scores)})\n"
        
        report_content += f"""
## 数据来源质量分布
"""
        
        for source, scores in self.validation_results['source_quality'].items():
            if scores:
                avg_score = statistics.mean(scores)
                report_content += f"- {source}: {avg_score:.3f} (样本数: {len(scores)})\n"
        
        report_content += f"""
## 改进建议
"""
        
        for i, recommendation in enumerate(self.validation_results['recommendations'], 1):
            report_content += f"{i}. {recommendation}\n"
        
        report_content += f"""
## 质量等级分布
"""
        
        excellent = len([s for s in quality_scores if s >= 0.9])
        good = len([s for s in quality_scores if 0.8 <= s < 0.9])
        fair = len([s for s in quality_scores if 0.7 <= s < 0.8])
        poor = len([s for s in quality_scores if s < 0.7])
        
        report_content += f"""- 优秀 (≥0.9): {excellent} 条 ({excellent/len(quality_scores)*100:.1f}%)
- 良好 (0.8-0.9): {good} 条 ({good/len(quality_scores)*100:.1f}%)
- 一般 (0.7-0.8): {fair} 条 ({fair/len(quality_scores)*100:.1f}%)
- 较差 (<0.7): {poor} 条 ({poor/len(quality_scores)*100:.1f}%)

## 训练建议
1. 数据质量整体{('良好' if avg_quality >= 0.8 else '一般' if avg_quality >= 0.7 else '需要改进')}，建议{'直接用于训练' if avg_quality >= 0.8 else '进一步筛选后训练'}
2. 重点关注质量评分较低的专家类型和数据来源
3. 建议实施质量加权训练策略
4. 定期进行数据质量监控和改进

## 验证结论
{'✅ 数据质量符合训练要求' if avg_quality >= 0.8 else '⚠️ 数据质量需要进一步改进' if avg_quality >= 0.7 else '❌ 数据质量不符合训练要求'}
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

def main():
    """主函数"""
    validator = DataQualityValidator()
    results = validator.run_validation()
    
    print(f"\n🔍 数据质量验证完成!")
    print(f"📊 总样本数: {results['total_samples']}")
    print(f"✅ 通过验证: {results['passed_samples']}")
    print(f"❌ 未通过验证: {results['failed_samples']}")
    print(f"📈 平均质量评分: {statistics.mean(results['quality_scores']):.3f}")
    print(f"💡 改进建议数: {len(results['recommendations'])}")
    
    return results

if __name__ == "__main__":
    main()