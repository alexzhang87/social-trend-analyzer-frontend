#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化 Hugging Face 数据集获取脚本
批量下载和处理多个数据集，生成详细报告
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from datasets import load_dataset
from tqdm import tqdm
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('huggingface_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HuggingFaceAutoCollector:
    """自动化 Hugging Face 数据集收集器"""
    
    def __init__(self, output_dir: str = "collected_data"):
        self.output_dir = output_dir
        self.results = {}
        self.start_time = datetime.now()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义要获取的数据集配置
        self.datasets_config = {
            "customer_support": {
                "name": "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
                "description": "客户支持对话数据集",
                "expected_tokens": "357万",
                "quality_score": 0.92,
                "max_samples": 10000,
                "split": "train"
            },
            "chatbot_arena": {
                "name": "lmsys/chatbot_arena_conversations",
                "description": "聊天机器人竞技场对话数据",
                "expected_tokens": "33,000条",
                "quality_score": 0.95,
                "max_samples": 5000,
                "split": "train"
            },
            "large_chat": {
                "name": "lmsys/lmsys-chat-1m",
                "description": "大规模聊天数据集",
                "expected_tokens": "100万对话",
                "quality_score": 0.88,
                "max_samples": 15000,
                "split": "train"
            },
            "banking77": {
                "name": "banking77",
                "description": "银行业对话数据",
                "expected_tokens": "77个类别",
                "quality_score": 0.85,
                "max_samples": None,  # 获取全部
                "split": "train"
            },
            "retail_banking": {
                "name": "bitext/Bitext-retail-banking-llm-chatbot-training-dataset",
                "description": "银行业专业数据集",
                "expected_tokens": "498万",
                "quality_score": 0.90,
                "max_samples": 12000,
                "split": "train"
            },
            "telco": {
                "name": "bitext/Bitext-telco-llm-chatbot-training-dataset",
                "description": "电信业对话数据",
                "expected_tokens": "303万",
                "quality_score": 0.87,
                "max_samples": 8000,
                "split": "train"
            }
        }
    
    def collect_single_dataset(self, key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个数据集"""
        logger.info(f"开始获取数据集: {config['name']}")
        
        result = {
            "dataset_key": key,
            "dataset_name": config["name"],
            "description": config["description"],
            "expected_tokens": config["expected_tokens"],
            "quality_score": config["quality_score"],
            "status": "failed",
            "error": None,
            "actual_samples": 0,
            "file_path": None,
            "download_time": 0,
            "processing_time": 0
        }
        
        try:
            download_start = time.time()
            
            # 加载数据集
            dataset = load_dataset(
                config["name"], 
                split=config["split"],
                trust_remote_code=True
            )
            
            download_time = time.time() - download_start
            result["download_time"] = round(download_time, 2)
            
            processing_start = time.time()
            
            # 限制样本数量（如果指定）
            if config["max_samples"] and len(dataset) > config["max_samples"]:
                dataset = dataset.select(range(config["max_samples"]))
            
            result["actual_samples"] = len(dataset)
            
            # 转换为 pandas DataFrame 并保存
            df = dataset.to_pandas()
            
            # 生成文件名
            safe_name = config["name"].replace("/", "_").replace("-", "_")
            file_path = os.path.join(self.output_dir, f"{safe_name}_{key}.csv")
            
            # 保存数据
            df.to_csv(file_path, index=False, encoding='utf-8')
            result["file_path"] = file_path
            
            processing_time = time.time() - processing_start
            result["processing_time"] = round(processing_time, 2)
            
            result["status"] = "success"
            logger.info(f"✅ 成功获取 {config['name']}: {result['actual_samples']} 条数据")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ 获取 {config['name']} 失败: {e}")
        
        return result
    
    def collect_all_datasets(self) -> Dict[str, Any]:
        """批量获取所有数据集"""
        logger.info("🚀 开始批量获取 Hugging Face 数据集")
        
        total_datasets = len(self.datasets_config)
        
        with tqdm(total=total_datasets, desc="获取数据集进度") as pbar:
            for key, config in self.datasets_config.items():
                pbar.set_description(f"正在获取: {config['description']}")
                
                result = self.collect_single_dataset(key, config)
                self.results[key] = result
                
                pbar.update(1)
                
                # 短暂休息，避免请求过于频繁
                time.sleep(1)
        
        return self.results
    
    def generate_report(self) -> str:
        """生成详细的获取报告"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        successful_datasets = [r for r in self.results.values() if r["status"] == "success"]
        failed_datasets = [r for r in self.results.values() if r["status"] == "failed"]
        
        total_samples = sum(r["actual_samples"] for r in successful_datasets)
        total_download_time = sum(r["download_time"] for r in successful_datasets)
        total_processing_time = sum(r["processing_time"] for r in successful_datasets)
        
        report = f"""
# 🎯 Hugging Face 数据集自动获取报告

## 📊 总体统计
- **获取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总耗时**: {total_time:.2f} 秒
- **成功数据集**: {len(successful_datasets)}/{len(self.results)}
- **总样本数**: {total_samples:,} 条
- **总下载时间**: {total_download_time:.2f} 秒
- **总处理时间**: {total_processing_time:.2f} 秒

## ✅ 成功获取的数据集

"""
        
        for result in successful_datasets:
            report += f"""### {result['description']}
- **数据集名称**: `{result['dataset_name']}`
- **预期数据量**: {result['expected_tokens']}
- **实际获取**: {result['actual_samples']:,} 条样本
- **质量分数**: {result['quality_score']}/1.0
- **下载时间**: {result['download_time']:.2f} 秒
- **处理时间**: {result['processing_time']:.2f} 秒
- **保存路径**: `{result['file_path']}`

"""
        
        if failed_datasets:
            report += "\n## ❌ 获取失败的数据集\n\n"
            for result in failed_datasets:
                report += f"""### {result['description']}
- **数据集名称**: `{result['dataset_name']}`
- **错误信息**: {result['error']}

"""
        
        report += f"""
## 🎉 获取完成！

总共成功获取了 **{total_samples:,}** 条高质量对话数据，涵盖：
- 客户支持场景
- 银行金融业务
- 电信行业服务
- 通用对话交互

这些数据可以直接用于 AI 模型训练和优化！

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def save_results(self):
        """保存获取结果和报告"""
        # 保存 JSON 格式的详细结果
        results_file = os.path.join(self.output_dir, "collection_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 保存 Markdown 格式的报告
        report = self.generate_report()
        report_file = os.path.join(self.output_dir, "collection_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 结果已保存到: {results_file}")
        logger.info(f"📄 报告已保存到: {report_file}")
        
        return report_file, results_file

def main():
    """主函数"""
    print("🤖 Hugging Face 数据集自动获取工具")
    print("=" * 50)
    
    # 创建收集器实例
    collector = HuggingFaceAutoCollector()
    
    try:
        # 批量获取数据集
        results = collector.collect_all_datasets()
        
        # 保存结果和生成报告
        report_file, results_file = collector.save_results()
        
        # 显示简要统计
        successful = sum(1 for r in results.values() if r["status"] == "success")
        total_samples = sum(r["actual_samples"] for r in results.values() if r["status"] == "success")
        
        print(f"\n🎉 获取完成！")
        print(f"✅ 成功: {successful}/{len(results)} 个数据集")
        print(f"📊 总样本: {total_samples:,} 条")
        print(f"📄 详细报告: {report_file}")
        
    except Exception as e:
        logger.error(f"获取过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()