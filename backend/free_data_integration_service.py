#!/usr/bin/env python3
"""
免费数据源集成服务
用于集成Hugging Face、Stack Overflow和SCORE等免费数据源
"""

import os
import json
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import hashlib
import re
from datasets import load_dataset, Dataset
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeDataIntegrationService:
    """免费数据源集成服务"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_dir = Path(config.get("data_dir", "./data/training"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.data_dir / "integrated_data.db"
        self.init_database()
        
        # 数据存储
        self.integrated_data = []
        self.quality_scores = []
        
    def init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                quality_score REAL,
                hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def integrate_all_sources(self) -> Dict[str, Any]:
        """集成所有数据源"""
        logger.info("🚀 开始集成所有免费数据源...")
        
        results = {
            "huggingface": await self.integrate_huggingface_datasets(),
            "stackoverflow": await self.integrate_stackoverflow_data(),
            "score": await self.integrate_score_data()
        }
        
        # 合并和处理数据
        await self.merge_and_process_data()
        
        # 生成报告
        report = self.generate_integration_report(results)
        
        logger.info("✅ 数据源集成完成")
        return report
    
    async def integrate_huggingface_datasets(self) -> Dict[str, Any]:
        """集成Hugging Face数据集"""
        logger.info("📚 集成Hugging Face数据集...")
        
        if not self.config.get("huggingface_datasets", {}).get("enabled", False):
            logger.info("⏭️ Hugging Face数据集集成已禁用")
            return {"status": "disabled", "count": 0}
        
        datasets_config = self.config["huggingface_datasets"]["datasets"]
        total_samples = 0
        
        for dataset_config in datasets_config:
            try:
                logger.info(f"📥 加载数据集: {dataset_config['name']}")
                
                # 加载数据集
                dataset = load_dataset(
                    dataset_config["name"],
                    dataset_config.get("config"),
                    split=dataset_config["split"]
                )
                
                # 提取文本数据
                text_column = dataset_config["text_column"]
                weight = dataset_config.get("weight", 1.0)
                
                for item in dataset:
                    text = self.extract_text_from_item(item, text_column)
                    if text and self.is_valid_text(text):
                        processed_text = self.adapt_to_consulting_format(text, "huggingface")
                        quality_score = self.calculate_quality_score(processed_text) * weight
                        
                        self.integrated_data.append({
                            "source": f"huggingface_{dataset_config['name']}",
                            "content": processed_text,
                            "quality_score": quality_score,
                            "original_text": text
                        })
                        total_samples += 1
                
                logger.info(f"✅ 数据集 {dataset_config['name']} 集成完成: {len(dataset)} 样本")
                
            except Exception as e:
                logger.error(f"❌ 数据集 {dataset_config['name']} 集成失败: {e}")
        
        return {"status": "completed", "count": total_samples}
    
    async def integrate_stackoverflow_data(self) -> Dict[str, Any]:
        """集成Stack Overflow数据"""
        logger.info("💻 集成Stack Overflow数据...")
        
        if not self.config.get("stackoverflow", {}).get("enabled", False):
            logger.info("⏭️ Stack Overflow数据集成已禁用")
            return {"status": "disabled", "count": 0}
        
        # 模拟Stack Overflow数据（实际实现需要API密钥）
        sample_data = [
            {
                "question": "How to validate a business idea?",
                "answer": "To validate a business idea, start by identifying your target market and conducting customer interviews. Create a minimum viable product (MVP) to test your assumptions. Use surveys, landing pages, and pre-orders to gauge interest.",
                "tags": ["entrepreneurship", "business-validation"],
                "score": 15
            },
            {
                "question": "What are the key metrics for a startup?",
                "answer": "Key startup metrics include Customer Acquisition Cost (CAC), Lifetime Value (LTV), Monthly Recurring Revenue (MRR), churn rate, and product-market fit indicators. Focus on metrics that directly impact your business model.",
                "tags": ["startup", "metrics"],
                "score": 23
            }
        ]
        
        total_samples = 0
        weight = self.config["stackoverflow"].get("weight", 1.0)
        
        for item in sample_data:
            # 组合问题和答案
            combined_text = f"Q: {item['question']}\nA: {item['answer']}"
            processed_text = self.adapt_to_consulting_format(combined_text, "stackoverflow")
            quality_score = self.calculate_quality_score(processed_text) * weight
            
            self.integrated_data.append({
                "source": "stackoverflow",
                "content": processed_text,
                "quality_score": quality_score,
                "original_text": combined_text
            })
            total_samples += 1
        
        return {"status": "completed", "count": total_samples}
    
    async def integrate_score_data(self) -> Dict[str, Any]:
        """集成SCORE平台数据"""
        logger.info("🏢 集成SCORE平台数据...")
        
        if not self.config.get("score_platform", {}).get("enabled", False):
            logger.info("⏭️ SCORE平台数据集成已禁用")
            return {"status": "disabled", "count": 0}
        
        # 模拟SCORE平台数据
        sample_data = [
            {
                "title": "Creating a Business Plan",
                "content": "A comprehensive business plan should include an executive summary, market analysis, organization structure, product description, marketing strategy, funding requirements, and financial projections. Start with a clear value proposition.",
                "category": "business-planning"
            },
            {
                "title": "Digital Marketing Strategies",
                "content": "Effective digital marketing combines SEO, content marketing, social media engagement, and email campaigns. Focus on understanding your customer journey and creating valuable content that addresses their pain points.",
                "category": "marketing"
            }
        ]
        
        total_samples = 0
        weight = self.config["score_platform"].get("weight", 1.0)
        
        for item in sample_data:
            combined_text = f"Topic: {item['title']}\n{item['content']}"
            processed_text = self.adapt_to_consulting_format(combined_text, "score")
            quality_score = self.calculate_quality_score(processed_text) * weight
            
            self.integrated_data.append({
                "source": "score",
                "content": processed_text,
                "quality_score": quality_score,
                "original_text": combined_text
            })
            total_samples += 1
        
        return {"status": "completed", "count": total_samples}
    
    def extract_text_from_item(self, item: Dict, text_column: str) -> Optional[str]:
        """从数据项中提取文本"""
        try:
            # 处理嵌套字段（如 "answers.text"）
            if "." in text_column:
                keys = text_column.split(".")
                value = item
                for key in keys:
                    if isinstance(value, list) and value:
                        value = value[0]  # 取第一个元素
                    value = value.get(key, "")
                return str(value) if value else None
            else:
                return str(item.get(text_column, ""))
        except Exception as e:
            logger.warning(f"提取文本失败: {e}")
            return None
    
    def is_valid_text(self, text: str) -> bool:
        """验证文本是否有效"""
        if not text or len(text.strip()) < 10:
            return False
        
        # 检查最小和最大长度
        min_length = self.config.get("data_integration", {}).get("min_text_length", 10)
        max_length = self.config.get("data_integration", {}).get("max_text_length", 512)
        
        return min_length <= len(text) <= max_length
    
    def adapt_to_consulting_format(self, text: str, source: str) -> str:
        """将文本适配为创业咨询格式"""
        # 清理文本
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\\S+@\\S+', '', text)  # 移除邮箱
        text = re.sub(r'\\s+', ' ', text)  # 规范化空白字符
        text = text.strip()
        
        # 根据来源添加上下文
        if source == "stackoverflow":
            if not text.startswith("Q:"):
                text = f"Business Question: {text}"
        elif source == "score":
            if not text.startswith("Topic:"):
                text = f"Business Guidance: {text}"
        elif source.startswith("huggingface"):
            text = f"Business Context: {text}"
        
        return text
    
    def calculate_quality_score(self, text: str) -> float:
        """计算文本质量分数"""
        score = 0.5  # 基础分数
        
        # 长度评分
        if 50 <= len(text) <= 300:
            score += 0.2
        elif 300 < len(text) <= 500:
            score += 0.1
        
        # 关键词评分
        business_keywords = [
            "business", "startup", "entrepreneur", "market", "customer",
            "revenue", "strategy", "plan", "growth", "innovation"
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in business_keywords if keyword in text_lower)
        score += min(keyword_count * 0.05, 0.3)
        
        # 结构评分
        if "?" in text:  # 包含问题
            score += 0.1
        if any(word in text_lower for word in ["how", "what", "why", "when", "where"]):
            score += 0.1
        
        return min(score, 1.0)
    
    async def merge_and_process_data(self):
        """合并和处理数据"""
        logger.info("🔄 合并和处理数据...")
        
        # 去重
        if self.config.get("data_integration", {}).get("enable_deduplication", True):
            self.deduplicate_data()
        
        # 质量过滤
        quality_threshold = self.config.get("data_integration", {}).get("quality_threshold", 0.7)
        self.integrated_data = [
            item for item in self.integrated_data 
            if item["quality_score"] >= quality_threshold
        ]
        
        # 保存到数据库
        self.save_to_database()
        
        # 导出为训练格式
        self.export_training_data()
    
    def deduplicate_data(self):
        """数据去重"""
        logger.info("🔍 执行数据去重...")
        
        seen_hashes = set()
        unique_data = []
        
        for item in self.integrated_data:
            content_hash = hashlib.md5(item["content"].encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                item["hash"] = content_hash
                unique_data.append(item)
        
        removed_count = len(self.integrated_data) - len(unique_data)
        self.integrated_data = unique_data
        
        logger.info(f"✅ 去重完成，移除 {removed_count} 个重复项")
    
    def save_to_database(self):
        """保存数据到数据库"""
        logger.info("💾 保存数据到数据库...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in self.integrated_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO training_data 
                    (source, content, quality_score, hash) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    item["source"],
                    item["content"],
                    item["quality_score"],
                    item.get("hash", "")
                ))
            except Exception as e:
                logger.warning(f"保存数据项失败: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ 已保存 {len(self.integrated_data)} 条数据到数据库")
    
    def export_training_data(self):
        """导出训练数据"""
        logger.info("📤 导出训练数据...")
        
        # 准备训练数据格式
        training_data = []
        for item in self.integrated_data:
            training_data.append({
                "text": item["content"],
                "source": item["source"],
                "quality_score": item["quality_score"]
            })
        
        # 保存为JSON
        output_file = self.data_dir / "integrated_training_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        # 保存为CSV
        df = pd.DataFrame(training_data)
        csv_file = self.data_dir / "integrated_training_data.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"✅ 训练数据已导出: {output_file}, {csv_file}")
    
    def generate_integration_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成集成报告"""
        total_samples = len(self.integrated_data)
        avg_quality = np.mean([item["quality_score"] for item in self.integrated_data]) if self.integrated_data else 0
        
        source_distribution = {}
        for item in self.integrated_data:
            source = item["source"]
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        report = {
            "integration_summary": {
                "total_samples": total_samples,
                "average_quality_score": round(avg_quality, 3),
                "source_distribution": source_distribution,
                "integration_time": datetime.now().isoformat()
            },
            "source_results": results,
            "data_quality": {
                "high_quality_samples": len([item for item in self.integrated_data if item["quality_score"] >= 0.8]),
                "medium_quality_samples": len([item for item in self.integrated_data if 0.6 <= item["quality_score"] < 0.8]),
                "low_quality_samples": len([item for item in self.integrated_data if item["quality_score"] < 0.6])
            }
        }
        
        # 保存报告
        report_file = self.data_dir / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 集成报告已生成: {report_file}")
        return report

async def main():
    """主函数"""
    # 加载配置
    config_file = "training_config_template.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        logger.error(f"配置文件 {config_file} 不存在")
        return
    
    # 创建集成服务
    service = FreeDataIntegrationService(config)
    
    # 执行集成
    report = await service.integrate_all_sources()
    
    print("🎉 数据集成完成！")
    print(f"📊 总样本数: {report['integration_summary']['total_samples']}")
    print(f"⭐ 平均质量分数: {report['integration_summary']['average_quality_score']}")

if __name__ == "__main__":
    asyncio.run(main())