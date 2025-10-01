"""
快速启动脚本 - AI产品训练数据自动收集系统
用于快速测试和验证整个数据收集系统
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickStartManager:
    """快速启动管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "collected_data"
        self.data_dir.mkdir(exist_ok=True)
        
    def check_environment(self) -> bool:
        """检查环境配置"""
        logger.info("🔍 检查环境配置...")
        
        # 检查.env文件
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            logger.warning("⚠️  .env文件不存在，将使用模拟数据模式")
            return False
        
        # 检查必要的Python包
        required_packages = [
            'requests', 'pandas', 'numpy', 'schedule', 'asyncio'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ 缺少必要的Python包: {', '.join(missing_packages)}")
            logger.info("请运行: pip install -r requirements.txt")
            return False
        
        logger.info("✅ 环境配置检查通过")
        return True
    
    def generate_sample_data(self, count: int = 1000) -> str:
        """生成示例数据用于测试"""
        logger.info(f"🎯 生成 {count} 条示例训练数据...")
        
        sample_data = []
        expert_types = [
            "business_strategy", "user_experience", "market_research", 
            "technical_analysis", "customer_service", "product_development"
        ]
        
        sources = [
            "reddit_business", "github_discussions", "twitter_insights",
            "producthunt_feedback", "huggingface_datasets"
        ]
        
        for i in range(count):
            # 生成示例文本内容
            texts = [
                f"Business strategy analysis for startup growth in {2024 + i % 5}. Key insights include market positioning, competitive analysis, and customer acquisition strategies.",
                f"User experience research findings show that {85 + i % 15}% of users prefer intuitive interfaces with minimal cognitive load and clear navigation patterns.",
                f"Market research indicates emerging trends in AI technology adoption, with {60 + i % 40}% of enterprises planning digital transformation initiatives.",
                f"Technical analysis of software architecture patterns reveals best practices for scalable system design and performance optimization.",
                f"Customer service excellence requires understanding user pain points and implementing proactive support strategies to improve satisfaction.",
                f"Product development lifecycle management involves iterative design, user feedback integration, and continuous improvement processes."
            ]
            
            item = {
                "text": texts[i % len(texts)],
                "expert_type": expert_types[i % len(expert_types)],
                "quality_score": 0.7 + (i % 30) / 100,  # 0.7-0.99
                "source": sources[i % len(sources)],
                "metadata": {
                    "generated": True,
                    "sample_id": i,
                    "created_at": datetime.now().isoformat()
                }
            }
            sample_data.append(item)
        
        # 保存示例数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"sample_training_data_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        # 生成统计报告
        stats = self.generate_sample_stats(sample_data)
        stats_file = self.data_dir / f"sample_stats_{timestamp}.json"
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 示例数据已生成: {output_file}")
        logger.info(f"📊 统计报告: {stats_file}")
        
        return str(output_file)
    
    def generate_sample_stats(self, data: list) -> dict:
        """生成示例数据统计"""
        stats = {
            "total_records": len(data),
            "generation_time": datetime.now().isoformat(),
            "data_type": "sample_data",
            "expert_type_distribution": {},
            "source_distribution": {},
            "quality_distribution": {
                "excellent": 0,  # >= 0.9
                "good": 0,       # >= 0.8
                "acceptable": 0  # >= 0.7
            },
            "average_quality_score": 0
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
            
            # 质量分布
            quality_scores = []
            for item in data:
                quality = item.get('quality_score', 0)
                quality_scores.append(quality)
                
                if quality >= 0.9:
                    stats["quality_distribution"]["excellent"] += 1
                elif quality >= 0.8:
                    stats["quality_distribution"]["good"] += 1
                elif quality >= 0.7:
                    stats["quality_distribution"]["acceptable"] += 1
            
            stats["average_quality_score"] = sum(quality_scores) / len(quality_scores)
        
        return stats
    
    def test_data_processing(self, data_file: str) -> bool:
        """测试数据处理功能"""
        logger.info("🧪 测试数据处理功能...")
        
        try:
            # 读取数据
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 基本验证
            assert isinstance(data, list), "数据应该是列表格式"
            assert len(data) > 0, "数据不能为空"
            
            # 检查数据结构
            required_fields = ['text', 'expert_type', 'quality_score', 'source']
            for i, item in enumerate(data[:10]):  # 检查前10条
                for field in required_fields:
                    assert field in item, f"记录 {i} 缺少字段: {field}"
            
            # 质量检查
            high_quality_count = sum(1 for item in data if item.get('quality_score', 0) >= 0.7)
            quality_ratio = high_quality_count / len(data)
            
            logger.info(f"✅ 数据处理测试通过")
            logger.info(f"📊 总记录数: {len(data)}")
            logger.info(f"🎯 高质量数据比例: {quality_ratio:.2%}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据处理测试失败: {str(e)}")
            return False
    
    def simulate_training_preparation(self, data_file: str) -> str:
        """模拟训练数据准备"""
        logger.info("🚀 模拟训练数据准备...")
        
        try:
            # 读取数据
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 过滤高质量数据
            high_quality_data = [
                item for item in data 
                if item.get('quality_score', 0) >= 0.8
            ]
            
            # 按专家类型分组
            grouped_data = {}
            for item in high_quality_data:
                expert_type = item.get('expert_type', 'unknown')
                if expert_type not in grouped_data:
                    grouped_data[expert_type] = []
                grouped_data[expert_type].append(item)
            
            # 生成训练格式数据
            training_data = []
            for expert_type, items in grouped_data.items():
                for item in items:
                    training_item = {
                        "input": item['text'],
                        "output": f"作为{expert_type}专家，我的分析是：{item['text'][:100]}...",
                        "expert_type": expert_type,
                        "quality_score": item['quality_score']
                    }
                    training_data.append(training_item)
            
            # 保存训练格式数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            training_file = self.data_dir / f"training_ready_data_{timestamp}.json"
            
            with open(training_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 训练数据准备完成: {training_file}")
            logger.info(f"🎯 可用于训练的数据: {len(training_data)} 条")
            logger.info(f"📋 专家类型覆盖: {list(grouped_data.keys())}")
            
            return str(training_file)
            
        except Exception as e:
            logger.error(f"❌ 训练数据准备失败: {str(e)}")
            return ""
    
    def run_quick_test(self):
        """运行快速测试"""
        logger.info("🚀 开始快速测试...")
        
        # 1. 检查环境
        env_ok = self.check_environment()
        
        # 2. 生成示例数据
        sample_file = self.generate_sample_data(2000)
        
        # 3. 测试数据处理
        if self.test_data_processing(sample_file):
            # 4. 模拟训练准备
            training_file = self.simulate_training_preparation(sample_file)
            
            if training_file:
                logger.info("🎉 快速测试完成！")
                logger.info("📁 生成的文件:")
                logger.info(f"   - 示例数据: {sample_file}")
                logger.info(f"   - 训练数据: {training_file}")
                logger.info("")
                logger.info("🎯 下一步:")
                if not env_ok:
                    logger.info("   1. 配置API密钥 (.env文件)")
                    logger.info("   2. 安装依赖包 (pip install -r requirements.txt)")
                logger.info("   3. 运行完整收集器 (python master_data_scheduler.py)")
                logger.info("   4. 部署到云服务器")
                
                return True
        
        logger.error("❌ 快速测试失败")
        return False

def main():
    """主函数"""
    print("🚀 AI产品训练数据自动收集系统 - 快速启动")
    print("=" * 50)
    
    manager = QuickStartManager()
    success = manager.run_quick_test()
    
    if success:
        print("\n✅ 系统就绪！可以开始大规模数据收集")
        print("📖 详细部署指南请查看: deployment_guide.md")
    else:
        print("\n❌ 系统配置需要调整，请检查错误信息")

if __name__ == "__main__":
    main()