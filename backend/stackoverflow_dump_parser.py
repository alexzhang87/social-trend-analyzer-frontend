#!/usr/bin/env python3
"""
Stack Overflow 数据转储解析器
用于解析 Stack Overflow 的 XML 数据转储文件，提取高质量的问答对
"""

import os
import json
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
import re
import html
from typing import List, Dict, Any, Optional
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stackoverflow_parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StackOverflowDumpParser:
    """Stack Overflow 数据转储解析器"""
    
    def __init__(self, output_dir: str = "collected_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 质量过滤配置
        self.min_question_score = 5
        self.min_answer_score = 3
        self.min_view_count = 100
        self.min_content_length = 50
        self.max_content_length = 2048
        
        # 目标标签（技术相关）
        self.target_tags = {
            'python', 'javascript', 'java', 'c#', 'php', 'c++', 'typescript',
            'react', 'angular', 'vue.js', 'node.js', 'express',
            'html', 'css', 'bootstrap', 'jquery',
            'sql', 'mysql', 'postgresql', 'mongodb', 'database',
            'git', 'docker', 'kubernetes', 'aws', 'azure',
            'machine-learning', 'artificial-intelligence', 'data-science',
            'tensorflow', 'pytorch', 'pandas', 'numpy',
            'web-development', 'mobile-development', 'android', 'ios',
            'api', 'rest', 'graphql', 'microservices',
            'startup', 'business', 'entrepreneurship'
        }
        
        logger.info("Stack Overflow 数据转储解析器已初始化")
    
    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签和转义字符"""
        if not text:
            return ""
        
        # 解码 HTML 实体
        text = html.unescape(text)
        
        # 保留代码块格式
        text = re.sub(r'<pre><code>(.*?)</code></pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL)
        text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
        
        # 移除其他 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        
        return text
    
    def _extract_tags(self, tags_str: str) -> List[str]:
        """提取标签列表"""
        if not tags_str:
            return []
        
        # 标签格式: <tag1><tag2><tag3>
        tags = re.findall(r'<([^>]+)>', tags_str)
        return [tag.lower() for tag in tags]
    
    def _is_target_question(self, tags: List[str]) -> bool:
        """判断是否为目标技术领域的问题"""
        return bool(set(tags) & self.target_tags)
    
    def _calculate_quality_score(self, question_score: int, answer_score: int, 
                               view_count: int, is_accepted: bool) -> float:
        """计算质量分数"""
        # 基础分数 (0-0.4)
        base_score = min(question_score / 20, 0.4) if question_score > 0 else 0
        
        # 答案分数 (0-0.3)
        answer_bonus = min(answer_score / 15, 0.3) if answer_score > 0 else 0
        
        # 浏览量加成 (0-0.2)
        view_bonus = min(view_count / 10000, 0.2)
        
        # 被接受答案加成 (0.1)
        accepted_bonus = 0.1 if is_accepted else 0
        
        total_score = base_score + answer_bonus + view_bonus + accepted_bonus
        return min(total_score, 1.0)
    
    def _is_quality_content(self, content: str, score: int) -> bool:
        """判断内容质量"""
        if not content or len(content) < self.min_content_length:
            return False
        
        if len(content) > self.max_content_length:
            return False
        
        # 检查是否包含有意义的内容
        if len(content.split()) < 10:  # 至少10个单词
            return False
        
        return True
    
    def parse_posts_xml(self, xml_file_path: str, max_records: int = 100000) -> List[Dict[str, Any]]:
        """解析 Posts.xml 文件"""
        logger.info(f"开始解析 {xml_file_path}...")
        
        if not os.path.exists(xml_file_path):
            logger.error(f"文件不存在: {xml_file_path}")
            return []
        
        questions = {}  # 存储问题
        qa_pairs = []
        processed_count = 0
        
        try:
            # 使用迭代解析处理大文件
            context = ET.iterparse(xml_file_path, events=('start', 'end'))
            context = iter(context)
            event, root = next(context)
            
            for event, elem in context:
                if event == 'end' and elem.tag == 'row':
                    post_type = elem.get('PostTypeId')
                    
                    if post_type == '1':  # 问题
                        question_id = elem.get('Id')
                        title = elem.get('Title', '')
                        body = elem.get('Body', '')
                        tags_str = elem.get('Tags', '')
                        score = int(elem.get('Score', 0))
                        view_count = int(elem.get('ViewCount', 0))
                        answer_count = int(elem.get('AnswerCount', 0))
                        creation_date = elem.get('CreationDate', '')
                        accepted_answer_id = elem.get('AcceptedAnswerId')
                        
                        # 提取和过滤标签
                        tags = self._extract_tags(tags_str)
                        
                        # 过滤条件
                        if (score >= self.min_question_score and 
                            view_count >= self.min_view_count and
                            answer_count > 0 and
                            self._is_target_question(tags)):
                            
                            # 清理内容
                            clean_title = self._clean_html(title)
                            clean_body = self._clean_html(body)
                            
                            if self._is_quality_content(clean_title + clean_body, score):
                                questions[question_id] = {
                                    'id': question_id,
                                    'title': clean_title,
                                    'body': clean_body,
                                    'tags': tags,
                                    'score': score,
                                    'view_count': view_count,
                                    'answer_count': answer_count,
                                    'creation_date': creation_date,
                                    'accepted_answer_id': accepted_answer_id
                                }
                    
                    elif post_type == '2':  # 答案
                        parent_id = elem.get('ParentId')
                        answer_id = elem.get('Id')
                        body = elem.get('Body', '')
                        score = int(elem.get('Score', 0))
                        creation_date = elem.get('CreationDate', '')
                        
                        if (parent_id in questions and 
                            score >= self.min_answer_score):
                            
                            # 清理答案内容
                            clean_body = self._clean_html(body)
                            
                            if self._is_quality_content(clean_body, score):
                                question = questions[parent_id]
                                is_accepted = (answer_id == question.get('accepted_answer_id'))
                                
                                # 构建问答对
                                instruction = f"问题: {question['title']}"
                                if question['body']:
                                    instruction += f"\n\n详细描述: {question['body']}"
                                
                                qa_pair = {
                                    'instruction': instruction,
                                    'input': '',
                                    'output': clean_body,
                                    'source': 'stackoverflow_dump',
                                    'domain': 'technical_qa',
                                    'question_id': question['id'],
                                    'answer_id': answer_id,
                                    'tags': question['tags'],
                                    'question_score': question['score'],
                                    'answer_score': score,
                                    'view_count': question['view_count'],
                                    'is_accepted': is_accepted,
                                    'creation_date': creation_date,
                                    'quality_score': self._calculate_quality_score(
                                        question['score'], score, question['view_count'], is_accepted
                                    )
                                }
                                
                                qa_pairs.append(qa_pair)
                                processed_count += 1
                                
                                if processed_count % 1000 == 0:
                                    logger.info(f"已处理 {processed_count} 条问答对...")
                                
                                if processed_count >= max_records:
                                    logger.info(f"达到最大记录数 {max_records}，停止解析")
                                    break
                    
                    # 清理内存
                    elem.clear()
                    root.clear()
                
                if processed_count >= max_records:
                    break
        
        except Exception as e:
            logger.error(f"解析 XML 文件时出错: {e}")
            return qa_pairs
        
        logger.info(f"解析完成，共获得 {len(qa_pairs)} 条高质量问答对")
        return qa_pairs
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """保存数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stackoverflow_dump_data_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # 自定义 JSON 编码器
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        logger.info(f"数据已保存到: {filepath}")
        return str(filepath)
    
    def save_as_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """保存为 CSV 格式"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stackoverflow_dump_data_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # 处理复杂字段
        processed_data = []
        for item in data:
            processed_item = item.copy()
            processed_item['tags'] = ', '.join(item['tags'])
            processed_data.append(processed_item)
        
        df = pd.DataFrame(processed_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"CSV 数据已保存到: {filepath}")
        return str(filepath)
    
    def generate_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成解析报告"""
        if not data:
            return {
                'total_count': 0,
                'average_quality': 0,
                'tag_distribution': {},
                'quality_distribution': {},
                'summary': '未解析到数据'
            }
        
        df = pd.DataFrame(data)
        
        # 标签分布
        all_tags = []
        for tags in df['tags']:
            all_tags.extend(tags)
        tag_counts = pd.Series(all_tags).value_counts().head(30).to_dict()
        
        # 质量分布
        quality_scores = df['quality_score']
        quality_distribution = {
            'excellent (0.8-1.0)': len(quality_scores[quality_scores >= 0.8]),
            'good (0.6-0.8)': len(quality_scores[(quality_scores >= 0.6) & (quality_scores < 0.8)]),
            'fair (0.4-0.6)': len(quality_scores[(quality_scores >= 0.4) & (quality_scores < 0.6)]),
            'poor (0.0-0.4)': len(quality_scores[quality_scores < 0.4])
        }
        
        # 被接受答案统计
        accepted_count = len(df[df['is_accepted'] == True])
        
        # 数据样本
        samples = data[:3] if len(data) >= 3 else data
        
        report = {
            'parse_time': datetime.now().isoformat(),
            'total_count': len(data),
            'average_quality': float(quality_scores.mean()),
            'quality_distribution': quality_distribution,
            'tag_distribution': tag_counts,
            'accepted_answers': accepted_count,
            'accepted_percentage': float(accepted_count / len(data) * 100),
            'score_stats': {
                'question_score_avg': float(df['question_score'].mean()),
                'answer_score_avg': float(df['answer_score'].mean()),
                'view_count_avg': float(df['view_count'].mean())
            },
            'data_samples': samples,
            'summary': f'成功解析 {len(data)} 条 Stack Overflow 高质量问答对，平均质量评分 {quality_scores.mean():.3f}，被接受答案占比 {accepted_count / len(data) * 100:.1f}%'
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """保存解析报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stackoverflow_dump_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Stack Overflow 数据转储解析报告\n\n")
            f.write(f"**解析时间**: {report['parse_time']}\n\n")
            f.write(f"**总数据量**: {report['total_count']} 条\n\n")
            f.write(f"**平均质量评分**: {report['average_quality']:.3f}/1.0\n\n")
            f.write(f"**被接受答案**: {report['accepted_answers']} 条 ({report['accepted_percentage']:.1f}%)\n\n")
            
            f.write("## 质量分布\n\n")
            for level, count in report['quality_distribution'].items():
                percentage = count / report['total_count'] * 100
                f.write(f"- {level}: {count} 条 ({percentage:.1f}%)\n")
            
            f.write("\n## 热门标签 (Top 30)\n\n")
            for tag, count in list(report['tag_distribution'].items())[:30]:
                f.write(f"- {tag}: {count} 次\n")
            
            f.write("\n## 评分统计\n\n")
            stats = report['score_stats']
            f.write(f"- 平均问题评分: {stats['question_score_avg']:.1f}\n")
            f.write(f"- 平均答案评分: {stats['answer_score_avg']:.1f}\n")
            f.write(f"- 平均浏览量: {stats['view_count_avg']:.0f}\n")
            
            f.write("\n## 数据样本预览\n\n")
            for i, sample in enumerate(report['data_samples'], 1):
                f.write(f"### 样本 {i}\n\n")
                f.write(f"**问题**: {sample['instruction'][:300]}...\n\n")
                f.write(f"**答案**: {sample['output'][:300]}...\n\n")
                f.write(f"**标签**: {', '.join(sample['tags'])}\n\n")
                f.write(f"**质量评分**: {sample['quality_score']:.3f}\n\n")
                f.write(f"**是否被接受**: {'是' if sample['is_accepted'] else '否'}\n\n")
                f.write("---\n\n")
            
            f.write(f"\n## 总结\n\n{report['summary']}\n")
        
        logger.info(f"报告已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Stack Overflow 数据转储解析器')
    parser.add_argument('xml_file', help='Posts.xml 文件路径')
    parser.add_argument('--max-records', type=int, default=100000, help='最大解析记录数')
    parser.add_argument('--output-dir', default='collected_data', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建解析器
    parser_instance = StackOverflowDumpParser(args.output_dir)
    
    try:
        # 解析数据
        logger.info(f"开始解析 {args.xml_file}...")
        data = parser_instance.parse_posts_xml(args.xml_file, args.max_records)
        
        if data:
            # 保存数据
            json_file = parser_instance.save_data(data)
            csv_file = parser_instance.save_as_csv(data)
            
            # 生成和保存报告
            report = parser_instance.generate_report(data)
            report_file = parser_instance.save_report(report)
            
            print(f"\n✅ Stack Overflow 数据转储解析完成!")
            print(f"📊 总计解析: {len(data)} 条数据")
            print(f"📁 JSON 文件: {json_file}")
            print(f"📁 CSV 文件: {csv_file}")
            print(f"📁 报告文件: {report_file}")
            print(f"⭐ 平均质量评分: {report['average_quality']:.3f}/1.0")
            print(f"✅ 被接受答案占比: {report['accepted_percentage']:.1f}%")
        else:
            print("❌ 未解析到任何数据")
    
    except Exception as e:
        logger.error(f"解析过程中出错: {e}")
        print(f"❌ 解析失败: {e}")

if __name__ == "__main__":
    main()