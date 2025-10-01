#!/usr/bin/env python3
"""
大规模模拟数据生成器
生成1000条高质量模拟数据用于测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_mock_service import EnhancedMockService
from app.utils.logger import logger

def main():
    """生成大规模模拟数据集"""
    print("🚀 开始生成大规模模拟数据集...")
    
    # 初始化服务
    mock_service = EnhancedMockService()
    
    # 测试关键词
    test_keywords = ["AI", "机器学习", "cryptocurrency"]
    
    # 生成数据集
    dataset = mock_service.generate_large_dataset(test_keywords)
    
    # 保存到文件
    filepath = mock_service.save_dataset_to_file(dataset, "large_mock_dataset.json")
    
    if filepath:
        print(f"✅ 成功生成并保存数据集到: {filepath}")
        print(f"📊 数据统计:")
        print(f"   - 总数据量: {dataset['stats']['total_posts']} 条")
        print(f"   - Twitter: {dataset['stats']['twitter_posts']} 条")
        print(f"   - Reddit: {dataset['stats']['reddit_posts']} 条")
        print(f"   - 情感分布: {dataset['stats']['sentiment_distribution']}")
        
        # 显示样本数据
        print(f"\n📝 样本数据预览:")
        for i, sample in enumerate(dataset['data'][:3]):
            print(f"   {i+1}. [{sample['platform']}] {sample['text'][:100]}...")
            print(f"      情感: {sample['sentiment']}, 互动: {sample.get('likes', sample.get('upvotes', 0))}")
    else:
        print("❌ 数据集生成失败")

if __name__ == "__main__":
    main()