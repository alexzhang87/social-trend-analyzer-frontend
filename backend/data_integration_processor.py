#!/usr/bin/env python3
"""
数据整合和预处理器
整合所有收集的数据，进行质量筛选、去重、格式化，生成最终训练数据集
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Set
import logging
from pathlib import Path
import re
from collections import defaultdict, Counter

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIntegrationProcessor:
    def __init__(self):
        self.collected_data_dir = Path("collected_data")
        self.output_dir = Path("final_training_data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 数据质量标准
        self.quality_standards = {
            'min_length': 20,           # 最小字符长度
            'max_length': 3000,         # 最大字符长度
            'min_quality_score': 0.6,   # 最低质量评分
            'required_fields': ['expert_type', 'question', 'answer', 'context', 'source']
        }
        
        # 专家类型标准化映射
        self.expert_type_mapping = {
            'data_insight': 'data_insight',
            'data_insights': 'data_insight',
            'failure_prevention': 'failure_prevention',
            'risk_prevention': 'failure_prevention',
            'business_strategy': 'business_strategy',
            'strategy': 'business_strategy',
            'competitive_intelligence': 'competitive_intelligence',
            'competition': 'competitive_intelligence',
            'user_insight': 'user_insight',
            'user_insights': 'user_insight',
            'customer_insight': 'user_insight'
        }
        
        # 处理统计
        self.processing_stats = {
            'total_raw_data': 0,
            'duplicates_removed': 0,
            'quality_filtered': 0,
            'final_training_data': 0,
            'expert_distribution': defaultdict(int),
            'source_distribution': defaultdict(int),
            'quality_distribution': defaultdict(int)
        }
        
        # 去重用的哈希集合
        self.seen_hashes: Set[str] = set()

    def load_all_collected_data(self) -> List[Dict]:
        """加载所有收集的数据"""
        logger.info("开始加载所有收集的数据...")
        
        all_data = []
        
        # 1. 加载综合收集的数据
        comprehensive_files = list(self.collected_data_dir.glob("comprehensive_training_*.json"))
        for file_path in comprehensive_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    logger.info(f"加载综合数据: {file_path.name} - {len(data)} 条")
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        
        # 2. 加载Hugging Face数据
        hf_dir = self.collected_data_dir / "huggingface"
        if hf_dir.exists():
            hf_files = list(hf_dir.glob("hf_training_data_*.json"))
            for file_path in hf_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.extend(data)
                        logger.info(f"加载HF数据: {file_path.name} - {len(data)} 条")
                except Exception as e:
                    logger.error(f"加载文件失败 {file_path}: {e}")
        
        # 3. 加载快速收集的数据
        quick_files = list(self.collected_data_dir.glob("quick/quick_training_*.json"))
        for file_path in quick_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    logger.info(f"加载快速数据: {file_path.name} - {len(data)} 条")
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        
        # 4. 加载目标数据源数据
        targeted_files = list(self.collected_data_dir.glob("targeted/targeted_training_*.json"))
        for file_path in targeted_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    logger.info(f"加载目标数据: {file_path.name} - {len(data)} 条")
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        
        # 5. 加载其他数据文件
        other_files = list(self.collected_data_dir.glob("**/training_data_*.json"))
        for file_path in other_files:
            # 避免重复加载已处理的文件
            if any(pattern in str(file_path) for pattern in ['comprehensive_training', 'hf_training_data', 'quick_training', 'targeted_training']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    logger.info(f"加载其他数据: {file_path.name} - {len(data)} 条")
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        
        self.processing_stats['total_raw_data'] = len(all_data)
        logger.info(f"总共加载数据: {len(all_data)} 条")
        
        return all_data

    def normalize_data_format(self, data_list: List[Dict]) -> List[Dict]:
        """标准化数据格式"""
        logger.info("开始标准化数据格式...")
        
        normalized_data = []
        
        for item in data_list:
            try:
                # 标准化专家类型
                expert_type = item.get('expert_type', 'business_strategy')
                expert_type = self.expert_type_mapping.get(expert_type, expert_type)
                
                # 确保必需字段存在
                normalized_item = {
                    'expert_type': expert_type,
                    'question': str(item.get('question', '')).strip(),
                    'answer': str(item.get('answer', '')).strip(),
                    'context': str(item.get('context', '')).strip(),
                    'source': str(item.get('source', 'unknown')).strip(),
                    'quality_score': float(item.get('quality_score', 0.7)),
                    'metadata': item.get('metadata', {}),
                    'created_at': item.get('created_at', datetime.now().isoformat())
                }
                
                # 添加唯一ID
                if 'id' not in item:
                    content_hash = self._generate_content_hash(normalized_item)
                    normalized_item['id'] = f"{expert_type}_{content_hash[:8]}_{self.timestamp}"
                else:
                    normalized_item['id'] = item['id']
                
                normalized_data.append(normalized_item)
                
            except Exception as e:
                logger.warning(f"标准化数据项失败: {e}")
                continue
        
        logger.info(f"数据格式标准化完成: {len(normalized_data)} 条")
        return normalized_data

    def remove_duplicates(self, data_list: List[Dict]) -> List[Dict]:
        """去除重复数据"""
        logger.info("开始去除重复数据...")
        
        unique_data = []
        
        for item in data_list:
            # 生成内容哈希
            content_hash = self._generate_content_hash(item)
            
            if content_hash not in self.seen_hashes:
                self.seen_hashes.add(content_hash)
                unique_data.append(item)
            else:
                self.processing_stats['duplicates_removed'] += 1
        
        logger.info(f"去重完成: 移除 {self.processing_stats['duplicates_removed']} 条重复数据")
        logger.info(f"剩余数据: {len(unique_data)} 条")
        
        return unique_data

    def filter_by_quality(self, data_list: List[Dict]) -> List[Dict]:
        """按质量标准筛选数据"""
        logger.info("开始质量筛选...")
        
        high_quality_data = []
        
        for item in data_list:
            if self._meets_quality_standards(item):
                high_quality_data.append(item)
                
                # 统计质量分布
                quality_score = item.get('quality_score', 0)
                if quality_score >= 0.9:
                    self.processing_stats['quality_distribution']['excellent'] += 1
                elif quality_score >= 0.8:
                    self.processing_stats['quality_distribution']['good'] += 1
                elif quality_score >= 0.7:
                    self.processing_stats['quality_distribution']['fair'] += 1
                else:
                    self.processing_stats['quality_distribution']['poor'] += 1
            else:
                self.processing_stats['quality_filtered'] += 1
        
        logger.info(f"质量筛选完成: 移除 {self.processing_stats['quality_filtered']} 条低质量数据")
        logger.info(f"高质量数据: {len(high_quality_data)} 条")
        
        return high_quality_data

    def balance_expert_types(self, data_list: List[Dict]) -> List[Dict]:
        """平衡专家类型分布"""
        logger.info("开始平衡专家类型分布...")
        
        # 按专家类型分组
        expert_groups = defaultdict(list)
        for item in data_list:
            expert_type = item['expert_type']
            expert_groups[expert_type].append(item)
        
        # 计算目标数量（以最少的类型为基准，但设置最小值）
        min_count = min(len(group) for group in expert_groups.values())
        target_count = max(min_count, 150)  # 每个专家类型至少150条
        
        balanced_data = []
        
        for expert_type, items in expert_groups.items():
            if len(items) <= target_count:
                # 如果数据不足，全部保留
                balanced_data.extend(items)
                self.processing_stats['expert_distribution'][expert_type] = len(items)
            else:
                # 如果数据过多，按质量评分排序后选择前target_count条
                sorted_items = sorted(items, key=lambda x: x.get('quality_score', 0), reverse=True)
                selected_items = sorted_items[:target_count]
                balanced_data.extend(selected_items)
                self.processing_stats['expert_distribution'][expert_type] = len(selected_items)
        
        logger.info(f"专家类型平衡完成: {len(balanced_data)} 条")
        for expert_type, count in self.processing_stats['expert_distribution'].items():
            logger.info(f"  {expert_type}: {count} 条")
        
        return balanced_data

    def enhance_training_data(self, data_list: List[Dict]) -> List[Dict]:
        """增强训练数据"""
        logger.info("开始增强训练数据...")
        
        enhanced_data = []
        
        for item in data_list:
            # 原始数据
            enhanced_data.append(item)
            
            # 为高质量数据生成变体
            if item.get('quality_score', 0) >= 0.85:
                variant = self._create_data_variant(item)
                if variant:
                    enhanced_data.append(variant)
        
        logger.info(f"数据增强完成: {len(enhanced_data)} 条 (增加了 {len(enhanced_data) - len(data_list)} 条变体)")
        
        return enhanced_data

    def _generate_content_hash(self, item: Dict) -> str:
        """生成内容哈希用于去重"""
        content = f"{item.get('question', '')}{item.get('answer', '')}{item.get('expert_type', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _meets_quality_standards(self, item: Dict) -> bool:
        """检查是否满足质量标准"""
        # 检查必需字段
        for field in self.quality_standards['required_fields']:
            if field not in item or not item[field]:
                return False
        
        # 检查长度
        question_len = len(item.get('question', ''))
        answer_len = len(item.get('answer', ''))
        
        if question_len < self.quality_standards['min_length'] or question_len > self.quality_standards['max_length']:
            return False
        
        if answer_len < self.quality_standards['min_length'] or answer_len > self.quality_standards['max_length']:
            return False
        
        # 检查质量评分
        quality_score = item.get('quality_score', 0)
        if quality_score < self.quality_standards['min_quality_score']:
            return False
        
        # 检查内容质量
        question = item.get('question', '')
        answer = item.get('answer', '')
        
        # 避免过于简单或重复的内容
        if len(set(question.split())) < 3 or len(set(answer.split())) < 5:
            return False
        
        return True

    def _create_data_variant(self, original_item: Dict) -> Dict:
        """创建数据变体"""
        try:
            variant = original_item.copy()
            
            # 修改问题表述
            original_question = original_item['question']
            
            # 简单的问题变体生成
            question_variants = [
                f"请分析一下：{original_question}",
                f"从专业角度，{original_question}",
                f"您如何看待这个问题：{original_question}",
                f"关于{original_question}，您的建议是什么？"
            ]
            
            variant['question'] = question_variants[hash(original_question) % len(question_variants)]
            variant['id'] = f"variant_{original_item['id']}"
            variant['quality_score'] = original_item.get('quality_score', 0.8) * 0.9  # 变体质量稍低
            variant['metadata'] = original_item.get('metadata', {}).copy()
            variant['metadata']['is_variant'] = True
            variant['metadata']['original_id'] = original_item['id']
            
            return variant
            
        except Exception as e:
            logger.warning(f"创建数据变体失败: {e}")
            return None

    def save_final_training_data(self, data_list: List[Dict]) -> Dict[str, str]:
        """保存最终训练数据"""
        logger.info("开始保存最终训练数据...")
        
        self.processing_stats['final_training_data'] = len(data_list)
        
        # 更新来源分布统计
        for item in data_list:
            source = item.get('source', 'unknown')
            self.processing_stats['source_distribution'][source] += 1
        
        # 保存完整训练数据
        training_file = self.output_dir / f"final_training_data_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        # 按专家类型分别保存
        expert_files = {}
        expert_groups = defaultdict(list)
        
        for item in data_list:
            expert_type = item['expert_type']
            expert_groups[expert_type].append(item)
        
        for expert_type, items in expert_groups.items():
            expert_file = self.output_dir / f"training_data_{expert_type}_{self.timestamp}.json"
            with open(expert_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            expert_files[expert_type] = str(expert_file)
        
        # 保存处理统计
        stats_file = self.output_dir / f"processing_stats_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            # 转换defaultdict为普通dict以便JSON序列化
            stats_dict = {
                'total_raw_data': self.processing_stats['total_raw_data'],
                'duplicates_removed': self.processing_stats['duplicates_removed'],
                'quality_filtered': self.processing_stats['quality_filtered'],
                'final_training_data': self.processing_stats['final_training_data'],
                'expert_distribution': dict(self.processing_stats['expert_distribution']),
                'source_distribution': dict(self.processing_stats['source_distribution']),
                'quality_distribution': dict(self.processing_stats['quality_distribution'])
            }
            json.dump(stats_dict, f, ensure_ascii=False, indent=2)
        
        # 生成处理报告
        report_file = self.output_dir / f"integration_report_{self.timestamp}.md"
        self._generate_integration_report(report_file, data_list)
        
        return {
            'training_file': str(training_file),
            'stats_file': str(stats_file),
            'report_file': str(report_file),
            'expert_files': expert_files
        }

    def _generate_integration_report(self, report_file: Path, data_list: List[Dict]):
        """生成数据整合报告"""
        
        report_content = f"""# 数据整合和预处理报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 处理概览
