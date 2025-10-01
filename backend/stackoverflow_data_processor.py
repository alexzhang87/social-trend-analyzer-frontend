#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stack Overflow 数据处理和质量评估脚本

功能：
1. 数据清理和预处理
2. 质量评估和过滤
3. 数据格式标准化
4. 重复数据检测和去除
5. 数据统计和报告生成

作者：AI Assistant
创建时间：2024年
"""

import json
import csv
import pandas as pd
import re
import html
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import logging
from collections import Counter
import hashlib

class StackOverflowDataProcessor:
    """Stack Overflow 数据处理器"""
    
    def __init__(self, output_dir: str = "processed_data"):
        """
        初始化数据处理器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 质量评估标准
        self.quality_standards = {
            'min_question_length': 20,
            'min_answer_length': 30,
            'min_score': -5,
            'max_title_length': 200,
            'required_fields': ['title', 'body', 'score'],
            'blacklist_tags': ['spam', 'off-topic', 'duplicate'],
            'min_view_count': 10
        }
        
        # 数据统计
        self.stats = {
            'total_processed': 0,
            'high_quality': 0,
            'medium_quality': 0,
            'low_quality': 0,
            'duplicates_removed': 0,
            'filtered_out': 0
        }
        
        # 重复检测
        self.seen_hashes = set()
    
    def clean_html(self, text: str) -> str:
        """清理 HTML 标签和特殊字符"""
        if not text:
            return ""
        
        # 解码 HTML 实体
        text = html.unescape(text)
        
        # 移除 HTML 标签，但保留代码块
        text = re.sub(r'<pre><code>(.*?)</code></pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL)
        text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_tags(self, tags_str: str) -> List[str]:
        """提取和清理标签"""
        if not tags_str:
            return []
        
        # 处理不同的标签格式
        if tags_str.startswith('<') and tags_str.endswith('>'):
            # XML 格式: <tag1><tag2><tag3>
            tags = re.findall(r'<([^>]+)>', tags_str)
        elif ',' in tags_str:
            # 逗号分隔格式
            tags = [tag.strip() for tag in tags_str.split(',')]
        elif ';' in tags_str:
            # 分号分隔格式
            tags = [tag.strip() for tag in tags_str.split(';')]
        else:
            # 单个标签或空格分隔
            tags = tags_str.split()
        
        # 清理和过滤标签
        cleaned_tags = []
        for tag in tags:
            tag = tag.strip().lower()
            if tag and tag not in self.quality_standards['blacklist_tags']:
                cleaned_tags.append(tag)
        
        return cleaned_tags
    
    def calculate_quality_score(self, item: Dict[str, Any]) -> Tuple[float, str]:
        """
        计算数据质量分数
        
        Returns:
            (质量分数, 质量等级)
        """
        score = 0.0
        
        # 基础字段检查 (20分)
        required_fields = self.quality_standards['required_fields']
        field_score = sum(1 for field in required_fields if item.get(field)) / len(required_fields)
        score += field_score * 20
        
        # 内容长度评估 (25分)
        title_len = len(item.get('title', ''))
        body_len = len(item.get('body', ''))
        
        if title_len >= 10 and title_len <= self.quality_standards['max_title_length']:
            score += 10
        if body_len >= self.quality_standards['min_question_length']:
            score += 15
        
        # 投票分数评估 (20分)
        vote_score = item.get('score', 0)
        if isinstance(vote_score, (int, float)):
            if vote_score >= 10:
                score += 20
            elif vote_score >= 5:
                score += 15
            elif vote_score >= 1:
                score += 10
            elif vote_score >= self.quality_standards['min_score']:
                score += 5
        
        # 浏览量评估 (15分)
        view_count = item.get('view_count', 0)
        if isinstance(view_count, (int, float)):
            if view_count >= 1000:
                score += 15
            elif view_count >= 100:
                score += 10
            elif view_count >= self.quality_standards['min_view_count']:
                score += 5
        
        # 答案质量评估 (20分)
        if 'answers' in item and item['answers']:
            answers = item['answers']
            if isinstance(answers, list) and len(answers) > 0:
                # 检查是否有被接受的答案
                has_accepted = any(ans.get('is_accepted', False) for ans in answers)
                if has_accepted:
                    score += 10
                
                # 检查答案长度和质量
                good_answers = 0
                for ans in answers:
                    ans_body = ans.get('body', '')
                    ans_score = ans.get('score', 0)
                    if len(ans_body) >= self.quality_standards['min_answer_length'] and ans_score >= 0:
                        good_answers += 1
                
                if good_answers > 0:
                    score += min(10, good_answers * 3)
        
        # 确定质量等级
        if score >= 80:
            quality_level = "high"
        elif score >= 60:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        return score, quality_level
    
    def generate_content_hash(self, item: Dict[str, Any]) -> str:
        """生成内容哈希用于重复检测"""
        content = f"{item.get('title', '')}{item.get('body', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, item: Dict[str, Any]) -> bool:
        """检测是否为重复内容"""
        content_hash = self.generate_content_hash(item)
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
    
    def process_single_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理单个数据项"""
        try:
            # 重复检测
            if self.is_duplicate(item):
                self.stats['duplicates_removed'] += 1
                return None
            
            # 数据清理
            processed_item = {
                'id': item.get('id', ''),
                'title': self.clean_html(item.get('title', '')),
                'body': self.clean_html(item.get('body', '')),
                'tags': self.extract_tags(item.get('tags', '')),
                'score': item.get('score', 0),
                'view_count': item.get('view_count', 0),
                'answer_count': item.get('answer_count', 0),
                'creation_date': item.get('creation_date', ''),
                'last_activity_date': item.get('last_activity_date', ''),
                'owner_user_id': item.get('owner_user_id', ''),
                'owner_display_name': item.get('owner_display_name', ''),
                'link': item.get('link', ''),
                'answers': []
            }
            
            # 处理答案
            if 'answers' in item and item['answers']:
                for answer in item['answers']:
                    if isinstance(answer, dict):
                        processed_answer = {
                            'id': answer.get('id', ''),
                            'body': self.clean_html(answer.get('body', '')),
                            'score': answer.get('score', 0),
                            'is_accepted': answer.get('is_accepted', False),
                            'creation_date': answer.get('creation_date', ''),
                            'owner_user_id': answer.get('owner_user_id', ''),
                            'owner_display_name': answer.get('owner_display_name', '')
                        }
                        processed_item['answers'].append(processed_answer)
            
            # 质量评估
            quality_score, quality_level = self.calculate_quality_score(processed_item)
            processed_item['quality_score'] = quality_score
            processed_item['quality_level'] = quality_level
            
            # 更新统计
            self.stats['total_processed'] += 1
            self.stats[quality_level + '_quality'] += 1
            
            # 基础过滤
            if (len(processed_item['title']) < 5 or 
                len(processed_item['body']) < self.quality_standards['min_question_length'] or
                processed_item['score'] < self.quality_standards['min_score']):
                self.stats['filtered_out'] += 1
                return None
            
            return processed_item
            
        except Exception as e:
            self.logger.error(f"处理数据项时出错: {e}")
            return None
    
    def process_json_file(self, input_file: str, output_file: str = None) -> str:
        """处理 JSON 格式的数据文件"""
        input_path = Path(input_file)
        if not output_file:
            output_file = self.output_dir / f"processed_{input_path.stem}.json"
        
        self.logger.info(f"开始处理 JSON 文件: {input_file}")
        
        processed_data = []
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    processed_item = self.process_single_item(item)
                    if processed_item:
                        processed_data.append(processed_item)
            elif isinstance(data, dict):
                processed_item = self.process_single_item(data)
                if processed_item:
                    processed_data.append(processed_item)
            
            # 保存处理后的数据
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"处理完成，保存到: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"处理 JSON 文件时出错: {e}")
            raise
    
    def process_csv_file(self, input_file: str, output_file: str = None) -> str:
        """处理 CSV 格式的数据文件"""
        input_path = Path(input_file)
        if not output_file:
            output_file = self.output_dir / f"processed_{input_path.stem}.csv"
        
        self.logger.info(f"开始处理 CSV 文件: {input_file}")
        
        processed_data = []
        
        try:
            df = pd.read_csv(input_path)
            
            for _, row in df.iterrows():
                item = row.to_dict()
                processed_item = self.process_single_item(item)
                if processed_item:
                    processed_data.append(processed_item)
            
            # 转换为 DataFrame 并保存
            if processed_data:
                # 展平数据结构以适应 CSV 格式
                flattened_data = []
                for item in processed_data:
                    flat_item = {
                        'id': item['id'],
                        'title': item['title'],
                        'body': item['body'],
                        'tags': ','.join(item['tags']),
                        'score': item['score'],
                        'view_count': item['view_count'],
                        'answer_count': item['answer_count'],
                        'quality_score': item['quality_score'],
                        'quality_level': item['quality_level'],
                        'creation_date': item['creation_date'],
                        'owner_display_name': item['owner_display_name'],
                        'link': item['link']
                    }
                    
                    # 添加最佳答案信息
                    if item['answers']:
                        best_answer = max(item['answers'], key=lambda x: x['score'])
                        flat_item['best_answer_body'] = best_answer['body']
                        flat_item['best_answer_score'] = best_answer['score']
                        flat_item['best_answer_accepted'] = best_answer['is_accepted']
                    else:
                        flat_item['best_answer_body'] = ''
                        flat_item['best_answer_score'] = 0
                        flat_item['best_answer_accepted'] = False
                    
                    flattened_data.append(flat_item)
                
                df_processed = pd.DataFrame(flattened_data)
                df_processed.to_csv(output_file, index=False, encoding='utf-8')
            
            self.logger.info(f"处理完成，保存到: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"处理 CSV 文件时出错: {e}")
            raise
    
    def create_training_dataset(self, processed_files: List[str], output_file: str = None) -> str:
        """创建统一的训练数据集"""
        if not output_file:
            output_file = self.output_dir / "stackoverflow_training_dataset.json"
        
        self.logger.info("创建训练数据集...")
        
        training_data = []
        
        for file_path in processed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    # 转换为统一的训练格式
                    training_item = {
                        'instruction': f"请回答以下关于 {', '.join(item['tags'])} 的技术问题：",
                        'input': item['title'] + '\n\n' + item['body'],
                        'output': '',
                        'source': 'stackoverflow',
                        'quality_score': item['quality_score'],
                        'metadata': {
                            'id': item['id'],
                            'tags': item['tags'],
                            'score': item['score'],
                            'view_count': item['view_count'],
                            'link': item['link']
                        }
                    }
                    
                    # 添加最佳答案作为输出
                    if item['answers']:
                        best_answer = max(item['answers'], key=lambda x: x['score'])
                        training_item['output'] = best_answer['body']
                        training_item['metadata']['answer_score'] = best_answer['score']
                        training_item['metadata']['answer_accepted'] = best_answer['is_accepted']
                    
                    # 只包含有答案的高质量问题
                    if (training_item['output'] and 
                        item['quality_level'] in ['high', 'medium']):
                        training_data.append(training_item)
                        
            except Exception as e:
                self.logger.error(f"处理文件 {file_path} 时出错: {e}")
        
        # 按质量分数排序
        training_data.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # 保存训练数据集
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"训练数据集创建完成，包含 {len(training_data)} 条数据")
        self.logger.info(f"保存到: {output_file}")
        
        return str(output_file)
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """生成数据质量报告"""
        report = {
            'processing_summary': {
                'total_processed': self.stats['total_processed'],
                'high_quality': self.stats['high_quality'],
                'medium_quality': self.stats['medium_quality'],
                'low_quality': self.stats['low_quality'],
                'duplicates_removed': self.stats['duplicates_removed'],
                'filtered_out': self.stats['filtered_out']
            },
            'quality_distribution': {
                'high_quality_percentage': round(self.stats['high_quality'] / max(self.stats['total_processed'], 1) * 100, 2),
                'medium_quality_percentage': round(self.stats['medium_quality'] / max(self.stats['total_processed'], 1) * 100, 2),
                'low_quality_percentage': round(self.stats['low_quality'] / max(self.stats['total_processed'], 1) * 100, 2)
            },
            'quality_standards': self.quality_standards,
            'processing_timestamp': datetime.now().isoformat(),
            'recommendations': []
        }
        
        # 添加建议
        if report['quality_distribution']['high_quality_percentage'] < 30:
            report['recommendations'].append("高质量数据比例较低，建议调整过滤标准或寻找更好的数据源")
        
        if self.stats['duplicates_removed'] > self.stats['total_processed'] * 0.1:
            report['recommendations'].append("发现较多重复数据，建议检查数据源的去重机制")
        
        if self.stats['filtered_out'] > self.stats['total_processed'] * 0.5:
            report['recommendations'].append("过滤掉的数据较多，建议检查过滤标准是否过于严格")
        
        return report
    
    def save_quality_report(self, report: Dict[str, Any] = None) -> str:
        """保存质量报告"""
        if not report:
            report = self.generate_quality_report()
        
        report_file = self.output_dir / "quality_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"质量报告保存到: {report_file}")
        return str(report_file)

def main():
    """主函数 - 演示用法"""
    processor = StackOverflowDataProcessor()
    
    print("Stack Overflow 数据处理器")
    print("=" * 50)
    
    # 示例：处理数据文件
    # processor.process_json_file("stackoverflow_data.json")
    # processor.process_csv_file("stackoverflow_data.csv")
    
    # 生成质量报告
    report = processor.generate_quality_report()
    processor.save_quality_report(report)
    
    print("\n处理统计:")
    print(f"总处理数量: {processor.stats['total_processed']}")
    print(f"高质量数据: {processor.stats['high_quality']}")
    print(f"中等质量数据: {processor.stats['medium_quality']}")
    print(f"低质量数据: {processor.stats['low_quality']}")
    print(f"重复数据移除: {processor.stats['duplicates_removed']}")
    print(f"过滤掉的数据: {processor.stats['filtered_out']}")

if __name__ == "__main__":
    main()