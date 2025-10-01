"""
主数据收集调度器
整合API数据收集和Hugging Face数据集，实现大规模自动化数据收集
"""

import os
import json
import asyncio
import schedule
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
import sqlite3
from pathlib import Path

# 导入自定义收集器
from enterprise_data_collector import EnterpriseDataCollector
from huggingface_data_integrator import HuggingFaceDataIntegrator
from health_server import start_health_server

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterDataScheduler:
    """主数据收集调度器"""
    
    def __init__(self, data_dir: str = "collected_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化收集器
        self.enterprise_collector = EnterpriseDataCollector()
        self.hf_integrator = HuggingFaceDataIntegrator(
            output_dir=os.path.join(data_dir, "huggingface_data")
        )
        
        # 数据库文件
        self.db_path = os.path.join(data_dir, "collection_tracking.db")
        self.init_database()
        
        # 收集目标配置
        self.collection_targets = {
            "daily_api_target": 5000,  # 每日API数据目标
            "weekly_hf_target": 20000,  # 每周Hugging Face数据目标
            "quality_threshold": 0.7,   # 质量阈值
            "max_storage_days": 30      # 数据保存天数
        }
        
        # 收集状态
        self.collection_status = {
            "last_api_collection": None,
            "last_hf_collection": None,
            "total_collected": 0,
            "high_quality_count": 0
        }
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建收集记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_type TEXT NOT NULL,
                collection_date DATE NOT NULL,
                records_collected INTEGER NOT NULL,
                high_quality_count INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建数据质量统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                source TEXT NOT NULL,
                expert_type TEXT NOT NULL,
                avg_quality_score REAL NOT NULL,
                record_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_collection(self, collection_type: str, records_collected: int, 
                         high_quality_count: int, file_path: str, status: str):
        """记录收集结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO collection_records 
            (collection_type, collection_date, records_collected, high_quality_count, file_path, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (collection_type, datetime.now().date(), records_collected, 
              high_quality_count, file_path, status))
        
        conn.commit()
        conn.close()
    
    async def run_api_collection(self) -> Dict[str, Any]:
        """运行API数据收集"""
        logger.info("🚀 开始API数据收集...")
        
        try:
            # 运行企业级数据收集
            result = await self.enterprise_collector.run_daily_collection()
            
            # 记录收集结果
            self.record_collection(
                collection_type="api",
                records_collected=result.get("total_collected", 0),
                high_quality_count=result.get("high_quality_count", 0),
                file_path=result.get("output_file", ""),
                status="success"
            )
            
            self.collection_status["last_api_collection"] = datetime.now()
            
            logger.info(f"✅ API数据收集完成: {result.get('total_collected', 0)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"❌ API数据收集失败: {str(e)}")
            self.record_collection("api", 0, 0, "", "failed")
            return {"error": str(e)}
    
    async def run_hf_collection(self) -> Dict[str, Any]:
        """运行Hugging Face数据收集"""
        logger.info("🚀 开始Hugging Face数据收集...")
        
        try:
            # 运行Hugging Face数据集成
            merged_file = await self.hf_integrator.run_integration(max_samples_per_dataset=5000)
            
            # 读取统计信息
            stats_file = merged_file.replace("_merged_data_", "_stats_")
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            total_records = stats.get("total_records", 0)
            high_quality_count = sum(1 for item in json.load(open(merged_file, 'r', encoding='utf-8'))
                                   if item.get("quality_score", 0) >= self.collection_targets["quality_threshold"])
            
            # 记录收集结果
            self.record_collection(
                collection_type="huggingface",
                records_collected=total_records,
                high_quality_count=high_quality_count,
                file_path=merged_file,
                status="success"
            )
            
            self.collection_status["last_hf_collection"] = datetime.now()
            
            logger.info(f"✅ Hugging Face数据收集完成: {total_records} 条记录")
            return {"total_collected": total_records, "output_file": merged_file}
            
        except Exception as e:
            logger.error(f"❌ Hugging Face数据收集失败: {str(e)}")
            self.record_collection("huggingface", 0, 0, "", "failed")
            return {"error": str(e)}
    
    def merge_all_collected_data(self) -> str:
        """合并所有收集的数据"""
        logger.info("🔄 开始合并所有收集的数据...")
        
        all_data = []
        
        # 查找所有数据文件
        data_files = []
        
        # API数据文件
        for file in os.listdir(self.data_dir):
            if file.startswith("api_data_") and file.endswith(".json"):
                data_files.append(os.path.join(self.data_dir, file))
        
        # Hugging Face数据文件
        hf_dir = os.path.join(self.data_dir, "huggingface_data")
        if os.path.exists(hf_dir):
            for file in os.listdir(hf_dir):
                if file.startswith("huggingface_merged_data_") and file.endswith(".json"):
                    data_files.append(os.path.join(hf_dir, file))
        
        # 合并数据
        for file_path in data_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    logger.info(f"已合并文件: {file_path} ({len(data)} 条记录)")
            except Exception as e:
                logger.warning(f"合并文件 {file_path} 时出错: {str(e)}")
        
        # 去重和质量过滤
        unique_data = []
        seen_texts = set()
        
        for item in all_data:
            text = item.get("text", "")
            if text and text not in seen_texts and item.get("quality_score", 0) >= 0.6:
                seen_texts.add(text)
                unique_data.append(item)
        
        # 按质量分数排序
        unique_data.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        # 保存合并后的数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_file = os.path.join(self.data_dir, f"master_training_data_{timestamp}.json")
        
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2)
        
        # 生成最终统计报告
        stats = self.generate_final_stats(unique_data)
        stats_file = os.path.join(self.data_dir, f"master_stats_{timestamp}.json")
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 数据合并完成!")
        logger.info(f"📁 最终训练数据: {merged_file}")
        logger.info(f"📊 统计报告: {stats_file}")
        logger.info(f"🎯 总计 {len(unique_data)} 条高质量训练数据")
        
        return merged_file
    
    def generate_final_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成最终统计报告"""
        stats = {
            "total_records": len(data),
            "generation_time": datetime.now().isoformat(),
            "expert_type_distribution": {},
            "source_distribution": {},
            "quality_distribution": {
                "excellent": 0,  # >= 0.9
                "good": 0,       # >= 0.8
                "acceptable": 0  # >= 0.7
            },
            "data_sources": {
                "api_sources": 0,
                "huggingface_sources": 0
            }
        }
        
        if data:
            # 专家类型分布
            expert_types = [item.get('expert_type', 'unknown') for item in data]
            for expert_type in set(expert_types):
                stats["expert_type_distribution"][expert_type] = expert_types.count(expert_type)
            
            # 数据源分布
            sources = [item.get('source', 'unknown') for item in data]
            for source in set(sources):
                stats["source_distribution"][source] = sources.count(source)
                
                # 统计API vs Hugging Face来源
                if 'huggingface' in source:
                    stats["data_sources"]["huggingface_sources"] += sources.count(source)
                else:
                    stats["data_sources"]["api_sources"] += sources.count(source)
            
            # 质量分布
            for item in data:
                quality = item.get('quality_score', 0)
                if quality >= 0.9:
                    stats["quality_distribution"]["excellent"] += 1
                elif quality >= 0.8:
                    stats["quality_distribution"]["good"] += 1
                elif quality >= 0.7:
                    stats["quality_distribution"]["acceptable"] += 1
        
        return stats
    
    def cleanup_old_data(self):
        """清理旧数据"""
        logger.info("🧹 开始清理旧数据...")
        
        cutoff_date = datetime.now() - timedelta(days=self.collection_targets["max_storage_days"])
        
        for file in os.listdir(self.data_dir):
            if file.endswith('.json'):
                file_path = os.path.join(self.data_dir, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"已删除旧文件: {file}")
    
    async def daily_collection_job(self):
        """每日收集任务"""
        logger.info("📅 开始执行每日数据收集任务")
        
        # 运行API收集
        api_result = await self.run_api_collection()
        
        # 每周运行一次Hugging Face收集
        if datetime.now().weekday() == 0:  # 周一
            hf_result = await self.run_hf_collection()
        
        # 合并数据
        merged_file = self.merge_all_collected_data()
        
        # 清理旧数据
        self.cleanup_old_data()
        
        logger.info("✅ 每日数据收集任务完成")
    
    def start_scheduler(self):
        """启动调度器"""
        logger.info("🚀 启动主数据收集调度器")
        
        # 设置定时任务
        schedule.every().day.at("02:00").do(lambda: asyncio.run(self.daily_collection_job()))
        schedule.every().hour.do(lambda: asyncio.run(self.run_api_collection()))  # 每小时收集API数据
        
        logger.info("⏰ 调度器已启动，等待执行...")
        logger.info("📋 调度计划:")
        logger.info("   - 每小时: API数据收集")
        logger.info("   - 每日02:00: 完整数据收集和合并")
        logger.info("   - 每周一: Hugging Face数据集成")
        
        # 立即执行一次收集
        logger.info("🎯 立即执行一次完整数据收集...")
        asyncio.run(self.daily_collection_job())
        
        # 持续运行调度器
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

async def main():
    """主函数"""
    # 启动健康检查服务器
    port = int(os.getenv("PORT", 8000))
    health_server = start_health_server(port)
    logger.info(f"🏥 健康检查服务器已启动在端口 {port}")
    
    scheduler = MasterDataScheduler()
    
    print("🚀 主数据收集调度器启动")
    print("📊 目标配置:")
    print(f"   - 每日API数据目标: {scheduler.collection_targets['daily_api_target']} 条")
    print(f"   - 每周HF数据目标: {scheduler.collection_targets['weekly_hf_target']} 条")
    print(f"   - 质量阈值: {scheduler.collection_targets['quality_threshold']}")
    print(f"🏥 健康检查端点: http://0.0.0.0:{port}/health")
    print()
    
    # 启动调度器
    scheduler.start_scheduler()

if __name__ == "__main__":
    asyncio.run(main())