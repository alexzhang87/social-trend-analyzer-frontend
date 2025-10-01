#!/usr/bin/env python3
"""
Free Data Collection Service for AI Advisor Model Training
Collects and processes training data from free open data sources
"""

import os
import sqlite3
import asyncio
import aiohttp
import aiofiles
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import ML libraries
from datasets import load_dataset
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from tqdm import tqdm
from loguru import logger

# Configure logging
logger.add("data_collection.log", rotation="10 MB", level="INFO")

@dataclass
class DataRecord:
    """Data record structure for training data"""
    id: str
    source: str
    category: str
    question: str
    answer: str
    quality_score: float
    business_relevance: float
    created_at: str
    metadata: Dict

class FreeDataCollectionService:
    """Service for collecting free training data from multiple sources"""
    
    def __init__(self, db_path: str = "training_data.db"):
        self.db_path = db_path
        self.session = None
        self.tokenizer = None
        self.business_keywords = [
            'business', 'startup', 'market', 'strategy', 'revenue', 'customer',
            'product', 'marketing', 'sales', 'growth', 'investment', 'funding',
            'competition', 'analysis', 'planning', 'management', 'consulting',
            'advice', 'recommendation', 'solution', 'opportunity', 'risk'
        ]
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing training data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create training_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    business_relevance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create data_sources table for tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_name TEXT PRIMARY KEY,
                    last_updated TEXT,
                    total_records INTEGER,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def init_session(self):
        """Initialize async HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
    
    def calculate_business_relevance(self, text: str) -> float:
        """Calculate business relevance score for text"""
        try:
            text_lower = text.lower()
            keyword_count = sum(1 for keyword in self.business_keywords if keyword in text_lower)
            max_score = len(self.business_keywords)
            relevance_score = min(keyword_count / max_score * 2, 1.0)  # Cap at 1.0
            return relevance_score
        except Exception as e:
            logger.warning(f"Business relevance calculation failed: {e}")
            return 0.0
    
    def calculate_quality_score(self, question: str, answer: str) -> float:
        """Calculate quality score based on text characteristics"""
        try:
            # Basic quality metrics
            q_len = len(question.split())
            a_len = len(answer.split())
            
            # Length score (prefer moderate lengths)
            len_score = 0.0
            if 5 <= q_len <= 50 and 10 <= a_len <= 500:
                len_score = 1.0
            elif 3 <= q_len <= 100 and 5 <= a_len <= 1000:
                len_score = 0.7
            else:
                len_score = 0.3
            
            # Completeness score
            completeness_score = 1.0 if answer.endswith(('.', '!', '?')) else 0.7
            
            # Professional language score (basic check)
            professional_score = 0.8 if any(word in answer.lower() for word in 
                                           ['recommend', 'suggest', 'consider', 'analyze', 'strategy']) else 0.5
            
            # Combined quality score
            quality_score = (len_score * 0.4 + completeness_score * 0.3 + professional_score * 0.3)
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            return 0.5
    
    def collect_huggingface_data(self, dataset_name: str, split: str = "train", max_samples: int = 1000) -> List[DataRecord]:
        """Collect data from Hugging Face datasets"""
        try:
            logger.info(f"Loading Hugging Face dataset: {dataset_name}")
            dataset = load_dataset(dataset_name, split=split, streaming=True)
            
            records = []
            count = 0
            
            for item in tqdm(dataset, desc=f"Processing {dataset_name}", total=max_samples):
                if count >= max_samples:
                    break
                
                # Extract question and answer based on dataset structure
                question, answer = self._extract_qa_from_item(item, dataset_name)
                
                if question and answer:
                    # Calculate scores
                    quality_score = self.calculate_quality_score(question, answer)
                    business_relevance = self.calculate_business_relevance(f"{question} {answer}")
                    
                    # Only keep high-quality, business-relevant data
                    if quality_score >= 0.5 and business_relevance >= 0.3:
                        record = DataRecord(
                            id=f"hf_{dataset_name}_{count}",
                            source=f"huggingface_{dataset_name}",
                            category=self._categorize_content(question, answer),
                            question=question,
                            answer=answer,
                            quality_score=quality_score,
                            business_relevance=business_relevance,
                            created_at=datetime.now().isoformat(),
                            metadata={"original_item": item}
                        )
                        records.append(record)
                
                count += 1
            
            logger.info(f"Collected {len(records)} records from {dataset_name}")
            return records
            
        except Exception as e:
            logger.error(f"Failed to collect data from {dataset_name}: {e}")
            return []
    
    def _extract_qa_from_item(self, item: Dict, dataset_name: str) -> Tuple[str, str]:
        """Extract question and answer from dataset item based on dataset structure"""
        try:
            # Common patterns for different datasets
            if "bitext" in dataset_name.lower():
                # Bitext customer support datasets
                question = item.get('instruction', '') or item.get('input', '')
                answer = item.get('response', '') or item.get('output', '')
            elif "lmsys" in dataset_name.lower():
                # LMSYS chat datasets
                if 'conversation' in item:
                    conv = item['conversation']
                    if len(conv) >= 2:
                        question = conv[0].get('content', '')
                        answer = conv[1].get('content', '')
                    else:
                        question, answer = '', ''
                else:
                    question = item.get('prompt', '') or item.get('instruction', '')
                    answer = item.get('response', '') or item.get('output', '')
            else:
                # Generic patterns
                question = (item.get('question', '') or 
                           item.get('instruction', '') or 
                           item.get('input', '') or 
                           item.get('prompt', ''))
                answer = (item.get('answer', '') or 
                         item.get('response', '') or 
                         item.get('output', '') or 
                         item.get('text', ''))
            
            return str(question).strip(), str(answer).strip()
            
        except Exception as e:
            logger.warning(f"Failed to extract Q&A from item: {e}")
            return '', ''
    
    def _categorize_content(self, question: str, answer: str) -> str:
        """Categorize content based on keywords"""
        text = f"{question} {answer}".lower()
        
        categories = {
            'business_strategy': ['strategy', 'planning', 'business model', 'competitive'],
            'market_analysis': ['market', 'analysis', 'research', 'trend', 'customer'],
            'product_management': ['product', 'feature', 'development', 'roadmap'],
            'technical_advice': ['technical', 'technology', 'implementation', 'system'],
            'customer_support': ['support', 'help', 'issue', 'problem', 'solution'],
            'general_business': ['business', 'company', 'management', 'advice']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def save_records_to_db(self, records: List[DataRecord]):
        """Save data records to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for record in records:
                cursor.execute('''
                    INSERT OR REPLACE INTO training_data 
                    (id, source, category, question, answer, quality_score, business_relevance, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.id,
                    record.source,
                    record.category,
                    record.question,
                    record.answer,
                    record.quality_score,
                    record.business_relevance,
                    record.created_at,
                    json.dumps(record.metadata)
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {len(records)} records to database")
            
        except Exception as e:
            logger.error(f"Failed to save records to database: {e}")
            raise
    
    def update_source_status(self, source_name: str, total_records: int, status: str = "completed"):
        """Update data source status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_sources 
                (source_name, last_updated, total_records, status)
                VALUES (?, ?, ?, ?)
            ''', (source_name, datetime.now().isoformat(), total_records, status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update source status: {e}")
    
    def get_training_data(self, category: Optional[str] = None, min_quality: float = 0.6, 
                         min_business_relevance: float = 0.4, limit: int = 1000) -> pd.DataFrame:
        """Retrieve training data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM training_data 
                WHERE quality_score >= ? AND business_relevance >= ?
            '''
            params = [min_quality, min_business_relevance]
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY quality_score DESC, business_relevance DESC LIMIT ?'
            params.append(limit)
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            logger.info(f"Retrieved {len(df)} training records")
            return df
            
        except Exception as e:
            logger.error(f"Failed to retrieve training data: {e}")
            return pd.DataFrame()
    
    def export_training_data(self, output_path: str, format: str = "jsonl"):
        """Export training data to file"""
        try:
            df = self.get_training_data()
            
            if format == "jsonl":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for _, row in df.iterrows():
                        record = {
                            "instruction": row['question'],
                            "output": row['answer'],
                            "category": row['category'],
                            "quality_score": row['quality_score'],
                            "business_relevance": row['business_relevance']
                        }
                        f.write(json.dumps(record, ensure_ascii=False) + '\n')
            elif format == "csv":
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"Exported training data to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
    
    def get_statistics(self) -> Dict:
        """Get collection statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM training_data")
            total_records = cursor.fetchone()[0]
            
            # Records by category
            cursor.execute("SELECT category, COUNT(*) FROM training_data GROUP BY category")
            category_stats = dict(cursor.fetchall())
            
            # Records by source
            cursor.execute("SELECT source, COUNT(*) FROM training_data GROUP BY source")
            source_stats = dict(cursor.fetchall())
            
            # Quality distribution
            cursor.execute("SELECT AVG(quality_score), AVG(business_relevance) FROM training_data")
            avg_quality, avg_relevance = cursor.fetchone()
            
            conn.close()
            
            stats = {
                "total_records": total_records,
                "category_distribution": category_stats,
                "source_distribution": source_stats,
                "average_quality_score": round(avg_quality or 0, 3),
                "average_business_relevance": round(avg_relevance or 0, 3)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

# Example usage and testing
async def main():
    """Main function for testing data collection"""
    service = FreeDataCollectionService()
    
    # Test with a small customer support dataset
    logger.info("Starting data collection test...")
    
    # Collect from Hugging Face customer support dataset
    try:
        records = service.collect_huggingface_data(
            "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
            max_samples=100
        )
        
        if records:
            service.save_records_to_db(records)
            service.update_source_status("bitext_customer_support", len(records))
            
            # Get statistics
            stats = service.get_statistics()
            logger.info(f"Collection statistics: {stats}")
            
            # Export sample data
            service.export_training_data("sample_training_data.jsonl")
            
        else:
            logger.warning("No records collected")
            
    except Exception as e:
        logger.error(f"Data collection test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())