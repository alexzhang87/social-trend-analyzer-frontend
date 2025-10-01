#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查训练数据的真实性
"""
import json
import os
from pathlib import Path

def check_data_reality():
    """检查数据文件的真实性"""
    print("=== 数据真实性检查报告 ===\n")
    
    # 1. 检查large_social_dataset.json
    dataset_file = "large_social_dataset.json"
    if os.path.exists(dataset_file):
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        actual_count = len(data["data"])
        claimed_count = data["stats"]["total_posts"]
        file_size = os.path.getsize(dataset_file)
        
        print(f"📁 {dataset_file}:")
        print(f"   - 文件大小: {file_size:,} 字节 ({file_size/1024:.1f} KB)")
        print(f"   - 声称数据量: {claimed_count:,} 条")
        print(f"   - 实际数据量: {actual_count:,} 条")
        print(f"   - 数据真实性: {'❌ 虚假' if actual_count != claimed_count else '✅ 一致'}")
        print(f"   - 平均每条数据大小: {file_size/actual_count:.1f} 字节")
        print()
    else:
        print(f"❌ {dataset_file} 不存在")
    
    # 2. 检查训练配置文件
    config_files = [
        "training_config_template.json",
        "config/training_config_template.json",
        "models/enhanced_startup_consultant/training_info.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"📋 {config_file}:")
            if 'training_data_size' in config:
                print(f"   - 训练数据大小: {config['training_data_size']}")
            if 'epochs' in config:
                print(f"   - 训练轮数: {config['epochs']}")
            print()
    
    # 3. 检查数据目录
    data_dirs = ["data/training", "training_data"]
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            files = list(Path(data_dir).rglob("*"))
            print(f"📂 {data_dir}:")
            print(f"   - 文件数量: {len(files)}")
            for file in files[:5]:  # 只显示前5个文件
                if file.is_file():
                    size = file.stat().st_size
                    print(f"   - {file.name}: {size:,} 字节")
            if len(files) > 5:
                print(f"   - ... 还有 {len(files)-5} 个文件")
            print()
    
    # 4. 估算真实数据规模
    print("🔍 真实数据规模估算:")
    
    # 基于实际文件大小估算
    if os.path.exists(dataset_file):
        # 8.6KB 包含约100条数据
        # 要达到2200万条数据，需要约 1.9GB
        estimated_size_for_22m = (file_size / actual_count) * 22_000_000
        print(f"   - 要存储2200万条类似数据需要: {estimated_size_for_22m/1024/1024/1024:.1f} GB")
        print(f"   - 当前实际数据量级: {actual_count:,} 条 (约为声称的 {actual_count/22_000_000*100:.4f}%)")
    
    print("\n📊 结论:")
    print("   - 当前系统中的训练数据主要是模拟数据")
    print("   - 实际数据量远小于文档中声称的规模")
    print("   - 需要真实的大规模数据集成才能达到声称的训练效果")

if __name__ == "__main__":
    check_data_reality()