#!/usr/bin/env python3
"""
Stack Overflow 数据获取器
支持通过 Stack Exchange API 获取高质量的技术问答数据
"""

import os
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
import html
import re
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stackoverflow_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StackOverflowDataCollector:
    """Stack Overflow 数据收集器"""
    
    def __init__(self, output_dir: str = "collected_data"):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # API 配置
        self.rate_limit_delay = 0.1  # 每秒最多10次请求
        self.max_retries = 3
        self.timeout = 30
        
        # 数据配置
        self.target_tags = [
            'python', 'javascript', 'java', 'react', 'node.js',
            'machine-learning', 'artificial-intelligence', 'data-science',
            'web-development', 'mobile-development', 'api', 'database',
            'startup', 'business', 'entrepreneurship'
        ]
        
        # 质量过滤配置
        self.min_score = 5  # 最低评分
        self.min_answer_count = 1  # 最少回答数
        self.min_view_count = 100  # 最少浏览数
        
        logger.info("Stack Overflow 数据收集器已初始化")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发起 API 请求"""
        url = f"{self.base_url}/{endpoint}"
        
        # 添加基础参数
        params.update({
            'site': self.site,
            'filter': 'withbody'  # 包含问题和答案内容
        })
        
        for attempt in range(self.max_retries):
            try:
                # 速率限制
                time.sleep(self.rate_limit_delay)
                
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查配额
                    quota_remaining = data.get('quota_remaining', 0)
                    if quota_remaining < 100:
                        logger.warning(f"API 配额剩余: {quota_remaining}")
                    
                    return data
                
                elif response.status_code == 429:
                    # 速率限制，等待更长时间
                    wait_time = 2 ** attempt
                    logger.warning(f"触发速率限制，等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.error(f"API 请求失败: {response.status_code} - {response.text}")
                    return {'items': []}
                    
            except Exception as e:
                logger.error(f"请求异常 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return {'items': []}
        
        return {'items': []}
    
    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签和转义字符"""
        if not text:
            return ""
        
        # 解码 HTML 实体
        text = html.unescape(text)
        
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_quality_score(self, question: Dict[str, Any]) -> float:
        """计算问题质量分数"""
        score = question.get('score', 0)
        view_count = question.get('view_count', 0)
        answer_count = question.get('answer_count', 0)
        
        # 基础分数 (0-1)
        base_score = min(score / 20, 1.0) if score > 0 else 0
        
        # 浏览量加成 (0-0.3)
        view_bonus = min(view_count / 10000, 0.3)
        
        # 回答数加成 (0-0.2)
        answer_bonus = min(answer_count / 10, 0.2)
        
        # 是否有被接受的答案 (0.1)
        accepted_bonus = 0.1 if question.get('accepted_answer_id') else 0
        
        total_score = base_score + view_bonus + answer_bonus + accepted_bonus
        return min(total_score, 1.0)
    
    def _is_quality_question(self, question: Dict[str, Any]) -> bool:
        """判断是否为高质量问题"""
        score = question.get('score', 0)
        view_count = question.get('view_count', 0)
        answer_count = question.get('answer_count', 0)
        
        return (score >= self.min_score and 
                view_count >= self.min_view_count and 
                answer_count >= self.min_answer_count)
    
    def collect_questions_by_tag(self, tag: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """根据标签收集问题"""
        logger.info(f"开始收集标签 '{tag}' 的问题...")
        
        all_questions = []
        
        for page in range(1, max_pages + 1):
            params = {
                'order': 'desc',
                'sort': 'votes',
                'tagged': tag,
                'pagesize': 100,
                'page': page
            }
            
            data = self._make_request('questions', params)
            questions = data.get('items', [])
            
            if not questions:
                logger.info(f"标签 '{tag}' 第 {page} 页无数据，停止收集")
                break
            
            # 过滤高质量问题
            quality_questions = [q for q in questions if self._is_quality_question(q)]
            all_questions.extend(quality_questions)
            
            logger.info(f"标签 '{tag}' 第 {page} 页: {len(quality_questions)}/{len(questions)} 个高质量问题")
            
            # 检查是否还有更多数据
            if not data.get('has_more', False):
                break
        
        logger.info(f"标签 '{tag}' 总计收集: {len(all_questions)} 个高质量问题")
        return all_questions
    
    def get_question_answers(self, question_id: int) -> List[Dict[str, Any]]:
        """获取问题的答案"""
        params = {
            'order': 'desc',
            'sort': 'votes',
            'pagesize': 10
        }
        
        data = self._make_request(f'questions/{question_id}/answers', params)
        return data.get('items', [])
    
    def format_question_data(self, question: Dict[str, Any], answers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化问题数据"""
        title = self._clean_html(question.get('title', ''))
        body = self._clean_html(question.get('body', ''))
        tags = question.get('tags', [])
        
        # 构建指令
        instruction = f"问题: {title}"
        if body:
            instruction += f"\n\n详细描述: {body}"
        
        # 获取最佳答案
        best_answer = ""
        if answers:
            # 优先选择被接受的答案
            accepted_answers = [a for a in answers if a.get('is_accepted', False)]
            if accepted_answers:
                best_answer = self._clean_html(accepted_answers[0].get('body', ''))
            elif answers:
                # 选择评分最高的答案
                best_answer = self._clean_html(answers[0].get('body', ''))
        
        return {
            'instruction': instruction,
            'input': '',
            'output': best_answer,
            'source': 'stackoverflow',
            'domain': 'technical_qa',
            'tags': tags,
            'question_id': question.get('question_id'),
            'score': question.get('score', 0),
            'view_count': question.get('view_count', 0),
            'answer_count': question.get('answer_count', 0),
            'creation_date': datetime.fromtimestamp(question.get('creation_date', 0)).isoformat(),
            'quality_score': self._calculate_quality_score(question),
            'link': question.get('link', '')
        }
    
    def collect_all_data(self, max_questions_per_tag: int = 500) -> List[Dict[str, Any]]:
        """收集所有数据"""
        logger.info("开始收集 Stack Overflow 数据...")
        
        all_data = []
        
        for tag in self.target_tags:
            try:
                # 计算每个标签需要的页数
                max_pages = max(1, max_questions_per_tag // 100)
                
                questions = self.collect_questions_by_tag(tag, max_pages)
                
                for question in questions:
                    # 获取答案（仅获取前几个高质量答案）
                    answers = self.get_question_answers(question.get('question_id'))
                    
                    # 格式化数据
                    formatted_data = self.format_question_data(question, answers)
                    
                    # 只保存有答案的问题
                    if formatted_data['output']:
                        all_data.append(formatted_data)
                
                logger.info(f"标签 '{tag}' 完成，累计收集: {len(all_data)} 条数据")
                
            except Exception as e:
                logger.error(f"收集标签 '{tag}' 数据时出错: {e}")
                continue
        
        logger.info(f"Stack Overflow 数据收集完成，总计: {len(all_data)} 条数据")
        return all_data
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """保存数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stackoverflow_data_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # 自定义 JSON 编码器处理 numpy 类型
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
            filename = f"stackoverflow_data_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"CSV 数据已保存到: {filepath}")
        return str(filepath)
    
    def generate_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据收集报告"""
        if not data:
            return {
                'total_count': 0,
                'average_quality': 0,
                'tag_distribution': {},
                'quality_distribution': {},
                'summary': '未收集到数据'
            }
        
        df = pd.DataFrame(data)
        
        # 标签分布
        all_tags = []
        for tags in df['tags']:
            all_tags.extend(tags)
        tag_counts = pd.Series(all_tags).value_counts().head(20).to_dict()
        
        # 质量分布
        quality_scores = df['quality_score']
        quality_distribution = {
            'excellent (0.8-1.0)': len(quality_scores[quality_scores >= 0.8]),
            'good (0.6-0.8)': len(quality_scores[(quality_scores >= 0.6) & (quality_scores < 0.8)]),
            'fair (0.4-0.6)': len(quality_scores[(quality_scores >= 0.4) & (quality_scores < 0.6)]),
            'poor (0.0-0.4)': len(quality_scores[quality_scores < 0.4])
        }
        
        # 数据样本
        samples = data[:3] if len(data) >= 3 else data
        
        report = {
            'collection_time': datetime.now().isoformat(),
            'total_count': len(data),
            'average_quality': float(quality_scores.mean()),
            'quality_distribution': quality_distribution,
            'tag_distribution': tag_counts,
            'score_stats': {
                'min_score': int(df['score'].min()),
                'max_score': int(df['score'].max()),
                'avg_score': float(df['score'].mean())
            },
            'view_stats': {
                'min_views': int(df['view_count'].min()),
                'max_views': int(df['view_count'].max()),
                'avg_views': float(df['view_count'].mean())
            },
            'data_samples': samples,
            'summary': f'成功收集 {len(data)} 条 Stack Overflow 高质量技术问答数据，平均质量评分 {quality_scores.mean():.3f}'
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """保存报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stackoverflow_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Stack Overflow 数据收集报告\n\n")
            f.write(f"**收集时间**: {report['collection_time']}\n\n")
            f.write(f"**总数据量**: {report['total_count']} 条\n\n")
            f.write(f"**平均质量评分**: {report['average_quality']:.3f}/1.0\n\n")
            
            f.write("## 质量分布\n\n")
            for level, count in report['quality_distribution'].items():
                f.write(f"- {level}: {count} 条\n")
            
            f.write("\n## 热门标签 (Top 20)\n\n")
            for tag, count in list(report['tag_distribution'].items())[:20]:
                f.write(f"- {tag}: {count} 次\n")
            
            f.write("\n## 评分统计\n\n")
            stats = report['score_stats']
            f.write(f"- 最低评分: {stats['min_score']}\n")
            f.write(f"- 最高评分: {stats['max_score']}\n")
            f.write(f"- 平均评分: {stats['avg_score']:.1f}\n")
            
            f.write("\n## 浏览量统计\n\n")
            stats = report['view_stats']
            f.write(f"- 最低浏览量: {stats['min_views']}\n")
            f.write(f"- 最高浏览量: {stats['max_views']}\n")
            f.write(f"- 平均浏览量: {stats['avg_views']:.0f}\n")
            
            f.write("\n## 数据样本预览\n\n")
            for i, sample in enumerate(report['data_samples'], 1):
                f.write(f"### 样本 {i}\n\n")
                f.write(f"**问题**: {sample['instruction'][:200]}...\n\n")
                f.write(f"**答案**: {sample['output'][:200]}...\n\n")
                f.write(f"**标签**: {', '.join(sample['tags'])}\n\n")
                f.write(f"**质量评分**: {sample['quality_score']:.3f}\n\n")
                f.write("---\n\n")
            
            f.write(f"\n## 总结\n\n{report['summary']}\n")
        
        logger.info(f"报告已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    collector = StackOverflowDataCollector()
    
    try:
        # 收集数据
        data = collector.collect_all_data(max_questions_per_tag=200)
        
        if data:
            # 保存数据
            json_file = collector.save_data(data)
            csv_file = collector.save_as_csv(data)
            
            # 生成和保存报告
            report = collector.generate_report(data)
            report_file = collector.save_report(report)
            
            print(f"\n✅ Stack Overflow 数据收集完成!")
            print(f"📊 总计收集: {len(data)} 条数据")
            print(f"📁 JSON 文件: {json_file}")
            print(f"📁 CSV 文件: {csv_file}")
            print(f"📁 报告文件: {report_file}")
            print(f"⭐ 平均质量评分: {report['average_quality']:.3f}/1.0")
        else:
            print("❌ 未收集到任何数据")
    
    except Exception as e:
        logger.error(f"数据收集过程中出错: {e}")
        print(f"❌ 数据收集失败: {e}")

if __name__ == "__main__":
    main()