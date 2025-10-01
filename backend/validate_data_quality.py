#!/usr/bin/env python3
"""
数据质量验证脚本
验证收集到的Product Hunt数据的质量和格式
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class DataQualityValidator:
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'files_validated': [],
            'overall_quality': 'unknown',
            'issues': [],
            'recommendations': []
        }
    
    def validate_product_hunt_data(self, file_path: str) -> Dict[str, Any]:
        """验证Product Hunt数据文件"""
        print(f"验证文件: {file_path}")
        
        if not os.path.exists(file_path):
            return {'error': f'文件不存在: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'无法读取JSON文件: {str(e)}'}
        
        validation_result = {
            'file_path': file_path,
            'total_records': len(data) if isinstance(data, list) else 1,
            'data_type': type(data).__name__,
            'required_fields_check': {},
            'data_quality_issues': [],
            'statistics': {}
        }
        
        if isinstance(data, list) and data:
            # 验证必需字段
            required_fields = ['id', 'name', 'tagline', 'url', 'votes', 'source', 'collected_at']
            sample_record = data[0]
            
            for field in required_fields:
                validation_result['required_fields_check'][field] = field in sample_record
                if field not in sample_record:
                    validation_result['data_quality_issues'].append(f'缺少必需字段: {field}')
            
            # 数据质量检查
            empty_names = sum(1 for item in data if not item.get('name', '').strip())
            empty_taglines = sum(1 for item in data if not item.get('tagline', '').strip())
            invalid_votes = sum(1 for item in data if not isinstance(item.get('votes'), int) or item.get('votes', 0) < 0)
            
            if empty_names > 0:
                validation_result['data_quality_issues'].append(f'{empty_names} 条记录缺少产品名称')
            
            if empty_taglines > 0:
                validation_result['data_quality_issues'].append(f'{empty_taglines} 条记录缺少产品标语')
            
            if invalid_votes > 0:
                validation_result['data_quality_issues'].append(f'{invalid_votes} 条记录投票数无效')
            
            # 统计信息
            votes = [item.get('votes', 0) for item in data if isinstance(item.get('votes'), int)]
            if votes:
                validation_result['statistics'] = {
                    'vote_range': {'min': min(votes), 'max': max(votes), 'avg': sum(votes) / len(votes)},
                    'products_with_high_votes': sum(1 for v in votes if v >= 100),
                    'products_with_comments': sum(1 for item in data if item.get('comments_count', 0) > 0)
                }
        
        return validation_result
    
    def validate_training_data(self, file_path: str) -> Dict[str, Any]:
        """验证训练数据格式"""
        print(f"验证训练数据: {file_path}")
        
        if not os.path.exists(file_path):
            return {'error': f'文件不存在: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'无法读取JSON文件: {str(e)}'}
        
        validation_result = {
            'file_path': file_path,
            'total_records': len(data) if isinstance(data, list) else 1,
            'training_format_check': {},
            'quality_issues': [],
            'text_statistics': {}
        }
        
        if isinstance(data, list) and data:
            # 验证训练数据格式
            required_training_fields = ['text', 'metadata', 'quality_score', 'category', 'type']
            sample_record = data[0]
            
            for field in required_training_fields:
                validation_result['training_format_check'][field] = field in sample_record
                if field not in sample_record:
                    validation_result['quality_issues'].append(f'缺少训练数据字段: {field}')
            
            # 文本质量检查
            empty_texts = sum(1 for item in data if not item.get('text', '').strip())
            short_texts = sum(1 for item in data if len(item.get('text', '')) < 10)
            
            if empty_texts > 0:
                validation_result['quality_issues'].append(f'{empty_texts} 条记录文本为空')
            
            if short_texts > 0:
                validation_result['quality_issues'].append(f'{short_texts} 条记录文本过短（<10字符）')
            
            # 文本统计
            text_lengths = [len(item.get('text', '')) for item in data]
            if text_lengths:
                validation_result['text_statistics'] = {
                    'length_range': {'min': min(text_lengths), 'max': max(text_lengths), 'avg': sum(text_lengths) / len(text_lengths)},
                    'categories': list(set(item.get('category', 'unknown') for item in data)),
                    'types': list(set(item.get('type', 'unknown') for item in data))
                }
        
        return validation_result
    
    def validate_stats_data(self, file_path: str) -> Dict[str, Any]:
        """验证统计数据"""
        print(f"验证统计数据: {file_path}")
        
        if not os.path.exists(file_path):
            return {'error': f'文件不存在: {file_path}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'无法读取JSON文件: {str(e)}'}
        
        validation_result = {
            'file_path': file_path,
            'stats_completeness': {},
            'data_consistency': []
        }
        
        # 验证统计数据完整性
        expected_stats = ['collection_date', 'total_products_fetched', 'filtered_products', 'vote_statistics', 'top_products']
        
        for stat in expected_stats:
            validation_result['stats_completeness'][stat] = stat in data
            if stat not in data:
                validation_result['data_consistency'].append(f'缺少统计字段: {stat}')
        
        # 数据一致性检查
        if 'total_products_fetched' in data and 'filtered_products' in data:
            if data['total_products_fetched'] < data['filtered_products']:
                validation_result['data_consistency'].append('过滤后产品数大于总产品数，数据不一致')
        
        return validation_result
    
    def run_validation(self, data_dir: str = "collected_data"):
        """运行完整的数据质量验证"""
        print("=== 开始数据质量验证 ===")
        
        # 查找最新的Product Hunt数据文件
        files_to_validate = []
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.startswith('product_hunt_latest_') and filename.endswith('.json'):
                    files_to_validate.append(os.path.join(data_dir, filename))
        
        if not files_to_validate:
            print("❌ 未找到Product Hunt数据文件")
            return
        
        # 按文件类型分组
        raw_files = [f for f in files_to_validate if '_raw_' in f]
        training_files = [f for f in files_to_validate if '_training_' in f]
        stats_files = [f for f in files_to_validate if '_stats_' in f]
        
        # 验证原始数据
        for file_path in raw_files:
            result = self.validate_product_hunt_data(file_path)
            self.validation_results['files_validated'].append(result)
            
            if 'error' in result:
                self.validation_results['issues'].append(f"原始数据错误: {result['error']}")
            elif result.get('data_quality_issues'):
                self.validation_results['issues'].extend([f"原始数据: {issue}" for issue in result['data_quality_issues']])
        
        # 验证训练数据
        for file_path in training_files:
            result = self.validate_training_data(file_path)
            self.validation_results['files_validated'].append(result)
            
            if 'error' in result:
                self.validation_results['issues'].append(f"训练数据错误: {result['error']}")
            elif result.get('quality_issues'):
                self.validation_results['issues'].extend([f"训练数据: {issue}" for issue in result['quality_issues']])
        
        # 验证统计数据
        for file_path in stats_files:
            result = self.validate_stats_data(file_path)
            self.validation_results['files_validated'].append(result)
            
            if 'error' in result:
                self.validation_results['issues'].append(f"统计数据错误: {result['error']}")
            elif result.get('data_consistency'):
                self.validation_results['issues'].extend([f"统计数据: {issue}" for issue in result['data_consistency']])
        
        # 评估整体质量
        if not self.validation_results['issues']:
            self.validation_results['overall_quality'] = 'excellent'
            self.validation_results['recommendations'].append('数据质量优秀，可以直接用于分析和训练')
        elif len(self.validation_results['issues']) <= 2:
            self.validation_results['overall_quality'] = 'good'
            self.validation_results['recommendations'].append('数据质量良好，建议修复少量问题后使用')
        else:
            self.validation_results['overall_quality'] = 'needs_improvement'
            self.validation_results['recommendations'].append('数据质量需要改进，建议重新收集或清理数据')
        
        # 保存验证报告
        report_path = os.path.join(data_dir, f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 数据质量验证完成 ===")
        print(f"验证文件数: {len(self.validation_results['files_validated'])}")
        print(f"整体质量: {self.validation_results['overall_quality']}")
        print(f"发现问题: {len(self.validation_results['issues'])}")
        
        if self.validation_results['issues']:
            print("\n问题列表:")
            for issue in self.validation_results['issues']:
                print(f"  ❌ {issue}")
        
        print(f"\n建议:")
        for rec in self.validation_results['recommendations']:
            print(f"  💡 {rec}")
        
        print(f"\n验证报告已保存: {report_path}")
        
        return self.validation_results

if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.run_validation()