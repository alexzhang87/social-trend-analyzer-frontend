#!/usr/bin/env python3
"""
Stack Overflow和Hugging Face专用数据收集器
专门收集高质量的技术问答和数据集
"""

import asyncio
import aiohttp
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote
import gzip

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stackoverflow_hf_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StackOverflowHFCollector:
    def __init__(self):
        self.session = None
        self.collected_data = []
        self.seen_urls = set()
        self.stats = {
            'stackoverflow_qa': 0,
            'huggingface_datasets': 0,
            'huggingface_models': 0,
            'total_collected': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 确保输出目录存在
        os.makedirs('collected_data', exist_ok=True)
        
        # Stack Overflow 高价值标签
        self.so_tags = [
            'python', 'javascript', 'java', 'c#', 'php', 'android', 'html',
            'jquery', 'c++', 'css', 'ios', 'sql', 'mysql', 'r', 'node.js',
            'angular', 'json', 'python-3.x', 'c', 'react', 'django', 'laravel',
            'spring', 'objective-c', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'machine-learning', 'deep-learning', 'artificial-intelligence',
            'data-science', 'nlp', 'computer-vision', 'blockchain', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'microservices', 'api',
            'rest', 'graphql', 'mongodb', 'postgresql', 'redis', 'elasticsearch'
        ]
        
        # Hugging Face 数据集类别
        self.hf_dataset_categories = [
            'text-classification', 'token-classification', 'question-answering',
            'summarization', 'translation', 'text-generation', 'fill-mask',
            'sentence-similarity', 'text-to-speech', 'automatic-speech-recognition',
            'image-classification', 'object-detection', 'image-segmentation',
            'text-to-image', 'image-to-text', 'unconditional-image-generation',
            'video-classification', 'reinforcement-learning', 'robotics',
            'tabular-classification', 'tabular-regression', 'time-series-forecasting'
        ]
        
        # Hugging Face 模型类别
        self.hf_model_categories = [
            'transformers', 'pytorch', 'tensorflow', 'jax', 'safetensors',
            'onnx', 'text-classification', 'token-classification', 'table-question-answering',
            'question-answering', 'zero-shot-classification', 'translation',
            'summarization', 'conversational', 'text-generation', 'text2text-generation',
            'fill-mask', 'sentence-similarity', 'text-to-speech', 'text-to-audio',
            'automatic-speech-recognition', 'audio-to-audio', 'audio-classification',
            'voice-activity-detection', 'depth-estimation', 'image-classification',
            'object-detection', 'image-segmentation', 'text-to-image', 'image-to-text',
            'image-to-image', 'unconditional-image-generation', 'video-classification',
            'reinforcement-learning', 'robotics', 'tabular-classification',
            'tabular-regression', 'time-series-forecasting', 'other'
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符但保留代码相关字符
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\\=\+\*\&\%\$\#\@]', '', text)
        
        return text.strip()

    async def collect_stackoverflow_qa(self, max_questions: int = 2000) -> List[Dict]:
        """收集Stack Overflow问答数据"""
        logger.info(f"💻 开始收集Stack Overflow问答，目标：{max_questions}个")
        qa_data = []
        
        try:
            # Stack Exchange API
            base_url = "https://api.stackexchange.com/2.3/questions"
            
            for tag in self.so_tags[:20]:  # 限制标签数量避免API限制
                if len(qa_data) >= max_questions:
                    break
                
                params = {
                    'order': 'desc',
                    'sort': 'votes',
                    'tagged': tag,
                    'site': 'stackoverflow',
                    'pagesize': min(100, max_questions - len(qa_data)),
                    'filter': 'withbody'
                }
                
                try:
                    async with self.session.get(base_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if 'items' in data:
                                for question in data['items']:
                                    if len(qa_data) >= max_questions:
                                        break
                                    
                                    title = question.get('title', '')
                                    body = question.get('body', '')
                                    question_id = question.get('question_id')
                                    
                                    if title and body and len(body) > 100:
                                        # 获取答案
                                        answers = await self.get_stackoverflow_answers(question_id)
                                        
                                        # 清理文本
                                        clean_title = self.clean_text(title)
                                        clean_body = self.clean_text(body)
                                        
                                        qa_text = f"问题：{clean_title}\n\n详情：{clean_body}"
                                        
                                        if answers:
                                            best_answer = answers[0]  # 通常第一个是最佳答案
                                            clean_answer = self.clean_text(best_answer.get('body', ''))
                                            qa_text += f"\n\n答案：{clean_answer}"
                                        
                                        qa_item = {
                                            'text': qa_text,
                                            'metadata': {
                                                'title': clean_title,
                                                'question_body': clean_body,
                                                'answers': answers,
                                                'tags': question.get('tags', []),
                                                'score': question.get('score', 0),
                                                'view_count': question.get('view_count', 0),
                                                'answer_count': question.get('answer_count', 0),
                                                'creation_date': question.get('creation_date'),
                                                'question_id': question_id,
                                                'source': 'Stack Overflow',
                                                'url': f"https://stackoverflow.com/questions/{question_id}",
                                                'primary_tag': tag
                                            },
                                            'quality_score': self.calculate_so_quality_score(question, answers),
                                            'category': 'technical_qa',
                                            'type': 'programming_qa'
                                        }
                                        
                                        qa_data.append(qa_item)
                                        self.stats['stackoverflow_qa'] += 1
                                        
                                        if len(qa_data) % 50 == 0:
                                            logger.info(f"已收集 {len(qa_data)} 个Stack Overflow问答")
                        
                        else:
                            logger.warning(f"Stack Overflow API请求失败，状态码：{response.status}")
                
                except Exception as e:
                    logger.error(f"收集标签 '{tag}' 的Stack Overflow数据时出错: {e}")
                    continue
                
                # API限制：每秒最多10个请求
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"收集Stack Overflow数据时出错: {e}")
        
        logger.info(f"✅ Stack Overflow问答收集完成，共收集 {len(qa_data)} 个")
        return qa_data

    async def get_stackoverflow_answers(self, question_id: int) -> List[Dict]:
        """获取问题的答案"""
        try:
            url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
            params = {
                'order': 'desc',
                'sort': 'votes',
                'site': 'stackoverflow',
                'filter': 'withbody',
                'pagesize': 3  # 只获取前3个答案
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
        
        except Exception as e:
            logger.error(f"获取问题 {question_id} 的答案时出错: {e}")
        
        return []

    async def collect_huggingface_datasets(self, max_datasets: int = 1000) -> List[Dict]:
        """收集Hugging Face数据集信息"""
        logger.info(f"🤗 开始收集Hugging Face数据集，目标：{max_datasets}个")
        datasets = []
        
        try:
            # Hugging Face Hub API
            base_url = "https://huggingface.co/api/datasets"
            
            params = {
                'limit': min(100, max_datasets),
                'sort': 'downloads',
                'direction': -1
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for dataset in data:
                        if len(datasets) >= max_datasets:
                            break
                        
                        dataset_id = dataset.get('id', '')
                        description = dataset.get('description', '')
                        
                        if dataset_id and description:
                            # 获取详细信息
                            dataset_info = await self.get_dataset_details(dataset_id)
                            
                            clean_description = self.clean_text(description)
                            
                            dataset_text = f"数据集：{dataset_id}\n\n描述：{clean_description}"
                            
                            if dataset_info:
                                if 'readme' in dataset_info:
                                    readme = self.clean_text(dataset_info['readme'][:1000])  # 限制长度
                                    dataset_text += f"\n\n详细信息：{readme}"
                            
                            dataset_item = {
                                'text': dataset_text,
                                'metadata': {
                                    'dataset_id': dataset_id,
                                    'description': clean_description,
                                    'tags': dataset.get('tags', []),
                                    'downloads': dataset.get('downloads', 0),
                                    'likes': dataset.get('likes', 0),
                                    'created_at': dataset.get('createdAt'),
                                    'updated_at': dataset.get('lastModified'),
                                    'source': 'Hugging Face Datasets',
                                    'url': f"https://huggingface.co/datasets/{dataset_id}",
                                    'size_categories': dataset.get('size_categories', []),
                                    'task_categories': dataset.get('task_categories', [])
                                },
                                'quality_score': self.calculate_hf_quality_score(dataset),
                                'category': 'dataset_info',
                                'type': 'ml_dataset'
                            }
                            
                            datasets.append(dataset_item)
                            self.stats['huggingface_datasets'] += 1
                            
                            if len(datasets) % 50 == 0:
                                logger.info(f"已收集 {len(datasets)} 个Hugging Face数据集")
                
                # 避免请求过快
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"收集Hugging Face数据集时出错: {e}")
        
        logger.info(f"✅ Hugging Face数据集收集完成，共收集 {len(datasets)} 个")
        return datasets

    async def get_dataset_details(self, dataset_id: str) -> Optional[Dict]:
        """获取数据集详细信息"""
        try:
            url = f"https://huggingface.co/api/datasets/{dataset_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        
        except Exception as e:
            logger.error(f"获取数据集 {dataset_id} 详细信息时出错: {e}")
        
        return None

    async def collect_huggingface_models(self, max_models: int = 1000) -> List[Dict]:
        """收集Hugging Face模型信息"""
        logger.info(f"🤖 开始收集Hugging Face模型，目标：{max_models}个")
        models = []
        
        try:
            # Hugging Face Hub API
            base_url = "https://huggingface.co/api/models"
            
            params = {
                'limit': min(100, max_models),
                'sort': 'downloads',
                'direction': -1
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for model in data:
                        if len(models) >= max_models:
                            break
                        
                        model_id = model.get('id', '')
                        
                        if model_id:
                            # 获取详细信息
                            model_info = await self.get_model_details(model_id)
                            
                            model_text = f"模型：{model_id}"
                            
                            if model_info:
                                if 'description' in model_info:
                                    description = self.clean_text(model_info['description'])
                                    model_text += f"\n\n描述：{description}"
                                
                                if 'readme' in model_info:
                                    readme = self.clean_text(model_info['readme'][:1000])  # 限制长度
                                    model_text += f"\n\n详细信息：{readme}"
                            
                            model_item = {
                                'text': model_text,
                                'metadata': {
                                    'model_id': model_id,
                                    'tags': model.get('tags', []),
                                    'downloads': model.get('downloads', 0),
                                    'likes': model.get('likes', 0),
                                    'created_at': model.get('createdAt'),
                                    'updated_at': model.get('lastModified'),
                                    'source': 'Hugging Face Models',
                                    'url': f"https://huggingface.co/{model_id}",
                                    'pipeline_tag': model.get('pipeline_tag'),
                                    'library_name': model.get('library_name')
                                },
                                'quality_score': self.calculate_hf_quality_score(model),
                                'category': 'model_info',
                                'type': 'ml_model'
                            }
                            
                            models.append(model_item)
                            self.stats['huggingface_models'] += 1
                            
                            if len(models) % 50 == 0:
                                logger.info(f"已收集 {len(models)} 个Hugging Face模型")
                
                # 避免请求过快
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"收集Hugging Face模型时出错: {e}")
        
        logger.info(f"✅ Hugging Face模型收集完成，共收集 {len(models)} 个")
        return models

    async def get_model_details(self, model_id: str) -> Optional[Dict]:
        """获取模型详细信息"""
        try:
            url = f"https://huggingface.co/api/models/{model_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        
        except Exception as e:
            logger.error(f"获取模型 {model_id} 详细信息时出错: {e}")
        
        return None

    def calculate_so_quality_score(self, question: Dict, answers: List[Dict]) -> float:
        """计算Stack Overflow问答质量分数"""
        score = 0.5  # 基础分数
        
        # 问题分数加分
        question_score = question.get('score', 0)
        if question_score > 0:
            score += min(question_score * 0.01, 0.2)
        
        # 浏览量加分
        view_count = question.get('view_count', 0)
        if view_count > 1000:
            score += 0.1
        if view_count > 10000:
            score += 0.1
        
        # 答案质量加分
        if answers:
            best_answer = answers[0]
            answer_score = best_answer.get('score', 0)
            if answer_score > 0:
                score += min(answer_score * 0.01, 0.2)
            
            if best_answer.get('is_accepted'):
                score += 0.1
        
        # 标签相关性加分
        tags = question.get('tags', [])
        high_value_tags = ['python', 'javascript', 'machine-learning', 'deep-learning', 'ai']
        for tag in tags:
            if tag in high_value_tags:
                score += 0.05
        
        return min(score, 1.0)

    def calculate_hf_quality_score(self, item: Dict) -> float:
        """计算Hugging Face项目质量分数"""
        score = 0.5  # 基础分数
        
        # 下载量加分
        downloads = item.get('downloads', 0)
        if downloads > 100:
            score += 0.1
        if downloads > 1000:
            score += 0.1
        if downloads > 10000:
            score += 0.1
        
        # 点赞数加分
        likes = item.get('likes', 0)
        if likes > 10:
            score += 0.1
        if likes > 50:
            score += 0.1
        
        # 标签相关性加分
        tags = item.get('tags', [])
        high_value_tags = ['pytorch', 'tensorflow', 'transformers', 'nlp', 'computer-vision']
        for tag in tags:
            if tag in high_value_tags:
                score += 0.02
        
        return min(score, 1.0)

    async def run_collection(self):
        """运行完整的Stack Overflow和Hugging Face收集"""
        logger.info("🎯 开始大规模Stack Overflow和Hugging Face数据收集")
        self.stats['start_time'] = datetime.now()
        
        # 并发收集所有类型的数据
        tasks = [
            self.collect_stackoverflow_qa(2000),
            self.collect_huggingface_datasets(1000),
            self.collect_huggingface_models(1000)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有数据
        for result in results:
            if isinstance(result, list):
                self.collected_data.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"收集任务失败: {result}")
        
        self.stats['total_collected'] = len(self.collected_data)
        self.stats['end_time'] = datetime.now()
        
        # 保存数据
        await self.save_data()
        
        # 显示统计信息
        self.show_final_stats()

    async def save_data(self):
        """保存收集的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存原始数据
        raw_file = f"collected_data/stackoverflow_hf_raw_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据
        training_data = []
        for item in self.collected_data:
            if item.get('quality_score', 0) >= 0.6:
                training_data.append({
                    'text': item['text'],
                    'metadata': item['metadata'],
                    'category': item['category'],
                    'type': item['type']
                })
        
        training_file = f"collected_data/stackoverflow_hf_training_{timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = f"collected_data/stackoverflow_hf_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"💾 原始数据：{raw_file}")
        logger.info(f"🎯 训练数据：{training_file}")
        logger.info(f"📊 统计信息：{stats_file}")

    def show_final_stats(self):
        """显示最终统计信息"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info("✅ Stack Overflow和Hugging Face数据收集完成！")
        logger.info("📊 最终统计：")
        logger.info(f"   - Stack Overflow问答：{self.stats['stackoverflow_qa']} 个")
        logger.info(f"   - Hugging Face数据集：{self.stats['huggingface_datasets']} 个")
        logger.info(f"   - Hugging Face模型：{self.stats['huggingface_models']} 个")
        logger.info(f"   - 总数据量：{self.stats['total_collected']} 条")
        logger.info(f"   - 数据大小：{len(json.dumps(self.collected_data)) / 1024 / 1024:.2f} MB")
        logger.info(f"⏱️ 耗时：{duration:.2f} 秒")

async def main():
    """主函数"""
    async with StackOverflowHFCollector() as collector:
        await collector.run_collection()

if __name__ == "__main__":
    asyncio.run(main())