- 原始数据总量: {self.processing_stats['total_raw_data']} 条
- 去除重复数据: {self.processing_stats['duplicates_removed']} 条
- 质量筛选移除: {self.processing_stats['quality_filtered']} 条
- 最终训练数据: {self.processing_stats['final_training_data']} 条
- 数据保留率: {(self.processing_stats['final_training_data'] / self.processing_stats['total_raw_data'] * 100):.1f}%

## 专家类型分布
"""
        
        for expert_type, count in self.processing_stats['expert_distribution'].items():
            percentage = (count / self.processing_stats['final_training_data']) * 100
            report_content += f"- {expert_type}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 数据来源分布
"""
        
        for source, count in sorted(self.processing_stats['source_distribution'].items()):
            percentage = (count / self.processing_stats['final_training_data']) * 100
            report_content += f"- {source}: {count} 条 ({percentage:.1f}%)\n"
        
        report_content += f"""
## 质量分布
"""
        
        for quality_level, count in self.processing_stats['quality_distribution'].items():
            percentage = (count / self.processing_stats['final_training_data']) * 100
            report_content += f"- {quality_level}: {count} 条 ({percentage:.1f}%)\n"
        
        # 计算平均质量评分
        avg_quality = sum(item.get('quality_score', 0) for item in data_list) / len(data_list)
        
        report_content += f"""
## 数据质量指标
- 平均质量评分: {avg_quality:.3f}
- 高质量数据(>0.8): {len([item for item in data_list if item.get('quality_score', 0) > 0.8])} 条
- 优秀数据(>0.9): {len([item for item in data_list if item.get('quality_score', 0) > 0.9])} 条

## 处理步骤
1. ✅ 加载所有收集的数据文件
2. ✅ 标准化数据格式和字段
3. ✅ 去除重复数据
4. ✅ 按质量标准筛选
5. ✅ 平衡专家类型分布
6. ✅ 增强高质量数据
7. ✅ 保存最终训练数据集

## 数据文件
- 完整训练数据: `final_training_data_{self.timestamp}.json`
- 按专家类型分组的数据文件已生成
- 处理统计: `processing_stats_{self.timestamp}.json`

## 训练建议
1. 数据已经过质量筛选和去重，可直接用于训练
2. 建议使用分层抽样确保各专家类型平衡
3. 可根据质量评分进行加权训练
4. 建议定期更新和扩充训练数据

## 下一步
1. 配置模型训练参数
2. 启动模型训练
3. 监控训练过程和效果
4. 评估模型性能
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def run_integration_process(self) -> Dict[str, str]:
        """执行完整的数据整合流程"""
        logger.info("开始执行数据整合和预处理流程...")
        start_time = time.time()
        
        # 1. 加载所有数据
        all_data = self.load_all_collected_data()
        
        # 2. 标准化格式
        normalized_data = self.normalize_data_format(all_data)
        
        # 3. 去除重复
        unique_data = self.remove_duplicates(normalized_data)
        
        # 4. 质量筛选
        quality_data = self.filter_by_quality(unique_data)
        
        # 5. 平衡专家类型
        balanced_data = self.balance_expert_types(quality_data)
        
        # 6. 数据增强
        enhanced_data = self.enhance_training_data(balanced_data)
        
        # 7. 保存最终数据
        files = self.save_final_training_data(enhanced_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"数据整合流程完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"最终训练数据: {len(enhanced_data)} 条")
        logger.info(f"处理统计: {dict(self.processing_stats)}")
        
        return files

def main():
    """主函数"""
    processor = DataIntegrationProcessor()
    files = processor.run_integration_process()
    
    print(f"\n🔄 数据整合和预处理完成!")
    print(f"📁 最终训练数据: {files['training_file']}")
    print(f"📊 处理统计: {files['stats_file']}")
    print(f"📋 整合报告: {files['report_file']}")
    print(f"📂 专家类型文件: {len(files['expert_files'])} 个")
    print(f"📈 处理统计: {processor.processing_stats}")
    
    return files

if __name__ == "__main__":
    main()