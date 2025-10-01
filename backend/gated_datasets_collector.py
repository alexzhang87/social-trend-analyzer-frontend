#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
受限 Hugging Face 数据集获取脚本
专门获取需要认证的高质量数据集
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
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gated_datasets_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 numpy 数组"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

class GatedDatasetsCollector:
    """受限数据集收集器"""
    
    def __init__(self, output_dir: str = "collected_data"):
        self.output_dir = output_dir
        self.results = {}
        self.start_time = datetime.now()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义受限数据集配置
        self.gated_datasets_config = {
            "chatbot_arena": {
                "name": "lmsys/chatbot_arena_conversations",
                "description": "聊天机器人竞技场对话数据",
                "expected_samples": "33,000条清洁对话",
                "quality_score": 0.95,
                "max_samples": 5000,  # 限制样本数量以避免过大
                "split": "train",
                "use_case": "对话质量优化、人类偏好学习"
            },
            "lmsys_chat_1m": {
                "name": "lmsys/lmsys-chat-1m", 
                "description": "大规模聊天数据集",
                "expected_samples": "100万真实对话",
                "quality_score": 0.88,
                "max_samples": 10000,  # 限制样本数量
                "split": "train",
                "use_case": "通用对话能力训练"
            }
        }
    
    def collect_gated_dataset(self, key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个受限数据集"""
        logger.info(f"开始获取受限数据集: {config['name']}")
        
        result = {
            "dataset_key": key,
            "dataset_name": config["name"],
            "description": config["description"],
            "expected_samples": config["expected_samples"],
            "quality_score": config["quality_score"],
            "use_case": config["use_case"],
            "status": "failed",
            "error": None,
            "actual_samples": 0,
            "file_path": None,
            "download_time": 0,
            "processing_time": 0,
            "sample_preview": []
        }
        
        try:
            download_start = time.time()
            
            # 加载数据集
            logger.info(f"正在下载 {config['name']}...")
            dataset = load_dataset(
                config["name"], 
                split=config["split"],
                trust_remote_code=True
            )
            
            download_time = time.time() - download_start
            result["download_time"] = round(download_time, 2)
            
            processing_start = time.time()
            
            # 限制样本数量（这些数据集很大）
            original_size = len(dataset)
            if config["max_samples"] and original_size > config["max_samples"]:
                # 随机采样而不是只取前N个
                import random
                indices = random.sample(range(original_size), config["max_samples"])
                dataset = dataset.select(indices)
                logger.info(f"从 {original_size:,} 条中随机采样了 {config['max_samples']:,} 条")
            
            result["actual_samples"] = len(dataset)
            
            # 转换为 pandas DataFrame
            df = dataset.to_pandas()
            
            # 获取样本预览
            if len(df) > 0:
                preview_count = min(3, len(df))
                result["sample_preview"] = df.head(preview_count).to_dict('records')
            
            # 生成文件名
            safe_name = config["name"].replace("/", "_").replace("-", "_")
            file_path = os.path.join(self.output_dir, f"{safe_name}_{key}.csv")
            
            # 保存数据
            df.to_csv(file_path, index=False, encoding='utf-8')
            result["file_path"] = file_path
            
            processing_time = time.time() - processing_start
            result["processing_time"] = round(processing_time, 2)
            
            result["status"] = "success"
            logger.info(f"✅ 成功获取 {config['name']}: {result['actual_samples']:,} 条数据")
            
            # 显示数据结构信息
            logger.info(f"📊 数据列: {list(df.columns)}")
            logger.info(f"💾 文件大小: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ 获取 {config['name']} 失败: {e}")
            
            # 如果是认证问题，提供解决方案
            if "gated" in str(e).lower() or "private" in str(e).lower():
                logger.error("🔒 这是一个受限数据集，需要申请访问权限")
                logger.error(f"📋 请访问: https://huggingface.co/datasets/{config['name']}")
        
        return result
    
    def collect_all_gated_datasets(self) -> Dict[str, Any]:
        """批量获取所有受限数据集"""
        logger.info("🚀 开始获取受限 Hugging Face 数据集")
        
        total_datasets = len(self.gated_datasets_config)
        
        with tqdm(total=total_datasets, desc="获取受限数据集") as pbar:
            for key, config in self.gated_datasets_config.items():
                pbar.set_description(f"正在获取: {config['description']}")
                
                result = self.collect_gated_dataset(key, config)
                self.results[key] = result
                
                pbar.update(1)
                
                # 休息一下，避免请求过于频繁
                time.sleep(2)
        
        return self.results
    
    def generate_detailed_report(self) -> str:
        """生成详细的获取报告"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        successful_datasets = [r for r in self.results.values() if r["status"] == "success"]
        failed_datasets = [r for r in self.results.values() if r["status"] == "failed"]
        
        total_samples = sum(r["actual_samples"] for r in successful_datasets)
        total_download_time = sum(r["download_time"] for r in successful_datasets)
        total_processing_time = sum(r["processing_time"] for r in successful_datasets)
        
        report = f"""
# 🔐 受限 Hugging Face 数据集获取报告

## 📊 总体统计
- **获取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总耗时**: {total_time:.2f} 秒
- **成功数据集**: {len(successful_datasets)}/{len(self.results)}
- **总样本数**: {total_samples:,} 条
- **总下载时间**: {total_download_time:.2f} 秒
- **总处理时间**: {total_processing_time:.2f} 秒

## ✅ 成功获取的受限数据集

"""
        
        for result in successful_datasets:
            report += f"""### {result['description']}
- **数据集名称**: `{result['dataset_name']}`
- **预期数据量**: {result['expected_samples']}
- **实际获取**: {result['actual_samples']:,} 条样本
- **质量分数**: {result['quality_score']}/1.0
- **用途**: {result['use_case']}
- **下载时间**: {result['download_time']:.2f} 秒
- **处理时间**: {result['processing_time']:.2f} 秒
- **保存路径**: `{result['file_path']}`

#### 数据样本预览:
```json
{json.dumps(result['sample_preview'][:2], ensure_ascii=False, indent=2, cls=NumpyEncoder)}
```

"""
        
        if failed_datasets:
            report += "\n## ❌ 获取失败的数据集\n\n"
            for result in failed_datasets:
                report += f"""### {result['description']}
- **数据集名称**: `{result['dataset_name']}`
- **错误信息**: {result['error']}
- **解决方案**: 请访问 https://huggingface.co/datasets/{result['dataset_name']} 申请访问权限

"""
        
        # 合并所有数据统计
        all_data_count = total_samples + 40003  # 之前获取的数据
        
        report += f"""
## 🎉 数据获取完成总结！

### 📈 完整数据统计
- **受限数据集**: {total_samples:,} 条 (本次获取)
- **开放数据集**: 40,003 条 (之前获取)
- **总计**: {all_data_count:,} 条高质量对话数据

### 🎯 数据覆盖范围
- ✅ 客户支持场景 (10,000 条)
- ✅ 银行金融业务 (22,003 条)
- ✅ 电信行业服务 (8,000 条)
- ✅ 聊天机器人竞技场数据 ({successful_datasets[0]['actual_samples'] if successful_datasets else 0:,} 条)
- ✅ 大规模真实对话数据 ({successful_datasets[1]['actual_samples'] if len(successful_datasets) > 1 else 0:,} 条)

### 🚀 可以开始训练了！
现在你拥有了 **{all_data_count:,}** 条多样化、高质量的对话数据，足够训练一个强大的AI对话模型！

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def save_results(self):
        """保存获取结果和报告"""
        # 保存 JSON 格式的详细结果
        results_file = os.path.join(self.output_dir, "gated_datasets_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        # 保存 Markdown 格式的报告
        report = self.generate_detailed_report()
        report_file = os.path.join(self.output_dir, "gated_datasets_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 结果已保存到: {results_file}")
        logger.info(f"📄 报告已保存到: {report_file}")
        
        return report_file, results_file

def main():
    """主函数"""
    print("🔐 受限 Hugging Face 数据集获取工具")
    print("=" * 50)
    
    # 创建收集器实例
    collector = GatedDatasetsCollector()
    
    try:
        # 批量获取受限数据集
        results = collector.collect_all_gated_datasets()
        
        # 保存结果和生成报告
        report_file, results_file = collector.save_results()
        
        # 显示简要统计
        successful = sum(1 for r in results.values() if r["status"] == "success")
        total_samples = sum(r["actual_samples"] for r in results.values() if r["status"] == "success")
        
        print(f"\n🎉 受限数据集获取完成！")
        print(f"✅ 成功: {successful}/{len(results)} 个数据集")
        print(f"📊 新增样本: {total_samples:,} 条")
        print(f"📊 总计样本: {total_samples + 40003:,} 条")
        print(f"📄 详细报告: {report_file}")
        
    except Exception as e:
        logger.error(f"获取过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()