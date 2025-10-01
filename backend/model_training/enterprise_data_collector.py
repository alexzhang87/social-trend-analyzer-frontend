#!/usr/bin/env python3
"""
企业级自动化数据收集系统
目标：每天收集数万条真实数据，支持云端24/7运行
作者：AI助手
创建时间：2024-12-30
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import schedule
import aiohttp
import pandas as pd
from dataclasses import dataclass
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DataCollectionTarget:
    """数据收集目标配置"""
    platform: str
    daily_target: int  # 每日目标数据量
    priority: int  # 优先级 1-5
    enabled: bool = True

@dataclass
class CollectedData:
    """收集到的数据结构"""
    text: str
    expert_type: str
    quality_score: float
    source: str
    metadata: Dict
    timestamp: datetime
    data_id: str

class EnterpriseDataCollector:
    """企业级数据收集器"""
    
    def __init__(self):
        self.load_config()
        self.setup_database()
        self.setup_collectors()
        self.running = False
        self.daily_stats = {}
        
        # 数据收集目标（每日）
        self.collection_targets = [
            DataCollectionTarget("reddit", 5000, 1),      # Reddit: 5000条/天
            DataCollectionTarget("github", 3000, 2),      # GitHub: 3000条/天  
            DataCollectionTarget("twitter", 2000, 3),     # Twitter: 2000条/天
            DataCollectionTarget("product_hunt", 500, 4), # Product Hunt: 500条/天
            DataCollectionTarget("google_trends", 1000, 5) # Google Trends: 1000条/天
        ]
        
        logger.info("企业级数据收集系统初始化完成")
        logger.info(f"每日目标总数据量: {sum(t.daily_target for t in self.collection_targets)}条")

    def load_config(self):
        """加载配置"""
        try:
            # 获取当前文件的绝对路径
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            backend_dir = os.path.dirname(current_dir)
            env_path = os.path.join(backend_dir, '.env')
            
            logger.info(f"尝试加载环境变量文件: {env_path}")
            
            if os.path.exists(env_path):
                from dotenv import load_dotenv
                load_dotenv(env_path)
                logger.info("环境变量加载成功")
            else:
                logger.warning(f"环境变量文件未找到: {env_path}")
                
        except Exception as e:
            logger.error(f"加载配置失败: {e}")

    def setup_database(self):
        """设置数据库"""
        self.db_path = "enterprise_data_collection.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collected_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_id TEXT UNIQUE,
                text TEXT NOT NULL,
                expert_type TEXT NOT NULL,
                quality_score REAL,
                source TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                platform TEXT,
                collected_count INTEGER,
                target_count INTEGER,
                success_rate REAL,
                timestamp DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")

    def setup_collectors(self):
        """设置各平台收集器"""
        from reddit_collector import RedditCollector
        from github_collector import GitHubCollector
        from twitter_collector import TwitterCollector
        from product_hunt_collector import ProductHuntCollector
        from google_trends_collector import GoogleTrendsCollector
        
        self.collectors = {
            'reddit': RedditCollector(),
            'github': GitHubCollector(),
            'twitter': TwitterCollector(),
            'product_hunt': ProductHuntCollector(),
            'google_trends': GoogleTrendsCollector()
        }
        
        logger.info("所有平台收集器初始化完成")

    async def collect_daily_data(self):
        """执行每日数据收集任务"""
        logger.info("开始执行每日数据收集任务")
        start_time = datetime.now()
        
        total_collected = 0
        collection_results = {}
        
        # 并行收集各平台数据
        tasks = []
        for target in self.collection_targets:
            if target.enabled:
                task = asyncio.create_task(
                    self.collect_platform_data(target)
                )
                tasks.append((target.platform, task))
        
        # 等待所有任务完成
        for platform, task in tasks:
            try:
                collected_count = await task
                collection_results[platform] = collected_count
                total_collected += collected_count
                logger.info(f"{platform}平台收集完成: {collected_count}条数据")
            except Exception as e:
                logger.error(f"{platform}平台收集失败: {e}")
                collection_results[platform] = 0
        
        # 记录统计信息
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.save_daily_stats(collection_results, start_time)
        
        logger.info(f"每日数据收集完成!")
        logger.info(f"总收集数据量: {total_collected}条")
        logger.info(f"耗时: {duration}")
        
        # 触发数据处理
        await self.process_collected_data()
        
        return total_collected

    async def collect_platform_data(self, target: DataCollectionTarget) -> int:
        """收集指定平台的数据"""
        platform = target.platform
        daily_target = target.daily_target
        
        logger.info(f"开始收集{platform}平台数据，目标: {daily_target}条")
        
        collector = self.collectors.get(platform)
        if not collector:
            logger.error(f"未找到{platform}平台的收集器")
            return 0
        
        collected_data = []
        batch_size = min(100, daily_target // 10)  # 分批收集
        
        for batch_num in range(0, daily_target, batch_size):
            try:
                current_batch_size = min(batch_size, daily_target - batch_num)
                batch_data = await collector.collect_batch(current_batch_size)
                
                if batch_data:
                    collected_data.extend(batch_data)
                    logger.info(f"{platform}: 已收集 {len(collected_data)}/{daily_target} 条数据")
                
                # 避免触发API限制
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"{platform}批次收集失败: {e}")
                await asyncio.sleep(5)  # 错误后等待更长时间
        
        # 保存收集到的数据
        saved_count = self.save_collected_data(collected_data)
        logger.info(f"{platform}平台数据保存完成: {saved_count}条")
        
        return saved_count

    def save_collected_data(self, data_list: List[CollectedData]) -> int:
        """保存收集到的数据"""
        if not data_list:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for data in data_list:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO collected_data 
                    (data_id, text, expert_type, quality_score, source, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.data_id,
                    data.text,
                    data.expert_type,
                    data.quality_score,
                    data.source,
                    json.dumps(data.metadata),
                    data.timestamp
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                logger.error(f"保存数据失败: {e}")
        
        conn.commit()
        conn.close()
        
        return saved_count

    def save_daily_stats(self, results: Dict[str, int], timestamp: datetime):
        """保存每日统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_str = timestamp.date()
        
        for target in self.collection_targets:
            platform = target.platform
            collected = results.get(platform, 0)
            target_count = target.daily_target
            success_rate = collected / target_count if target_count > 0 else 0
            
            cursor.execute('''
                INSERT INTO collection_stats 
                (date, platform, collected_count, target_count, success_rate, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date_str, platform, collected, target_count, success_rate, timestamp))
        
        conn.commit()
        conn.close()

    async def process_collected_data(self):
        """处理收集到的数据（清洗、标注、质量评估）"""
        logger.info("开始处理收集到的数据")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取未处理的数据
        cursor.execute('''
            SELECT id, text, expert_type, source, metadata 
            FROM collected_data 
            WHERE processed = FALSE
        ''')
        
        unprocessed_data = cursor.fetchall()
        logger.info(f"待处理数据量: {len(unprocessed_data)}条")
        
        processed_count = 0
        for row in unprocessed_data:
            data_id, text, expert_type, source, metadata = row
            
            try:
                # 数据清洗
                cleaned_text = self.clean_text(text)
                
                # 重新评估专家类型
                refined_expert_type = self.refine_expert_type(cleaned_text, expert_type)
                
                # 重新计算质量分数
                quality_score = self.calculate_quality_score(cleaned_text, source)
                
                # 更新数据库
                cursor.execute('''
                    UPDATE collected_data 
                    SET text = ?, expert_type = ?, quality_score = ?, processed = TRUE
                    WHERE id = ?
                ''', (cleaned_text, refined_expert_type, quality_score, data_id))
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"处理数据失败 (ID: {data_id}): {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"数据处理完成: {processed_count}条")

    def clean_text(self, text: str) -> str:
        """清洗文本数据"""
        import re
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符但保留基本标点
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # 限制长度
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        return text

    def refine_expert_type(self, text: str, current_type: str) -> str:
        """优化专家类型分类"""
        text_lower = text.lower()
        
        # 关键词映射
        keyword_mapping = {
            'business_strategy': ['strategy', 'business', 'market', 'competition', 'revenue', 'growth'],
            'data_insight': ['data', 'analytics', 'metrics', 'analysis', 'statistics', 'insights'],
            'user_insight': ['user', 'customer', 'feedback', 'experience', 'behavior', 'satisfaction'],
            'competitive_intelligence': ['competitor', 'competitive', 'market share', 'benchmark'],
            'failure_prevention': ['risk', 'failure', 'problem', 'issue', 'mistake', 'avoid']
        }
        
        # 计算每个类型的匹配分数
        scores = {}
        for expert_type, keywords in keyword_mapping.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[expert_type] = score
        
        # 如果有更好的匹配，则更新类型
        best_type = max(scores, key=scores.get)
        if scores[best_type] > scores.get(current_type, 0):
            return best_type
        
        return current_type

    def calculate_quality_score(self, text: str, source: str) -> float:
        """计算数据质量分数"""
        score = 0.5  # 基础分数
        
        # 长度评分
        if 50 <= len(text) <= 1000:
            score += 0.2
        elif len(text) > 1000:
            score += 0.1
        
        # 来源评分
        source_scores = {
            'reddit': 0.15,
            'github': 0.2,
            'twitter': 0.1,
            'product_hunt': 0.15,
            'google_trends': 0.1
        }
        score += source_scores.get(source, 0.05)
        
        # 内容质量评分
        if any(word in text.lower() for word in ['detailed', 'analysis', 'insight', 'strategy']):
            score += 0.1
        
        return min(1.0, score)

    def export_training_data(self, output_file: str = None) -> str:
        """导出训练数据"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"enterprise_training_data_{timestamp}.json"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT text, expert_type, quality_score, source, metadata, timestamp
            FROM collected_data 
            WHERE processed = TRUE AND quality_score >= 0.6
            ORDER BY quality_score DESC, timestamp DESC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        # 转换为训练格式
        training_data = []
        for row in data:
            text, expert_type, quality_score, source, metadata, timestamp = row
            training_data.append({
                'text': text,
                'expert_type': expert_type,
                'quality_score': quality_score,
                'source': source,
                'metadata': json.loads(metadata) if metadata else {},
                'timestamp': timestamp
            })
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"训练数据导出完成: {output_file}")
        logger.info(f"数据量: {len(training_data)}条")
        
        return output_file

    def get_collection_stats(self, days: int = 7) -> Dict:
        """获取收集统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最近N天的统计
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        cursor.execute('''
            SELECT platform, SUM(collected_count) as total_collected, 
                   SUM(target_count) as total_target,
                   AVG(success_rate) as avg_success_rate
            FROM collection_stats 
            WHERE date >= ?
            GROUP BY platform
        ''', (start_date,))
        
        platform_stats = cursor.fetchall()
        
        # 获取总体数据量
        cursor.execute('''
            SELECT COUNT(*) as total_records,
                   AVG(quality_score) as avg_quality,
                   COUNT(DISTINCT source) as unique_sources
            FROM collected_data 
            WHERE processed = TRUE
        ''')
        
        overall_stats = cursor.fetchone()
        conn.close()
        
        return {
            'platform_stats': platform_stats,
            'overall_stats': overall_stats,
            'period_days': days
        }

    def start_scheduler(self):
        """启动调度器"""
        logger.info("启动企业级数据收集调度器")
        
        # 每天凌晨2点执行数据收集
        schedule.every().day.at("02:00").do(
            lambda: asyncio.run(self.collect_daily_data())
        )
        
        # 每6小时执行一次小规模收集
        schedule.every(6).hours.do(
            lambda: asyncio.run(self.collect_incremental_data())
        )
        
        # 每天晚上11点导出训练数据
        schedule.every().day.at("23:00").do(self.export_training_data)
        
        self.running = True
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    async def collect_incremental_data(self):
        """增量数据收集（每6小时）"""
        logger.info("执行增量数据收集")
        
        # 减少目标量，避免API限制
        for target in self.collection_targets:
            target.daily_target = target.daily_target // 4  # 1/4的量
        
        await self.collect_daily_data()
        
        # 恢复原始目标
        for target in self.collection_targets:
            target.daily_target = target.daily_target * 4

    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        logger.info("数据收集调度器已停止")

def main():
    """主函数"""
    collector = EnterpriseDataCollector()
    
    try:
        # 立即执行一次数据收集测试
        logger.info("执行初始数据收集测试...")
        asyncio.run(collector.collect_daily_data())
        
        # 导出当前数据
        output_file = collector.export_training_data()
        
        # 显示统计信息
        stats = collector.get_collection_stats()
        logger.info(f"收集统计: {stats}")
        
        # 启动调度器（用于生产环境）
        # collector.start_scheduler()
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在停止...")
        collector.stop_scheduler()
    except Exception as e:
        logger.error(f"系统错误: {e}")

if __name__ == "__main__":
    main()