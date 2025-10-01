#!/usr/bin/env python3
"""
多数据源大规模收集器
集成Reddit、Stack Overflow、Hugging Face、arXiv等高质量数据源
目标：收集10,000+条训练数据
"""

import asyncio
import json
import os
import sys
import time
import requests
import re
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加服务路径
sys.path.append('app/services')

class MultiSourceCollector:
    def __init__(self):
        self.collected_data = []
        self.processed_ids = set()
        self.stats = {
            'reddit': 0,
            'stackoverflow': 0,
            'huggingface': 0,
            'arxiv': 0,
            'github': 0,
            'total': 0,
            'failed_requests': 0
        }

    async def collect_stackoverflow_data(self, target_count=2000):
        """收集Stack Overflow数据"""
        logger.info(f"🔍 开始收集Stack Overflow数据，目标：{target_count} 条")
        
        # 高价值标签（创业、技术、AI相关）
        tags = [
            'artificial-intelligence', 'machine-learning', 'deep-learning',
            'python', 'javascript', 'react', 'node.js', 'django', 'flask',
            'startup', 'business', 'entrepreneurship', 'saas', 'fintech',
            'blockchain', 'cryptocurrency', 'automation', 'api', 'database',
            'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'microservices',
            'data-science', 'analytics', 'big-data', 'mongodb', 'postgresql'
        ]
        
        collected_count = 0
        
        for tag in tags:
            if collected_count >= target_count:
                break
                
            try:
                # Stack Overflow API
                url = f"https://api.stackexchange.com/2.3/questions"
                params = {
                    'order': 'desc',
                    'sort': 'votes',
                    'tagged': tag,
                    'site': 'stackoverflow',
                    'pagesize': 100,
                    'filter': 'withbody'
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        if collected_count >= target_count:
                            break
                            
                        # 提取问题内容
                        question_data = self.process_stackoverflow_item(item, tag)
                        if question_data and question_data['metadata']['id'] not in self.processed_ids:
                            self.collected_data.append(question_data)
                            self.processed_ids.add(question_data['metadata']['id'])
                            collected_count += 1
                            self.stats['stackoverflow'] += 1
                            self.stats['total'] += 1
                
                logger.info(f"从Stack Overflow标签'{tag}'收集到数据，当前总计：{collected_count}")
                await asyncio.sleep(0.1)  # API限制
                
            except Exception as e:
                self.stats['failed_requests'] += 1
                logger.error(f"Stack Overflow收集失败 - {tag}: {e}")
                continue
        
        logger.info(f"✅ Stack Overflow收集完成，共 {collected_count} 条")

    def process_stackoverflow_item(self, item, tag):
        """处理Stack Overflow数据项"""
        try:
            # 清理HTML标签
            title = item.get('title', '')
            body = re.sub(r'<[^>]+>', '', item.get('body', ''))
            
            # 组合文本
            text = f"{title}\n\n{body}"
            
            # 质量过滤
            if len(text) < 100 or item.get('score', 0) < 5:
                return None
            
            return {
                'text': text[:2000],  # 限制长度
                'metadata': {
                    'source': 'stackoverflow',
                    'id': f"so_{item.get('question_id')}",
                    'title': title,
                    'score': item.get('score', 0),
                    'view_count': item.get('view_count', 0),
                    'answer_count': item.get('answer_count', 0),
                    'tags': item.get('tags', []),
                    'creation_date': item.get('creation_date'),
                    'url': item.get('link', ''),
                    'category': tag
                },
                'quality_score': min(1.0, (item.get('score', 0) + item.get('view_count', 0) / 1000) / 100),
                'category': 'technology',
                'type': 'qa'
            }
        except Exception as e:
            logger.error(f"处理Stack Overflow数据失败: {e}")
            return None

    async def collect_huggingface_datasets(self, target_count=1000):
        """收集Hugging Face数据集信息"""
        logger.info(f"🤗 开始收集Hugging Face数据，目标：{target_count} 条")
        
        try:
            # Hugging Face Hub API
            url = "https://huggingface.co/api/datasets"
            params = {
                'limit': 100,
                'sort': 'downloads',
                'direction': -1
            }
            
            collected_count = 0
            page = 0
            
            while collected_count < target_count and page < 10:
                params['offset'] = page * 100
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    datasets = response.json()
                    
                    for dataset in datasets:
                        if collected_count >= target_count:
                            break
                            
                        dataset_data = self.process_huggingface_dataset(dataset)
                        if dataset_data and dataset_data['metadata']['id'] not in self.processed_ids:
                            self.collected_data.append(dataset_data)
                            self.processed_ids.add(dataset_data['metadata']['id'])
                            collected_count += 1
                            self.stats['huggingface'] += 1
                            self.stats['total'] += 1
                
                page += 1
                await asyncio.sleep(0.5)
            
            logger.info(f"✅ Hugging Face收集完成，共 {collected_count} 条")
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Hugging Face收集失败: {e}")

    def process_huggingface_dataset(self, dataset):
        """处理Hugging Face数据集"""
        try:
            dataset_id = dataset.get('id', '')
            description = dataset.get('description', '')
            
            # 过滤相关数据集
            relevant_keywords = [
                'business', 'startup', 'finance', 'market', 'customer',
                'product', 'innovation', 'technology', 'ai', 'ml',
                'text', 'nlp', 'language', 'conversation', 'qa'
            ]
            
            if not any(keyword in description.lower() or keyword in dataset_id.lower() 
                      for keyword in relevant_keywords):
                return None
            
            if len(description) < 50:
                return None
            
            return {
                'text': f"Dataset: {dataset_id}\n\nDescription: {description}",
                'metadata': {
                    'source': 'huggingface',
                    'id': f"hf_{dataset_id}",
                    'dataset_id': dataset_id,
                    'downloads': dataset.get('downloads', 0),
                    'likes': dataset.get('likes', 0),
                    'tags': dataset.get('tags', []),
                    'url': f"https://huggingface.co/datasets/{dataset_id}",
                    'created_at': dataset.get('createdAt'),
                    'updated_at': dataset.get('lastModified')
                },
                'quality_score': min(1.0, (dataset.get('downloads', 0) + dataset.get('likes', 0) * 10) / 1000),
                'category': 'dataset',
                'type': 'resource'
            }
        except Exception as e:
            logger.error(f"处理Hugging Face数据失败: {e}")
            return None

    async def collect_arxiv_papers(self, target_count=1500):
        """收集arXiv学术论文"""
        logger.info(f"📚 开始收集arXiv学术论文，目标：{target_count} 条")
        
        # 相关研究领域
        categories = [
            'cs.AI',  # Artificial Intelligence
            'cs.LG',  # Machine Learning
            'cs.CL',  # Computation and Language
            'cs.IR',  # Information Retrieval
            'cs.SI',  # Social and Information Networks
            'econ.GN',  # General Economics
            'q-fin.GN',  # General Finance
            'stat.ML'  # Machine Learning (Statistics)
        ]
        
        # 相关关键词
        keywords = [
            'startup', 'entrepreneurship', 'business model', 'innovation',
            'artificial intelligence', 'machine learning', 'deep learning',
            'natural language processing', 'recommendation system',
            'market analysis', 'customer behavior', 'fintech',
            'digital transformation', 'automation', 'blockchain'
        ]
        
        collected_count = 0
        
        for category in categories:
            if collected_count >= target_count:
                break
                
            try:
                # arXiv API查询
                url = "http://export.arxiv.org/api/query"
                params = {
                    'search_query': f'cat:{category}',
                    'start': 0,
                    'max_results': 200,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    # 解析XML响应
                    root = ET.fromstring(response.content)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        if collected_count >= target_count:
                            break
                            
                        paper_data = self.process_arxiv_paper(entry, category)
                        if paper_data and paper_data['metadata']['id'] not in self.processed_ids:
                            self.collected_data.append(paper_data)
                            self.processed_ids.add(paper_data['metadata']['id'])
                            collected_count += 1
                            self.stats['arxiv'] += 1
                            self.stats['total'] += 1
                
                logger.info(f"从arXiv类别'{category}'收集到数据，当前总计：{collected_count}")
                await asyncio.sleep(1)  # 避免过于频繁请求
                
            except Exception as e:
                self.stats['failed_requests'] += 1
                logger.error(f"arXiv收集失败 - {category}: {e}")
                continue
        
        # 按关键词搜索
        for keyword in keywords[:10]:  # 限制关键词数量
            if collected_count >= target_count:
                break
                
            try:
                params = {
                    'search_query': f'all:{keyword}',
                    'start': 0,
                    'max_results': 50,
                    'sortBy': 'relevance'
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        if collected_count >= target_count:
                            break
                            
                        paper_data = self.process_arxiv_paper(entry, keyword)
                        if paper_data and paper_data['metadata']['id'] not in self.processed_ids:
                            self.collected_data.append(paper_data)
                            self.processed_ids.add(paper_data['metadata']['id'])
                            collected_count += 1
                            self.stats['arxiv'] += 1
                            self.stats['total'] += 1
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.stats['failed_requests'] += 1
                logger.error(f"arXiv关键词搜索失败 - {keyword}: {e}")
                continue
        
        logger.info(f"✅ arXiv收集完成，共 {collected_count} 条")

    def process_arxiv_paper(self, entry, category):
        """处理arXiv论文数据"""
        try:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            paper_id = entry.find('atom:id', ns).text.split('/')[-1]
            
            # 组合文本
            text = f"Title: {title}\n\nAbstract: {summary}"
            
            # 质量过滤
            if len(text) < 200:
                return None
            
            # 获取作者
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            # 获取发布日期
            published = entry.find('atom:published', ns)
            published_date = published.text if published is not None else ''
            
            return {
                'text': text[:2000],  # 限制长度
                'metadata': {
                    'source': 'arxiv',
                    'id': f"arxiv_{paper_id}",
                    'paper_id': paper_id,
                    'title': title,
                    'authors': authors,
                    'published': published_date,
                    'category': category,
                    'url': f"https://arxiv.org/abs/{paper_id}"
                },
                'quality_score': 0.8,  # 学术论文默认高质量
                'category': 'academic',
                'type': 'paper'
            }
        except Exception as e:
            logger.error(f"处理arXiv论文失败: {e}")
            return None

    async def collect_github_repositories(self, target_count=500):
        """收集GitHub仓库信息"""
        logger.info(f"🐙 开始收集GitHub仓库数据，目标：{target_count} 条")
        
        # 相关主题
        topics = [
            'startup', 'business', 'fintech', 'saas', 'ecommerce',
            'artificial-intelligence', 'machine-learning', 'nlp',
            'automation', 'blockchain', 'cryptocurrency', 'api',
            'data-science', 'analytics', 'recommendation-system'
        ]
        
        collected_count = 0
        
        for topic in topics:
            if collected_count >= target_count:
                break
                
            try:
                # GitHub Search API
                url = "https://api.github.com/search/repositories"
                params = {
                    'q': f'topic:{topic} stars:>100',
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 50
                }
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for repo in data.get('items', []):
                        if collected_count >= target_count:
                            break
                            
                        repo_data = self.process_github_repo(repo, topic)
                        if repo_data and repo_data['metadata']['id'] not in self.processed_ids:
                            self.collected_data.append(repo_data)
                            self.processed_ids.add(repo_data['metadata']['id'])
                            collected_count += 1
                            self.stats['github'] += 1
                            self.stats['total'] += 1
                
                logger.info(f"从GitHub主题'{topic}'收集到数据，当前总计：{collected_count}")
                await asyncio.sleep(1)  # GitHub API限制
                
            except Exception as e:
                self.stats['failed_requests'] += 1
                logger.error(f"GitHub收集失败 - {topic}: {e}")
                continue
        
        logger.info(f"✅ GitHub收集完成，共 {collected_count} 条")

    def process_github_repo(self, repo, topic):
        """处理GitHub仓库数据"""
        try:
            name = repo.get('name', '')
            description = repo.get('description', '') or ''
            
            # 组合文本
            text = f"Repository: {name}\n\nDescription: {description}"
            
            # 质量过滤
            if len(description) < 50 or repo.get('stargazers_count', 0) < 100:
                return None
            
            return {
                'text': text,
                'metadata': {
                    'source': 'github',
                    'id': f"gh_{repo.get('id')}",
                    'name': name,
                    'full_name': repo.get('full_name', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'language': repo.get('language', ''),
                    'topics': repo.get('topics', []),
                    'url': repo.get('html_url', ''),
                    'created_at': repo.get('created_at'),
                    'updated_at': repo.get('updated_at'),
                    'category': topic
                },
                'quality_score': min(1.0, repo.get('stargazers_count', 0) / 1000),
                'category': 'technology',
                'type': 'repository'
            }
        except Exception as e:
            logger.error(f"处理GitHub仓库失败: {e}")
            return None

    async def run_multi_source_collection(self):
        """运行多数据源收集"""
        start_time = time.time()
        logger.info("🚀 开始多数据源大规模数据收集...")
        
        # 并发收集不同数据源
        tasks = [
            self.collect_stackoverflow_data(2000),
            self.collect_huggingface_datasets(1000),
            self.collect_arxiv_papers(1500),
            self.collect_github_repositories(500)
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 保存最终数据
        final_stats = await self.save_final_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 多数据源收集完成！")
        logger.info(f"📊 最终统计：")
        logger.info(f"   - Reddit: {self.stats['reddit']} 条")
        logger.info(f"   - Stack Overflow: {self.stats['stackoverflow']} 条")
        logger.info(f"   - Hugging Face: {self.stats['huggingface']} 条")
        logger.info(f"   - arXiv: {self.stats['arxiv']} 条")
        logger.info(f"   - GitHub: {self.stats['github']} 条")
        logger.info(f"   - 总计: {self.stats['total']} 条")
        logger.info(f"   - 失败请求: {self.stats['failed_requests']} 次")
        logger.info(f"⏱️ 耗时：{duration:.2f} 秒")

    async def save_final_data(self):
        """保存最终数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        os.makedirs('collected_data', exist_ok=True)
        
        # 保存原始数据
        raw_file = f'collected_data/multi_source_raw_{timestamp}.json'
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据格式
        training_data = []
        for item in self.collected_data:
            if len(item.get('text', '')) >= 100 and item.get('quality_score', 0) >= 0.3:
                training_data.append(item)
        
        training_file = f'collected_data/multi_source_training_{timestamp}.json'
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 统计信息
        stats = {
            'collection_time': timestamp,
            'source_stats': self.stats,
            'total_items': len(self.collected_data),
            'training_items': len(training_data),
            'source_distribution': self.get_source_distribution(),
            'quality_distribution': self.get_quality_distribution(),
            'category_distribution': self.get_category_distribution()
        }
        
        stats_file = f'collected_data/multi_source_stats_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 原始数据：{raw_file}")
        logger.info(f"🎯 训练数据：{training_file}")
        logger.info(f"📊 统计信息：{stats_file}")
        
        return stats

    def get_source_distribution(self):
        """获取数据源分布"""
        sources = {}
        for item in self.collected_data:
            source = item.get('metadata', {}).get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        return sources

    def get_quality_distribution(self):
        """获取质量分布"""
        high, medium, low = 0, 0, 0
        for item in self.collected_data:
            score = item.get('quality_score', 0)
            if score >= 0.7:
                high += 1
            elif score >= 0.4:
                medium += 1
            else:
                low += 1
        return {'high': high, 'medium': medium, 'low': low}

    def get_category_distribution(self):
        """获取类别分布"""
        categories = {}
        for item in self.collected_data:
            category = item.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories

async def main():
    """主函数"""
    collector = MultiSourceCollector()
    await collector.run_multi_source_collection()

if __name__ == "__main__":
    asyncio.run(main())