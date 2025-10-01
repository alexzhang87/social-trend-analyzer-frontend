"""
免费训练数据收集服务
用于从各种免费数据源收集和处理AI顾问模型训练数据
"""

import asyncio
import aiohttp
import json
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from datasets import load_dataset
import sqlite3

logger = logging.getLogger(__name__)

class FreeDataCollectionService:
    """免费训练数据收集服务"""
    
    def __init__(self, data_dir: str = "training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "training_data.db"
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                domain TEXT,
                instruction TEXT NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                quality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT,
                last_updated TIMESTAMP,
                total_records INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        """)
        
        conn.commit()
        conn.close()
        
    async def collect_huggingface_data(self, dataset_name: str, split: str = "train") -> int:
        """
        从Hugging Face收集数据
        
        Args:
            dataset_name: 数据集名称，如 'bitext/Bitext-customer-support-llm-chatbot-training-dataset'
            split: 数据集分割，默认为 'train'
            
        Returns:
            收集到的记录数量
        """
        try:
            logger.info(f"开始收集Hugging Face数据集: {dataset_name}")
            
            # 加载数据集
            dataset = load_dataset(dataset_name, split=split)
            
            processed_count = 0
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in dataset:
                # 提取指令和响应
                instruction = item.get('instruction', item.get('input', ''))
                response = item.get('response', item.get('output', ''))
                
                if not instruction or not response:
                    continue
                
                # 数据质量检查
                if not self._is_quality_data(instruction, response):
                    continue
                
                # 分类商业领域
                domain = self._classify_business_domain(instruction + " " + response)
                
                # 计算质量分数
                quality_score = self._calculate_quality_score(instruction, response)
                
                # 存储到数据库
                cursor.execute("""
                    INSERT INTO conversations 
                    (source, domain, instruction, response, quality_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    dataset_name,
                    domain,
                    instruction,
                    response,
                    quality_score,
                    json.dumps({"original_item": item})
                ))
                
                processed_count += 1
                
                if processed_count % 1000 == 0:
                    logger.info(f"已处理 {processed_count} 条记录")
            
            conn.commit()
            conn.close()
            
            # 更新数据源记录
            self._update_data_source(dataset_name, processed_count)
            
            logger.info(f"完成收集 {dataset_name}，共 {processed_count} 条记录")
            return processed_count
            
        except Exception as e:
            logger.error(f"收集Hugging Face数据失败: {e}")
            return 0
    
    async def collect_stackoverflow_data(self, data_file_path: str) -> int:
        """
        收集Stack Overflow数据
        
        Args:
            data_file_path: Stack Overflow数据文件路径
            
        Returns:
            收集到的记录数量
        """
        try:
            logger.info(f"开始收集Stack Overflow数据: {data_file_path}")
            
            # 这里假设数据是CSV格式
            df = pd.read_csv(data_file_path)
            
            processed_count = 0
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                # 提取问题和答案
                question = row.get('Title', '') + " " + row.get('Body', '')
                answer = row.get('Answer', '')
                
                if not question or not answer:
                    continue
                
                # 过滤非商业相关内容
                if not self._is_business_related(question + " " + answer):
                    continue
                
                # 数据质量检查
                if not self._is_quality_data(question, answer):
                    continue
                
                domain = self._classify_business_domain(question + " " + answer)
                quality_score = self._calculate_quality_score(question, answer)
                
                cursor.execute("""
                    INSERT INTO conversations 
                    (source, domain, instruction, response, quality_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "stackoverflow",
                    domain,
                    question,
                    answer,
                    quality_score,
                    json.dumps({"question_id": row.get('Id', '')})
                ))
                
                processed_count += 1
                
                if processed_count % 1000 == 0:
                    logger.info(f"已处理 {processed_count} 条记录")
            
            conn.commit()
            conn.close()
            
            self._update_data_source("stackoverflow", processed_count)
            
            logger.info(f"完成收集Stack Overflow数据，共 {processed_count} 条记录")
            return processed_count
            
        except Exception as e:
            logger.error(f"收集Stack Overflow数据失败: {e}")
            return 0
    
    def _is_quality_data(self, instruction: str, response: str) -> bool:
        """检查数据质量"""
        # 长度检查
        if len(instruction) < 10 or len(response) < 20:
            return False
        
        if len(instruction) > 2000 or len(response) > 4000:
            return False
        
        # 内容检查
        banned_words = ['spam', 'advertisement', 'buy now', 'click here']
        text = (instruction + " " + response).lower()
        
        if any(word in text for word in banned_words):
            return False
        
        # 语言检查（简单的英文检查）
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        return True
    
    def _is_business_related(self, text: str) -> bool:
        """检查是否与商业相关"""
        business_keywords = [
            'business', 'startup', 'company', 'strategy', 'marketing', 
            'finance', 'investment', 'growth', 'revenue', 'profit',
            'customer', 'market', 'sales', 'management', 'entrepreneur',
            'funding', 'venture', 'business plan', 'roi', 'kpi'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in business_keywords)
    
    def _classify_business_domain(self, text: str) -> str:
        """分类商业领域"""
        domains = {
            'finance': ['finance', 'investment', 'funding', 'money', 'capital', 'loan', 'budget'],
            'marketing': ['marketing', 'promotion', 'brand', 'customer', 'advertising', 'social media'],
            'strategy': ['strategy', 'planning', 'development', 'competition', 'growth', 'expansion'],
            'operations': ['operations', 'management', 'process', 'efficiency', 'workflow', 'productivity'],
            'hr': ['human resources', 'hiring', 'employee', 'team', 'recruitment', 'training'],
            'technology': ['technology', 'software', 'digital', 'automation', 'ai', 'data'],
            'legal': ['legal', 'compliance', 'regulation', 'contract', 'intellectual property']
        }
        
        text_lower = text.lower()
        
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def _calculate_quality_score(self, instruction: str, response: str) -> float:
        """计算质量分数"""
        score = 0.5  # 基础分数
        
        # 长度合理性
        if 50 <= len(instruction) <= 500:
            score += 0.1
        if 100 <= len(response) <= 1000:
            score += 0.1
        
        # 结构化程度
        if '?' in instruction:  # 包含问号
            score += 0.1
        if any(word in response.lower() for word in ['because', 'therefore', 'however', 'first', 'second']):
            score += 0.1
        
        # 专业术语
        business_terms = ['roi', 'kpi', 'revenue', 'profit', 'market share', 'customer acquisition']
        if any(term in (instruction + response).lower() for term in business_terms):
            score += 0.2
        
        return min(score, 1.0)
    
    def _update_data_source(self, source_name: str, record_count: int):
        """更新数据源记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO data_sources 
            (name, last_updated, total_records)
            VALUES (?, ?, ?)
        """, (source_name, datetime.now(), record_count))
        
        conn.commit()
        conn.close()
    
    def get_training_data(self, domain: Optional[str] = None, 
                         min_quality: float = 0.6,
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取训练数据
        
        Args:
            domain: 指定领域，None表示所有领域
            min_quality: 最小质量分数
            limit: 限制返回数量
            
        Returns:
            训练数据列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT instruction, response, domain, quality_score, source
            FROM conversations 
            WHERE quality_score >= ?
        """
        params = [min_quality]
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        query += " ORDER BY quality_score DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'instruction': row[0],
                'response': row[1],
                'domain': row[2],
                'quality_score': row[3],
                'source': row[4]
            }
            for row in results
        ]
    
    def export_training_data(self, output_file: str, format: str = "jsonl"):
        """
        导出训练数据
        
        Args:
            output_file: 输出文件路径
            format: 输出格式，支持 'jsonl', 'csv', 'json'
        """
        data = self.get_training_data()
        
        if format == "jsonl":
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        elif format == "csv":
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False, encoding='utf-8')
        
        elif format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"训练数据已导出到: {output_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_records = cursor.fetchone()[0]
        
        # 按领域统计
        cursor.execute("""
            SELECT domain, COUNT(*) 
            FROM conversations 
            GROUP BY domain 
            ORDER BY COUNT(*) DESC
        """)
        domain_stats = dict(cursor.fetchall())
        
        # 按数据源统计
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM conversations 
            GROUP BY source 
            ORDER BY COUNT(*) DESC
        """)
        source_stats = dict(cursor.fetchall())
        
        # 质量分数分布
        cursor.execute("""
            SELECT 
                ROUND(quality_score, 1) as score_range,
                COUNT(*) 
            FROM conversations 
            GROUP BY ROUND(quality_score, 1)
            ORDER BY score_range
        """)
        quality_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_records': total_records,
            'domain_distribution': domain_stats,
            'source_distribution': source_stats,
            'quality_distribution': quality_stats
        }

# 使用示例
async def main():
    """主函数示例"""
    service = FreeDataCollectionService()
    
    # 收集Hugging Face数据
    await service.collect_huggingface_data(
        "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
    )
    
    # 获取统计信息
    stats = service.get_statistics()
    print("数据统计:", json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 导出训练数据
    service.export_training_data("training_data.jsonl", "jsonl")

if __name__ == "__main__":
    asyncio.run(main())