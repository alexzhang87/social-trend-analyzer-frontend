"""
Hugging Face数据集集成器
用于下载和整合相关的商业、产品和用户反馈数据集
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datasets import load_dataset, Dataset
from transformers import pipeline
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceDataIntegrator:
    """Hugging Face数据集集成器"""
    
    def __init__(self, output_dir: str = "huggingface_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化情感分析模型用于质量评估
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                         model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        
        # 相关数据集列表
        self.relevant_datasets = {
            # 应用评论数据集
            "app_reviews": {
                "name": "app_reviews",
                "description": "Android应用评论数据集，包含用户反馈",
                "text_column": "review",
                "expert_type": "user_experience"
            },
            
            # 亚马逊产品评论
            "amazon_polarity": {
                "name": "amazon_polarity", 
                "description": "亚马逊产品评论情感分析数据集",
                "text_column": "content",
                "expert_type": "market_research"
            },
            
            # IMDB电影评论（用户体验分析）
            "imdb": {
                "name": "imdb",
                "description": "IMDB电影评论数据集，用于用户体验分析",
                "text_column": "text", 
                "expert_type": "user_experience"
            },
            
            # 金融数据集
            "finance_alpaca": {
                "name": "gbharti/finance-alpaca",
                "description": "金融相关问答数据集",
                "text_column": "instruction",
                "expert_type": "business_strategy"
            },
            
            # 客户服务数据集
            "banking77": {
                "name": "banking77",
                "description": "银行客户服务意图分类数据集",
                "text_column": "text",
                "expert_type": "customer_service"
            },
            
            # 新闻分类数据集
            "ag_news": {
                "name": "ag_news",
                "description": "新闻分类数据集，包含商业新闻",
                "text_column": "text",
                "expert_type": "market_research"
            }
        }
        
    def download_dataset(self, dataset_config: Dict[str, str], max_samples: int = 5000) -> Optional[Dataset]:
        """下载指定数据集"""
        try:
            logger.info(f"正在下载数据集: {dataset_config['name']}")
            
            # 加载数据集
            if dataset_config['name'] == "app_reviews":
                # app_reviews数据集可能需要特殊处理
                try:
                    dataset = load_dataset(dataset_config['name'], split='train')
                except:
                    logger.warning(f"无法加载数据集 {dataset_config['name']}")
                    return None
            else:
                dataset = load_dataset(dataset_config['name'], split='train')
            
            # 限制样本数量
            if len(dataset) > max_samples:
                dataset = dataset.select(range(max_samples))
                
            logger.info(f"成功下载数据集 {dataset_config['name']}: {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            logger.error(f"下载数据集 {dataset_config['name']} 失败: {str(e)}")
            return None
    
    def process_dataset(self, dataset: Dataset, dataset_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """处理数据集，转换为统一格式"""
        processed_data = []
        text_column = dataset_config['text_column']
        expert_type = dataset_config['expert_type']
        
        logger.info(f"正在处理数据集: {dataset_config['name']}")
        
        for i, item in enumerate(dataset):
            try:
                # 获取文本内容
                if text_column in item:
                    text = str(item[text_column])
                else:
                    # 如果指定列不存在，尝试其他可能的文本列
                    text_candidates = ['text', 'content', 'review', 'instruction', 'input']
                    text = None
                    for candidate in text_candidates:
                        if candidate in item:
                            text = str(item[candidate])
                            break
                    
                    if not text:
                        continue
                
                # 过滤太短的文本
                if len(text.strip()) < 20:
                    continue
                
                # 计算质量分数
                quality_score = self.calculate_quality_score(text)
                
                # 只保留高质量数据
                if quality_score < 0.6:
                    continue
                
                processed_item = {
                    "text": text,
                    "expert_type": expert_type,
                    "quality_score": quality_score,
                    "source": f"huggingface_{dataset_config['name']}",
                    "metadata": {
                        "dataset": dataset_config['name'],
                        "description": dataset_config['description'],
                        "original_index": i,
                        "collected_at": datetime.now().isoformat()
                    }
                }
                
                processed_data.append(processed_item)
                
                # 每处理1000条记录打印进度
                if len(processed_data) % 1000 == 0:
                    logger.info(f"已处理 {len(processed_data)} 条高质量记录")
                    
            except Exception as e:
                logger.warning(f"处理记录 {i} 时出错: {str(e)}")
                continue
        
        logger.info(f"数据集 {dataset_config['name']} 处理完成: {len(processed_data)} 条高质量记录")
        return processed_data
    
    def calculate_quality_score(self, text: str) -> float:
        """计算文本质量分数"""
        try:
            # 基础质量检查
            score = 0.5
            
            # 长度检查
            if 50 <= len(text) <= 1000:
                score += 0.2
            elif len(text) > 1000:
                score += 0.1
            
            # 句子结构检查
            sentences = text.split('.')
            if len(sentences) >= 2:
                score += 0.1
            
            # 使用情感分析模型评估文本质量
            try:
                sentiment_result = self.sentiment_analyzer(text[:512])  # 限制长度
                confidence = sentiment_result[0]['score']
                score += confidence * 0.2
            except:
                pass
            
            # 检查是否包含有用的关键词
            business_keywords = [
                'strategy', 'business', 'market', 'customer', 'product', 
                'service', 'experience', 'feedback', 'analysis', 'insight',
                'growth', 'revenue', 'profit', 'competition', 'innovation'
            ]
            
            keyword_count = sum(1 for keyword in business_keywords if keyword.lower() in text.lower())
            if keyword_count > 0:
                score += min(keyword_count * 0.05, 0.2)
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.warning(f"计算质量分数时出错: {str(e)}")
            return 0.5
    
    async def download_all_datasets(self, max_samples_per_dataset: int = 5000) -> Dict[str, List[Dict[str, Any]]]:
        """下载并处理所有相关数据集"""
        all_data = {}
        
        for dataset_key, dataset_config in self.relevant_datasets.items():
            logger.info(f"开始处理数据集: {dataset_key}")
            
            # 下载数据集
            dataset = self.download_dataset(dataset_config, max_samples_per_dataset)
            
            if dataset is not None:
                # 处理数据集
                processed_data = self.process_dataset(dataset, dataset_config)
                all_data[dataset_key] = processed_data
                
                # 保存单个数据集
                output_file = os.path.join(self.output_dir, f"{dataset_key}_processed.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"数据集 {dataset_key} 已保存到 {output_file}")
            else:
                logger.warning(f"跳过数据集: {dataset_key}")
                all_data[dataset_key] = []
        
        return all_data
    
    def merge_all_data(self, all_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """合并所有数据集"""
        merged_data = []
        
        for dataset_key, data_list in all_data.items():
            merged_data.extend(data_list)
            logger.info(f"合并数据集 {dataset_key}: {len(data_list)} 条记录")
        
        # 按质量分数排序
        merged_data.sort(key=lambda x: x['quality_score'], reverse=True)
        
        logger.info(f"总共合并 {len(merged_data)} 条高质量记录")
        return merged_data
    
    def generate_statistics(self, merged_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据统计报告"""
        stats = {
            "total_records": len(merged_data),
            "collection_time": datetime.now().isoformat(),
            "datasets_used": list(self.relevant_datasets.keys()),
            "expert_type_distribution": {},
            "source_distribution": {},
            "quality_score_stats": {
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0
            }
        }
        
        if merged_data:
            # 专家类型分布
            expert_types = [item['expert_type'] for item in merged_data]
            for expert_type in set(expert_types):
                stats["expert_type_distribution"][expert_type] = expert_types.count(expert_type)
            
            # 数据源分布
            sources = [item['source'] for item in merged_data]
            for source in set(sources):
                stats["source_distribution"][source] = sources.count(source)
            
            # 质量分数统计
            quality_scores = [item['quality_score'] for item in merged_data]
            stats["quality_score_stats"] = {
                "mean": np.mean(quality_scores),
                "median": np.median(quality_scores),
                "min": np.min(quality_scores),
                "max": np.max(quality_scores)
            }
        
        return stats
    
    async def run_integration(self, max_samples_per_dataset: int = 5000) -> str:
        """运行完整的数据集成流程"""
        logger.info("开始Hugging Face数据集成流程")
        
        # 下载并处理所有数据集
        all_data = await self.download_all_datasets(max_samples_per_dataset)
        
        # 合并所有数据
        merged_data = self.merge_all_data(all_data)
        
        # 生成统计报告
        stats = self.generate_statistics(merged_data)
        
        # 保存合并后的数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_file = os.path.join(self.output_dir, f"huggingface_merged_data_{timestamp}.json")
        
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计报告
        stats_file = os.path.join(self.output_dir, f"huggingface_stats_{timestamp}.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据集成完成！")
        logger.info(f"合并数据文件: {merged_file}")
        logger.info(f"统计报告文件: {stats_file}")
        logger.info(f"总共获得 {len(merged_data)} 条高质量训练数据")
        
        return merged_file

async def main():
    """主函数"""
    integrator = HuggingFaceDataIntegrator()
    
    # 运行数据集成
    merged_file = await integrator.run_integration(max_samples_per_dataset=3000)
    
    print(f"\n✅ Hugging Face数据集成完成！")
    print(f"📁 合并数据文件: {merged_file}")
    print(f"🎯 可用于AI产品训练的高质量数据已准备就绪")

if __name__ == "__main__":
    asyncio.run(main())