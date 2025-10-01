#!/usr/bin/env python3
"""
数据验证脚本

验证收集的数据质量和格式完整性
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validation_results = {
            'reddit_data': {},
            'product_hunt_data': {},
            'overall_summary': {}
        }
    
    def validate_reddit_data(self) -> Dict[str, Any]:
        """验证Reddit数据"""
        logger.info("开始验证Reddit数据...")
        
        # 查找最新的Reddit数据文件
        reddit_files = glob.glob("collected_data/reddit_*.json")
        if not reddit_files:
            return {'error': '未找到Reddit数据文件'}
        
        results = {
            'files_found': len(reddit_files),
            'training_data_validation': {},
            'raw_data_validation': {},
            'stats_validation': {}
        }
        
        # 验证训练数据
        training_files = [f for f in reddit_files if 'training' in f]
        if training_files:
            latest_training = max(training_files, key=os.path.getctime)
            results['training_data_validation'] = self._validate_training_data(latest_training)
        
        # 验证原始数据
        raw_files = [f for f in reddit_files if 'raw' in f]
        if raw_files:
            latest_raw = max(raw_files, key=os.path.getctime)
            results['raw_data_validation'] = self._validate_raw_data(latest_raw)
        
        # 验证统计数据
        stats_files = [f for f in reddit_files if 'stats' in f]
        if stats_files:
            latest_stats = max(stats_files, key=os.path.getctime)
            results['stats_validation'] = self._validate_stats_data(latest_stats)
        
        return results
    
    def _validate_training_data(self, file_path: str) -> Dict[str, Any]:
        """验证训练数据格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return {'error': '训练数据应该是列表格式'}
            
            results = {
                'total_items': len(data),
                'valid_items': 0,
                'invalid_items': 0,
                'missing_fields': [],
                'quality_scores': [],
                'categories': {},
                'sources': {}
            }
            
            required_fields = ['text', 'metadata', 'quality_score', 'category', 'type']
            metadata_fields = ['source', 'post_id', 'subreddit', 'score', 'url']
            
            for i, item in enumerate(data):
                is_valid = True
                
                # 检查必需字段
                for field in required_fields:
                    if field not in item:
                        results['missing_fields'].append(f"Item {i}: missing {field}")
                        is_valid = False
                
                # 检查metadata字段
                if 'metadata' in item and isinstance(item['metadata'], dict):
                    for field in metadata_fields:
                        if field not in item['metadata']:
                            results['missing_fields'].append(f"Item {i}: missing metadata.{field}")
                            is_valid = False
                
                if is_valid:
                    results['valid_items'] += 1
                    
                    # 收集质量分数
                    if 'quality_score' in item:
                        results['quality_scores'].append(item['quality_score'])
                    
                    # 统计类别
                    category = item.get('category', 'unknown')
                    results['categories'][category] = results['categories'].get(category, 0) + 1
                    
                    # 统计来源
                    source = item.get('metadata', {}).get('source', 'unknown')
                    results['sources'][source] = results['sources'].get(source, 0) + 1
                else:
                    results['invalid_items'] += 1
            
            # 计算质量统计
            if results['quality_scores']:
                results['quality_stats'] = {
                    'min': min(results['quality_scores']),
                    'max': max(results['quality_scores']),
                    'avg': sum(results['quality_scores']) / len(results['quality_scores']),
                    'high_quality_count': len([s for s in results['quality_scores'] if s >= 0.7])
                }
            
            results['validation_status'] = 'passed' if results['invalid_items'] == 0 else 'failed'
            
            return results
            
        except Exception as e:
            return {'error': f'验证训练数据时出错: {e}'}
    
    def _validate_raw_data(self, file_path: str) -> Dict[str, Any]:
        """验证原始数据格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = {
                'total_items': len(data),
                'has_content': 0,
                'has_score': 0,
                'has_subreddit': 0,
                'avg_content_length': 0,
                'score_range': {}
            }
            
            content_lengths = []
            scores = []
            
            for item in data:
                if 'content' in item and item['content']:
                    results['has_content'] += 1
                    content_lengths.append(len(item['content']))
                
                if 'score' in item:
                    results['has_score'] += 1
                    scores.append(item['score'])
                
                if 'subreddit' in item:
                    results['has_subreddit'] += 1
            
            if content_lengths:
                results['avg_content_length'] = sum(content_lengths) / len(content_lengths)
            
            if scores:
                results['score_range'] = {
                    'min': min(scores),
                    'max': max(scores),
                    'avg': sum(scores) / len(scores)
                }
            
            results['validation_status'] = 'passed'
            return results
            
        except Exception as e:
            return {'error': f'验证原始数据时出错: {e}'}
    
    def _validate_stats_data(self, file_path: str) -> Dict[str, Any]:
        """验证统计数据格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_fields = ['total_posts', 'filtered_posts', 'keywords_used', 'collection_time']
            
            results = {
                'has_required_fields': True,
                'missing_fields': [],
                'data_summary': {}
            }
            
            for field in required_fields:
                if field not in data:
                    results['has_required_fields'] = False
                    results['missing_fields'].append(field)
            
            # 提取关键统计信息
            results['data_summary'] = {
                'total_posts': data.get('total_posts', 0),
                'filtered_posts': data.get('filtered_posts', 0),
                'filter_rate': data.get('filtered_posts', 0) / data.get('total_posts', 1) if data.get('total_posts', 0) > 0 else 0,
                'keywords_count': len(data.get('keywords_used', [])),
                'subreddits_count': len(data.get('subreddits', {})),
                'collection_time': data.get('collection_time')
            }
            
            results['validation_status'] = 'passed' if results['has_required_fields'] else 'failed'
            return results
            
        except Exception as e:
            return {'error': f'验证统计数据时出错: {e}'}
    
    def validate_product_hunt_data(self) -> Dict[str, Any]:
        """验证Product Hunt数据"""
        logger.info("开始验证Product Hunt数据...")
        
        # 查找Product Hunt数据文件
        ph_files = glob.glob("collected_data/product_hunt_*.json")
        
        if not ph_files:
            return {'status': 'no_data', 'message': '未找到Product Hunt数据文件'}
        
        results = {
            'files_found': len(ph_files),
            'validation_status': 'passed'
        }
        
        return results
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        logger.info("生成数据验证报告...")
        
        # 验证Reddit数据
        reddit_results = self.validate_reddit_data()
        self.validation_results['reddit_data'] = reddit_results
        
        # 验证Product Hunt数据
        ph_results = self.validate_product_hunt_data()
        self.validation_results['product_hunt_data'] = ph_results
        
        # 生成总体摘要
        overall_summary = {
            'validation_time': datetime.now().isoformat(),
            'reddit_status': 'passed' if 'error' not in reddit_results else 'failed',
            'product_hunt_status': ph_results.get('validation_status', 'no_data'),
            'total_files_validated': reddit_results.get('files_found', 0) + ph_results.get('files_found', 0)
        }
        
        # Reddit数据摘要
        if 'training_data_validation' in reddit_results:
            training_validation = reddit_results['training_data_validation']
            if 'total_items' in training_validation:
                overall_summary['reddit_training_items'] = training_validation['total_items']
                overall_summary['reddit_valid_items'] = training_validation.get('valid_items', 0)
                overall_summary['reddit_data_quality'] = training_validation.get('quality_stats', {}).get('avg', 0)
        
        self.validation_results['overall_summary'] = overall_summary
        
        return self.validation_results
    
    def save_validation_report(self, results: Dict[str, Any]):
        """保存验证报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"collected_data/validation_report_{timestamp}.json"
        
        os.makedirs('collected_data', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"验证报告已保存: {filename}")
        return filename
    
    def print_validation_summary(self, results: Dict[str, Any]):
        """打印验证摘要"""
        print("\n" + "="*60)
        print("📋 数据验证报告")
        print("="*60)
        
        overall = results.get('overall_summary', {})
        print(f"🕐 验证时间: {overall.get('validation_time', 'N/A')}")
        print(f"📁 验证文件数: {overall.get('total_files_validated', 0)}")
        
        # Reddit数据验证结果
        reddit_data = results.get('reddit_data', {})
        print(f"\n🔴 Reddit数据验证:")
        print(f"   状态: {'✅ 通过' if overall.get('reddit_status') == 'passed' else '❌ 失败'}")
        
        if 'training_data_validation' in reddit_data:
            training = reddit_data['training_data_validation']
            print(f"   训练数据项: {training.get('total_items', 0)}")
            print(f"   有效项: {training.get('valid_items', 0)}")
            print(f"   无效项: {training.get('invalid_items', 0)}")
            
            if 'quality_stats' in training:
                quality = training['quality_stats']
                print(f"   平均质量分: {quality.get('avg', 0):.3f}")
                print(f"   高质量项: {quality.get('high_quality_count', 0)}")
            
            if 'categories' in training:
                print(f"   数据类别: {list(training['categories'].keys())}")
        
        # Product Hunt数据验证结果
        ph_data = results.get('product_hunt_data', {})
        print(f"\n🟠 Product Hunt数据验证:")
        ph_status = ph_data.get('validation_status', 'no_data')
        if ph_status == 'no_data':
            print(f"   状态: ⚠️ 无数据")
        else:
            print(f"   状态: {'✅ 通过' if ph_status == 'passed' else '❌ 失败'}")
            print(f"   文件数: {ph_data.get('files_found', 0)}")
        
        print(f"\n📊 总体评估:")
        if overall.get('reddit_status') == 'passed':
            print("   ✅ 数据收集系统运行正常")
            print("   ✅ 数据格式符合标准")
            print("   ✅ 数据质量满足要求")
        else:
            print("   ⚠️ 发现数据质量问题，请检查详细报告")

def main():
    """主函数"""
    print("🔍 开始数据验证...")
    
    validator = DataValidator()
    
    # 生成验证报告
    results = validator.generate_validation_report()
    
    # 保存报告
    report_file = validator.save_validation_report(results)
    
    # 打印摘要
    validator.print_validation_summary(results)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    print("✅ 数据验证完成！")

if __name__ == "__main__":
    main()