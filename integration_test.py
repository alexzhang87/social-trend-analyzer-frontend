#!/usr/bin/env python3
"""
集成测试脚本 - 验证数据收集和AI专家增强系统
"""

import asyncio
import os
import sqlite3
from loguru import logger
from test_data_collection import main as test_data_collection
from ai_expert_enhancer import AIExpertEnhancer

async def run_integration_test():
    """运行完整的集成测试"""
    logger.info("开始集成测试...")
    
    # 1. 清理旧数据
    db_path = "training_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("清理旧数据库")
    
    # 2. 运行数据收集测试
    logger.info("步骤 1: 运行数据收集测试")
    await test_data_collection()
    
    # 3. 验证数据库内容
    logger.info("步骤 2: 验证数据库内容")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM training_data")
    total_records = cursor.fetchone()[0]
    logger.info(f"数据库中总记录数: {total_records}")
    
    cursor.execute("SELECT category, COUNT(*) FROM training_data GROUP BY category")
    categories = cursor.fetchall()
    logger.info("按类别统计:")
    for category, count in categories:
        logger.info(f"  {category}: {count} 条")
    
    conn.close()
    
    # 4. 测试AI专家增强功能
    logger.info("步骤 3: 测试AI专家增强功能")
    enhancer = AIExpertEnhancer(db_path)
    
    # 测试查询
    test_queries = [
        ("进入新市场策略", "business_strategy"),
        ("处理产品bug", "technical_support"),
        ("提升用户体验", "product_consultation"),
        ("客户投诉处理", "customer_support"),
        ("产品功能规划", "product_strategy")
    ]
    
    for query, expert_type in test_queries:
        logger.info(f"\n测试查询: '{query}' (专家类型: {expert_type})")
        
        # 查找相关示例
        examples = enhancer.find_relevant_examples(query, expert_type, limit=3)
        if examples:
            logger.info(f"找到 {len(examples)} 个相关示例:")
            for i, example in enumerate(examples, 1):
                logger.info(f"  示例 {i}: {example['category']} (相关性: {example['relevance']:.3f}, 质量: {example['quality_score']:.3f})")
        else:
            logger.warning("未找到相关示例")
        
        # 生成增强提示词
        enhanced_prompt = enhancer.enhance_expert_prompt(query, expert_type)
        logger.info(f"增强提示词长度: {len(enhanced_prompt)} 字符")
    
    # 5. 生成统计报告
    logger.info("\n步骤 4: 生成统计报告")
    stats = enhancer.get_enhancement_stats()
    logger.info("AI专家增强统计:")
    logger.info(f"  总训练数据: {stats['total_training_data']}")
    logger.info(f"  知识库类别: {len(stats['knowledge_categories'])}")
    logger.info(f"  支持的专家类型: {len(stats['supported_expert_types'])}")
    
    # 6. 验证配置文件
    config_file = "ai_expert_enhancement_config.json"
    if os.path.exists(config_file):
        logger.info(f"AI专家增强配置文件已生成: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            import json
            config = json.load(f)
            logger.info(f"配置文件包含 {len(config['expert_types'])} 种专家类型")
    else:
        logger.warning("AI专家增强配置文件未生成")
    
    logger.info("\n============================================================")
    logger.info("集成测试完成！")
    logger.info("============================================================")
    
    return {
        "total_records": total_records,
        "categories": dict(categories),
        "enhancement_stats": stats,
        "config_generated": os.path.exists(config_file)
    }

def main():
    """主函数"""
    return asyncio.run(run_integration_test())

if __name__ == "__main__":
    result = main()
    print(f"\n集成测试结果: {result}")