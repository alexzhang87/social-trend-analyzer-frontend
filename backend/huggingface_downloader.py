#!/usr/bin/env python3
"""
Hugging Face 数据集下载器
专门下载商业洞察相关的高质量数据集
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HuggingFaceDownloader:
    def __init__(self):
        self.output_dir = Path("collected_data/huggingface")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 目标数据集列表 (基于文档分析的高价值数据集)
        self.target_datasets = [
            # 商业对话数据集
            {
                'id': 'microsoft/DialoGPT-medium',
                'type': 'conversation',
                'expert_type': 'business_strategy',
                'priority': 'high'
            },
            {
                'id': 'facebook/blenderbot-400M-distill',
                'type': 'conversation',
                'expert_type': 'user_insight',
                'priority': 'high'
            },
            
            # 商业文本数据集
            {
                'id': 'squad',
                'type': 'qa',
                'expert_type': 'data_insight',
                'priority': 'medium'
            },
            {
                'id': 'natural_questions',
                'type': 'qa',
                'expert_type': 'competitive_intelligence',
                'priority': 'medium'
            },
            
            # 金融和商业数据集
            {
                'id': 'financial_phrasebank',
                'type': 'classification',
                'expert_type': 'failure_prevention',
                'priority': 'high'
            },
            {
                'id': 'reuters21578',
                'type': 'news',
                'expert_type': 'competitive_intelligence',
                'priority': 'medium'
            },
            
            # 客户服务数据集
            {
                'id': 'banking77',
                'type': 'intent',
                'expert_type': 'user_insight',
                'priority': 'high'
            },
            {
                'id': 'bitext/Bitext-customer-support-llm-chatbot-training-dataset',
                'type': 'support',
                'expert_type': 'user_insight',
                'priority': 'high'
            }
        ]
        
        # 搜索关键词
        self.search_keywords = [
            'business', 'startup', 'entrepreneurship', 'market analysis',
            'customer service', 'financial', 'investment', 'venture capital',
            'business intelligence', 'market research', 'competitive analysis',
            'user research', 'product management', 'business strategy',
            'consulting', 'management', 'economics', 'commerce'
        ]
        
        # 数据质量标准
        self.quality_criteria = {
            'min_downloads': 100,
            'min_likes': 5,
            'required_tags': ['business', 'finance', 'economics', 'management', 'consulting'],
            'exclude_tags': ['medical', 'biology', 'chemistry', 'physics']
        }
        
        self.download_stats = {
            'searched': 0,
            'filtered': 0,
            'downloaded': 0,
            'failed': 0,
            'total_size': 0
        }

    def search_business_datasets(self) -> List[Dict]:
        """搜索商业相关数据集"""
        logger.info("开始搜索Hugging Face商业数据集...")
        
        all_datasets = []
        
        for keyword in self.search_keywords:
            try:
                # 搜索数据集
                url = f"https://huggingface.co/api/datasets?search={keyword}&limit=50"
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    datasets = response.json()
                    self.download_stats['searched'] += len(datasets)
                    
                    for dataset in datasets:
                        # 应用质量过滤
                        if self._meets_quality_criteria(dataset):
                            dataset_info = self._extract_dataset_info(dataset)
                            all_datasets.append(dataset_info)
                            self.download_stats['filtered'] += 1
                    
                    logger.info(f"关键词 '{keyword}': 找到 {len(datasets)} 个数据集，筛选出 {len([d for d in datasets if self._meets_quality_criteria(d)])} 个")
                    time.sleep(1)  # 避免请求过快
                    
            except Exception as e:
                logger.error(f"搜索数据集失败 (关键词: {keyword}): {e}")
                self.download_stats['failed'] += 1
        
        # 去重并排序
        unique_datasets = self._deduplicate_and_rank(all_datasets)
        
        logger.info(f"搜索完成: 总共找到 {len(unique_datasets)} 个高质量商业数据集")
        return unique_datasets

    def download_dataset_info(self, dataset_id: str) -> Optional[Dict]:
        """下载单个数据集的详细信息"""
        try:
            # 获取数据集详细信息
            url = f"https://huggingface.co/api/datasets/{dataset_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dataset_info = response.json()
                
                # 获取数据集文件列表
                files_url = f"https://huggingface.co/api/datasets/{dataset_id}/tree/main"
                files_response = requests.get(files_url, timeout=10)
                
                files_info = []
                if files_response.status_code == 200:
                    files_info = files_response.json()
                
                # 构建完整数据集信息
                complete_info = {
                    'id': dataset_id,
                    'description': dataset_info.get('description', ''),
                    'tags': dataset_info.get('tags', []),
                    'downloads': dataset_info.get('downloads', 0),
                    'likes': dataset_info.get('likes', 0),
                    'files': files_info,
                    'size_estimate': self._estimate_dataset_size(files_info),
                    'expert_type': self._classify_expert_type(dataset_info.get('description', '')),
                    'business_relevance': self._calculate_business_relevance(dataset_info),
                    'download_priority': self._calculate_download_priority(dataset_info),
                    'collected_at': datetime.now().isoformat()
                }
                
                return complete_info
                
        except Exception as e:
            logger.error(f"下载数据集信息失败 ({dataset_id}): {e}")
            return None

    def download_high_priority_datasets(self, max_datasets: int = 10) -> List[Dict]:
        """下载高优先级数据集"""
        logger.info(f"开始下载前 {max_datasets} 个高优先级数据集...")
        
        # 首先搜索数据集
        all_datasets = self.search_business_datasets()
        
        # 按优先级排序
        sorted_datasets = sorted(all_datasets, key=lambda x: x.get('download_priority', 0), reverse=True)
        
        downloaded_datasets = []
        
        for i, dataset in enumerate(sorted_datasets[:max_datasets]):
            try:
                logger.info(f"下载数据集 {i+1}/{max_datasets}: {dataset['id']}")
                
                # 下载详细信息
                detailed_info = self.download_dataset_info(dataset['id'])
                
                if detailed_info:
                    # 保存数据集信息
                    dataset_file = self.output_dir / f"{dataset['id'].replace('/', '_')}_{self.timestamp}.json"
                    with open(dataset_file, 'w', encoding='utf-8') as f:
                        json.dump(detailed_info, f, ensure_ascii=False, indent=2)
                    
                    downloaded_datasets.append(detailed_info)
                    self.download_stats['downloaded'] += 1
                    
                    logger.info(f"✅ 成功下载: {dataset['id']}")
                else:
                    logger.warning(f"❌ 下载失败: {dataset['id']}")
                    self.download_stats['failed'] += 1
                
                time.sleep(2)  # 避免请求过快
                
            except Exception as e:
                logger.error(f"下载数据集时出错 ({dataset['id']}): {e}")
                self.download_stats['failed'] += 1
        
        logger.info(f"数据集下载完成: {len(downloaded_datasets)} 个成功")
        return downloaded_datasets

    def generate_training_data(self, datasets: List[Dict]) -> List[Dict]:
        """将下载的数据集转换为训练数据格式"""
        logger.info("生成训练数据格式...")
        
        training_data = []
        
        for dataset in datasets:
            # 为每个数据集生成多个训练样本
            samples = self._generate_dataset_samples(dataset)
            training_data.extend(samples)
        
        logger.info(f"生成训练数据: {len(training_data)} 条")
        return training_data

    def _meets_quality_criteria(self, dataset: Dict) -> bool:
        """检查数据集是否符合质量标准"""
        # 检查下载量
        if dataset.get('downloads', 0) < self.quality_criteria['min_downloads']:
            return False
        
        # 检查点赞数
        if dataset.get('likes', 0) < self.quality_criteria['min_likes']:
            return False
        
        # 检查标签
        tags = dataset.get('tags', [])
        
        # 排除不相关标签
        for exclude_tag in self.quality_criteria['exclude_tags']:
            if exclude_tag in tags:
                return False
        
        # 检查商业相关性
        description = dataset.get('description', '').lower()
        dataset_id = dataset.get('id', '').lower()
        
        business_terms = ['business', 'finance', 'market', 'customer', 'startup', 'economic', 'commercial', 'enterprise']
        
        for term in business_terms:
            if term in description or term in dataset_id:
                return True
        
        return False

    def _extract_dataset_info(self, dataset: Dict) -> Dict:
        """提取数据集关键信息"""
        return {
            'id': dataset.get('id'),
            'description': dataset.get('description', ''),
            'tags': dataset.get('tags', []),
            'downloads': dataset.get('downloads', 0),
            'likes': dataset.get('likes', 0),
            'expert_type': self._classify_expert_type(dataset.get('description', '')),
            'business_relevance': self._calculate_business_relevance(dataset),
            'download_priority': self._calculate_download_priority(dataset)
        }

    def _classify_expert_type(self, description: str) -> str:
        """分类AI专家类型"""
        description_lower = description.lower()
        
        expert_keywords = {
            'data_insight': ['data', 'analysis', 'trends', 'metrics', 'insights', 'statistics'],
            'failure_prevention': ['risk', 'failure', 'crisis', 'warning', 'prevention', 'alert'],
            'business_strategy': ['strategy', 'planning', 'business', 'model', 'growth', 'development'],
            'competitive_intelligence': ['competition', 'competitor', 'market', 'intelligence', 'positioning'],
            'user_insight': ['user', 'customer', 'client', 'experience', 'behavior', 'satisfaction']
        }
        
        scores = {}
        for expert_type, keywords in expert_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            scores[expert_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'business_strategy'

    def _calculate_business_relevance(self, dataset: Dict) -> float:
        """计算商业相关性评分"""
        score = 0.0
        
        # 基于描述的相关性
        description = dataset.get('description', '').lower()
        business_keywords = ['business', 'market', 'customer', 'finance', 'startup', 'enterprise']
        
        for keyword in business_keywords:
            if keyword in description:
                score += 0.2
        
        # 基于标签的相关性
        tags = dataset.get('tags', [])
        business_tags = ['business', 'finance', 'economics', 'management', 'consulting']
        
        for tag in business_tags:
            if tag in tags:
                score += 0.15
        
        # 基于受欢迎程度
        downloads = dataset.get('downloads', 0)
        if downloads > 1000:
            score += 0.1
        elif downloads > 500:
            score += 0.05
        
        return min(score, 1.0)

    def _calculate_download_priority(self, dataset: Dict) -> float:
        """计算下载优先级"""
        priority = 0.0
        
        # 商业相关性权重最高
        priority += self._calculate_business_relevance(dataset) * 0.5
        
        # 受欢迎程度
        downloads = dataset.get('downloads', 0)
        likes = dataset.get('likes', 0)
        
        popularity_score = min((downloads / 1000 + likes / 10) / 2, 1.0)
        priority += popularity_score * 0.3
        
        # 数据集类型偏好
        dataset_id = dataset.get('id', '').lower()
        preferred_types = ['conversation', 'qa', 'classification', 'financial']
        
        for pref_type in preferred_types:
            if pref_type in dataset_id:
                priority += 0.2
                break
        
        return priority

    def _deduplicate_and_rank(self, datasets: List[Dict]) -> List[Dict]:
        """去重并排序数据集"""
        # 去重
        unique_datasets = []
        seen_ids = set()
        
        for dataset in datasets:
            dataset_id = dataset.get('id')
            if dataset_id and dataset_id not in seen_ids:
                unique_datasets.append(dataset)
                seen_ids.add(dataset_id)
        
        # 按优先级排序
        return sorted(unique_datasets, key=lambda x: x.get('download_priority', 0), reverse=True)

    def _estimate_dataset_size(self, files_info: List[Dict]) -> str:
        """估算数据集大小"""
        total_size = 0
        
        for file_info in files_info:
            if isinstance(file_info, dict) and 'size' in file_info:
                total_size += file_info.get('size', 0)
        
        # 转换为可读格式
        if total_size > 1024 * 1024 * 1024:  # GB
            return f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        elif total_size > 1024 * 1024:  # MB
            return f"{total_size / (1024 * 1024):.1f} MB"
        elif total_size > 1024:  # KB
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size} B"

    def _generate_dataset_samples(self, dataset: Dict) -> List[Dict]:
        """为数据集生成训练样本"""
        samples = []
        
        dataset_id = dataset.get('id', '')
        description = dataset.get('description', '')
        expert_type = dataset.get('expert_type', '')
        
        # 生成多种类型的问答对
        question_templates = [
            f"这个数据集 {dataset_id} 对{expert_type}有什么价值？",
            f"如何使用 {dataset_id} 数据集进行{expert_type}分析？",
            f"从{expert_type}角度，{dataset_id} 数据集的主要特点是什么？",
            f"{dataset_id} 数据集适合用于哪些{expert_type}场景？"
        ]
        
        for i, question in enumerate(question_templates):
            sample = {
                'expert_type': expert_type,
                'question': question,
                'answer': self._generate_expert_answer(dataset, question),
                'context': description,
                'source': 'huggingface',
                'dataset_id': dataset_id,
                'quality_score': dataset.get('business_relevance', 0.5),
                'sample_id': f"{dataset_id.replace('/', '_')}_sample_{i+1}",
                'metadata': {
                    'downloads': dataset.get('downloads', 0),
                    'likes': dataset.get('likes', 0),
                    'tags': dataset.get('tags', []),
                    'collected_at': dataset.get('collected_at')
                }
            }
            samples.append(sample)
        
        return samples

    def _generate_expert_answer(self, dataset: Dict, question: str) -> str:
        """生成专家风格的答案"""
        dataset_id = dataset.get('id', '')
        description = dataset.get('description', '')
        expert_type = dataset.get('expert_type', '')
        downloads = dataset.get('downloads', 0)
        
        # 基于专家类型生成不同风格的答案
        if expert_type == 'data_insight':
            return f"从数据洞察角度分析，{dataset_id} 数据集包含了{description}。该数据集已被下载{downloads}次，说明其在业界有一定认可度。我们可以利用这个数据集来识别数据模式、发现趋势，并为商业决策提供数据支撑。建议重点关注数据的时间序列特征和关键指标变化。"
        
        elif expert_type == 'failure_prevention':
            return f"从失败预防专家的角度，{dataset_id} 数据集提供了{description}。这类数据对于识别潜在风险信号非常有价值。通过分析历史数据中的失败案例和风险模式，我们可以建立预警机制。建议特别关注异常值和负面指标，以便及时发现和预防潜在问题。"
        
        elif expert_type == 'business_strategy':
            return f"从商业策略角度，{dataset_id} 数据集描述为{description}，下载量达到{downloads}次。这个数据集可以为制定商业策略提供重要参考。我建议将其用于市场分析、竞争对手研究和商业模式优化。通过深入分析数据中的商业模式和成功案例，可以为企业战略规划提供有力支撑。"
        
        elif expert_type == 'competitive_intelligence':
            return f"从竞争情报角度，{dataset_id} 数据集包含{description}。该数据集的{downloads}次下载量反映了市场对此类信息的需求。我们可以利用这个数据集来分析竞争格局、识别市场机会和威胁。建议重点关注竞争对手的策略模式和市场表现数据。"
        
        elif expert_type == 'user_insight':
            return f"从用户洞察专家的视角，{dataset_id} 数据集提供了{description}。这个数据集对于理解用户行为和需求非常有价值。通过分析用户数据，我们可以识别用户痛点、偏好和行为模式。建议将重点放在用户体验优化和个性化服务设计上。"
        
        return f"基于{expert_type}的专业角度，{dataset_id} 数据集（{description}）为我们提供了宝贵的分析资源。建议结合具体业务场景进行深入分析和应用。"

    def save_results(self, datasets: List[Dict], training_data: List[Dict]) -> Dict[str, str]:
        """保存结果"""
        # 保存数据集列表
        datasets_file = self.output_dir / f"business_datasets_{self.timestamp}.json"
        with open(datasets_file, 'w', encoding='utf-8') as f:
            json.dump(datasets, f, ensure_ascii=False, indent=2)
        
        # 保存训练数据
        training_file = self.output_dir / f"hf_training_data_{self.timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = self.output_dir / f"download_stats_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_stats, f, ensure_ascii=False, indent=2)
        
        return {
            'datasets_file': str(datasets_file),
            'training_file': str(training_file),
            'stats_file': str(stats_file)
        }

    def run_download_process(self, max_datasets: int = 15) -> Dict[str, str]:
        """执行完整的下载流程"""
        logger.info("开始Hugging Face数据集下载流程...")
        start_time = time.time()
        
        # 下载数据集
        datasets = self.download_high_priority_datasets(max_datasets)
        
        # 生成训练数据
        training_data = self.generate_training_data(datasets)
        
        # 保存结果
        files = self.save_results(datasets, training_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Hugging Face下载完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info(f"下载统计: {self.download_stats}")
        logger.info(f"生成训练数据: {len(training_data)} 条")
        
        return files

def main():
    """主函数"""
    downloader = HuggingFaceDownloader()
    files = downloader.run_download_process(max_datasets=20)
    
    print(f"\n🎉 Hugging Face数据下载完成!")
    print(f"📁 数据集文件: {files['datasets_file']}")
    print(f"📁 训练数据文件: {files['training_file']}")
    print(f"📊 统计文件: {files['stats_file']}")
    print(f"📈 下载统计: {downloader.download_stats}")
    
    return files

if __name__ == "__main__":
    main()