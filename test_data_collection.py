#!/usr/bin/env python3
"""
离线测试数据收集服务
使用模拟数据验证数据收集管道的功能
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
import json

# 模拟的训练数据
MOCK_CUSTOMER_SUPPORT_DATA = [
    {
        "instruction": "客户询问产品退货政策",
        "input": "我想了解你们的退货政策，买了产品不满意可以退吗？",
        "output": "我们提供30天无理由退货服务。您可以在收到商品后30天内申请退货，商品需保持原包装和标签完整。退货流程：1）联系客服申请退货单号 2）按照退货地址寄回商品 3）我们收到商品后3-5个工作日内处理退款。",
        "category": "customer_support",
        "business_relevance": 0.95,
        "quality_score": 0.92
    },
    {
        "instruction": "客户咨询产品功能",
        "input": "这个产品有什么主要功能？适合什么场景使用？",
        "output": "我们的产品主要功能包括：1）智能数据分析 2）自动化报告生成 3）多维度可视化展示 4）实时监控预警。适用场景：企业数据分析、市场研究、业务决策支持、运营监控等。特别适合需要快速获取数据洞察的中小企业。",
        "category": "product_consultation",
        "business_relevance": 0.88,
        "quality_score": 0.85
    },
    {
        "instruction": "技术支持咨询",
        "input": "系统登录不了，提示密码错误，但我确定密码是对的",
        "output": "遇到登录问题，请按以下步骤排查：1）确认用户名和密码输入正确，注意大小写 2）清除浏览器缓存和Cookie 3）尝试重置密码 4）检查网络连接是否正常 5）如果问题持续，请提供错误截图，我们技术团队会进一步协助。",
        "category": "technical_support",
        "business_relevance": 0.82,
        "quality_score": 0.88
    },
    {
        "instruction": "客户服务质量提升",
        "input": "如何提升客户服务质量和用户满意度？",
        "output": "提升客户服务质量的关键措施：1）建立完善的客服培训体系，提升专业技能 2）优化服务流程，缩短响应时间 3）建立客户反馈机制，及时收集改进建议 4）使用智能客服系统，提高服务效率 5）定期进行客户满意度调研，持续优化服务体验。",
        "category": "customer_support",
        "business_relevance": 0.90,
        "quality_score": 0.89
    },
    {
        "instruction": "产品用户体验优化",
        "input": "用户反馈产品界面复杂，如何优化用户体验？",
        "output": "用户体验优化建议：1）简化界面设计，突出核心功能 2）优化信息架构，减少用户认知负担 3）增加新手引导和帮助文档 4）进行用户测试，收集真实使用反馈 5）采用响应式设计，适配不同设备 6）持续迭代优化，基于数据驱动改进。",
        "category": "product_consultation",
        "business_relevance": 0.93,
        "quality_score": 0.91
    }
]

MOCK_BUSINESS_STRATEGY_DATA = [
    {
        "instruction": "市场进入策略分析",
        "input": "我们是一家SaaS公司，想进入东南亚市场，应该如何制定进入策略？",
        "output": "东南亚SaaS市场进入策略建议：1）市场调研：重点关注新加坡、泰国、印尼等核心市场的数字化程度和竞争格局 2）本地化策略：产品界面多语言支持、符合当地法规要求 3）合作伙伴：寻找当地系统集成商或渠道伙伴 4）定价策略：考虑当地购买力，采用灵活定价模式 5）营销渠道：数字营销为主，参加当地行业展会建立品牌知名度。",
        "category": "business_strategy",
        "business_relevance": 0.95,
        "quality_score": 0.90
    },
    {
        "instruction": "产品定位分析",
        "input": "我们的产品在竞争激烈的市场中如何找到差异化定位？",
        "output": "差异化定位策略：1）深度用户调研：了解目标用户未被满足的需求痛点 2）竞品分析：识别竞争对手的功能空白和服务短板 3）核心价值主张：基于用户痛点和竞品空白，确定独特价值 4）功能差异化：在核心功能基础上增加独特特性 5）服务差异化：提供更好的客户体验和售后服务 6）品牌差异化：建立独特的品牌形象和价值观。",
        "category": "product_strategy",
        "business_relevance": 0.92,
        "quality_score": 0.87
    },
    {
        "instruction": "新市场开拓策略",
        "input": "初创公司如何制定有效的市场开拓策略？",
        "output": "初创公司市场开拓策略：1）精准定位目标市场：选择细分市场，避免与大公司正面竞争 2）MVP验证：快速推出最小可行产品，验证市场需求 3）种子用户培养：重点服务早期用户，建立口碑传播 4）低成本营销：利用社交媒体、内容营销等成本效益高的渠道 5）合作伙伴关系：与互补企业建立战略合作 6）数据驱动决策：持续收集用户反馈，快速迭代优化。",
        "category": "business_strategy",
        "business_relevance": 0.94,
        "quality_score": 0.88
    },
    {
        "instruction": "产品功能规划",
        "input": "如何规划产品功能优先级和开发路线图？",
        "output": "产品功能规划方法：1）用户需求分析：通过用户调研、数据分析确定核心需求 2）价值评估：评估功能对用户价值和商业价值的贡献 3）技术可行性：评估开发难度和资源需求 4）竞争分析：了解竞品功能布局，找到差异化机会 5）优先级矩阵：使用RICE模型（Reach、Impact、Confidence、Effort）排序 6）敏捷迭代：制定短期冲刺计划，保持灵活调整能力。",
        "category": "product_strategy",
        "business_relevance": 0.91,
        "quality_score": 0.86
    }
]

class TestDataCollectionService:
    def __init__(self, db_path: str = "test_training_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化测试数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                instruction TEXT NOT NULL,
                input_text TEXT,
                output_text TEXT NOT NULL,
                business_relevance REAL,
                quality_score REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT UNIQUE NOT NULL,
                source_type TEXT NOT NULL,
                last_updated TIMESTAMP,
                total_records INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"测试数据库初始化完成: {self.db_path}")
    
    def save_mock_data(self, data_list: List[Dict], source_name: str):
        """保存模拟数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for item in data_list:
            try:
                cursor.execute('''
                    INSERT INTO training_data 
                    (source, category, instruction, input_text, output_text, 
                     business_relevance, quality_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    source_name,
                    item['category'],
                    item['instruction'],
                    item['input'],
                    item['output'],
                    item['business_relevance'],
                    item['quality_score'],
                    json.dumps({"test_data": True})
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"保存数据失败: {e}")
        
        # 更新数据源状态
        cursor.execute('''
            INSERT OR REPLACE INTO data_sources 
            (source_name, source_type, last_updated, total_records, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_name, "mock_data", datetime.now(), saved_count, "active"))
        
        conn.commit()
        conn.close()
        
        logger.info(f"成功保存 {saved_count} 条模拟数据到 {source_name}")
        return saved_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM training_data")
        total_records = cursor.fetchone()[0]
        
        # 按类别统计
        cursor.execute("""
            SELECT category, COUNT(*) as count, 
                   AVG(business_relevance) as avg_relevance,
                   AVG(quality_score) as avg_quality
            FROM training_data 
            GROUP BY category
        """)
        category_stats = cursor.fetchall()
        
        # 按数据源统计
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM training_data 
            GROUP BY source
        """)
        source_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_records": total_records,
            "category_stats": [
                {
                    "category": row[0],
                    "count": row[1],
                    "avg_business_relevance": round(row[2], 3),
                    "avg_quality_score": round(row[3], 3)
                }
                for row in category_stats
            ],
            "source_stats": [
                {"source": row[0], "count": row[1]}
                for row in source_stats
            ]
        }
    
    def export_training_data(self, min_quality: float = 0.7) -> List[Dict]:
        """导出训练数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT instruction, input_text, output_text, category, 
                   business_relevance, quality_score
            FROM training_data 
            WHERE quality_score >= ?
            ORDER BY quality_score DESC, business_relevance DESC
        """, (min_quality,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "instruction": row[0],
                "input": row[1],
                "output": row[2],
                "category": row[3],
                "business_relevance": row[4],
                "quality_score": row[5]
            }
            for row in results
        ]

def main():
    """主测试函数"""
    logger.info("开始测试数据收集服务...")
    
    # 创建测试服务实例
    test_service = TestDataCollectionService()
    
    # 保存模拟的客户支持数据
    logger.info("保存客户支持模拟数据...")
    test_service.save_mock_data(MOCK_CUSTOMER_SUPPORT_DATA, "mock_customer_support")
    
    # 保存模拟的商业策略数据
    logger.info("保存商业策略模拟数据...")
    test_service.save_mock_data(MOCK_BUSINESS_STRATEGY_DATA, "mock_business_strategy")
    
    # 获取统计信息
    logger.info("获取数据统计信息...")
    stats = test_service.get_statistics()
    
    print("\n" + "="*50)
    print("数据收集测试结果")
    print("="*50)
    print(f"总记录数: {stats['total_records']}")
    
    print("\n按类别统计:")
    for cat_stat in stats['category_stats']:
        print(f"  {cat_stat['category']}: {cat_stat['count']} 条")
        print(f"    平均业务相关性: {cat_stat['avg_business_relevance']}")
        print(f"    平均质量分数: {cat_stat['avg_quality_score']}")
    
    print("\n按数据源统计:")
    for source_stat in stats['source_stats']:
        print(f"  {source_stat['source']}: {source_stat['count']} 条")
    
    # 导出高质量训练数据
    logger.info("导出高质量训练数据...")
    training_data = test_service.export_training_data(min_quality=0.8)
    
    print(f"\n高质量训练数据 (质量分数 >= 0.8): {len(training_data)} 条")
    
    # 显示样本数据
    if training_data:
        print("\n样本训练数据:")
        sample = training_data[0]
        print(f"指令: {sample['instruction']}")
        print(f"输入: {sample['input'][:100]}...")
        print(f"输出: {sample['output'][:100]}...")
        print(f"类别: {sample['category']}")
        print(f"业务相关性: {sample['business_relevance']}")
        print(f"质量分数: {sample['quality_score']}")
    
    print("\n" + "="*50)
    print("数据收集管道测试完成！")
    print("="*50)
    
    logger.info("测试完成，数据收集管道工作正常")

if __name__ == "__main__":
    main()