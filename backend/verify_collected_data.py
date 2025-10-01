#!/usr/bin/env python3
"""
🔍 数据收集验证脚本
查看和验证收集到的训练数据

使用方法:
python verify_collected_data.py
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def verify_collected_data():
    """验证收集到的数据"""
    db_path = Path("collected_data/collected_data.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在，请先运行数据收集脚本")
        return
    
    print("🔍 数据收集验证报告")
    print("=" * 60)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 总体统计
    cursor.execute('SELECT COUNT(*) FROM collected_data')
    total_count = cursor.fetchone()[0]
    print(f"📊 总记录数: {total_count:,}")
    
    # 2. 按来源统计
    cursor.execute('SELECT source, COUNT(*) FROM collected_data GROUP BY source ORDER BY COUNT(*) DESC')
    source_stats = cursor.fetchall()
    print(f"\n📈 数据源分布:")
    for source, count in source_stats:
        percentage = (count / total_count) * 100
        print(f"  - {source}: {count:,} 条 ({percentage:.1f}%)")
    
    # 3. 按类型统计
    cursor.execute('SELECT data_type, COUNT(*) FROM collected_data GROUP BY data_type ORDER BY COUNT(*) DESC')
    type_stats = cursor.fetchall()
    print(f"\n📋 数据类型分布:")
    for data_type, count in type_stats:
        percentage = (count / total_count) * 100
        print(f"  - {data_type}: {count:,} 条 ({percentage:.1f}%)")
    
    # 4. 质量分析
    cursor.execute('SELECT AVG(quality_score), MIN(quality_score), MAX(quality_score) FROM collected_data WHERE quality_score IS NOT NULL')
    quality_stats = cursor.fetchone()
    if quality_stats[0]:
        print(f"\n⭐ 质量分析:")
        print(f"  - 平均质量分数: {quality_stats[0]:.3f}")
        print(f"  - 最低质量分数: {quality_stats[1]:.3f}")
        print(f"  - 最高质量分数: {quality_stats[2]:.3f}")
    
    # 5. 时间分析
    cursor.execute('SELECT MIN(collected_at), MAX(collected_at) FROM collected_data')
    time_stats = cursor.fetchone()
    print(f"\n🕒 收集时间范围:")
    print(f"  - 最早: {time_stats[0]}")
    print(f"  - 最晚: {time_stats[1]}")
    
    # 6. 数据样本展示
    print(f"\n📝 数据样本 (每种类型显示1条):")
    print("-" * 60)
    
    for data_type, _ in type_stats[:5]:  # 显示前5种类型
        cursor.execute('''
            SELECT title, content, quality_score, source 
            FROM collected_data 
            WHERE data_type = ? 
            LIMIT 1
        ''', (data_type,))
        
        sample = cursor.fetchone()
        if sample:
            title, content, quality_score, source = sample
            print(f"\n🏷️  类型: {data_type} | 来源: {source} | 质量: {quality_score:.2f}")
            print(f"📌 标题: {title}")
            print(f"📄 内容: {content[:200]}{'...' if len(content) > 200 else ''}")
            print("-" * 40)
    
    # 7. 高质量数据统计
    cursor.execute('SELECT COUNT(*) FROM collected_data WHERE quality_score >= 0.8')
    high_quality_count = cursor.fetchone()[0]
    high_quality_percentage = (high_quality_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n🌟 高质量数据 (≥0.8分):")
    print(f"  - 数量: {high_quality_count:,} 条")
    print(f"  - 占比: {high_quality_percentage:.1f}%")
    
    # 8. 数据完整性检查
    cursor.execute('SELECT COUNT(*) FROM collected_data WHERE title IS NULL OR title = ""')
    missing_title = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM collected_data WHERE content IS NULL OR content = ""')
    missing_content = cursor.fetchone()[0]
    
    print(f"\n🔍 数据完整性:")
    print(f"  - 缺少标题: {missing_title} 条")
    print(f"  - 缺少内容: {missing_content} 条")
    print(f"  - 完整性: {((total_count - max(missing_title, missing_content)) / total_count * 100):.1f}%")
    
    # 9. 推荐的下一步操作
    print(f"\n💡 推荐操作:")
    if total_count < 1000:
        print("  ⚠️  数据量较少，建议:")
        print("     - 运行 python auto_data_collector.py --all 收集更多数据")
        print("     - 配置真实的API密钥获取真实数据")
    else:
        print("  ✅ 数据量充足，可以:")
        print("     - 开始数据预处理和清洗")
        print("     - 进行模型训练")
    
    if high_quality_percentage < 70:
        print("  ⚠️  高质量数据占比较低，建议:")
        print("     - 提高数据质量筛选标准")
        print("     - 优化数据收集策略")
    
    print(f"\n📁 数据文件位置:")
    print(f"  - 数据库: {db_path}")
    print(f"  - 大小: {db_path.stat().st_size / 1024:.1f} KB")
    
    conn.close()
    print("=" * 60)

def export_sample_data():
    """导出样本数据用于检查"""
    db_path = Path("collected_data/collected_data.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 导出每种类型的前10条数据
    cursor.execute('SELECT DISTINCT data_type FROM collected_data')
    data_types = [row[0] for row in cursor.fetchall()]
    
    sample_data = {}
    
    for data_type in data_types:
        cursor.execute('''
            SELECT id, source, data_type, title, content, quality_score, collected_at
            FROM collected_data 
            WHERE data_type = ? 
            ORDER BY quality_score DESC 
            LIMIT 10
        ''', (data_type,))
        
        rows = cursor.fetchall()
        sample_data[data_type] = []
        
        for row in rows:
            sample_data[data_type].append({
                'id': row[0],
                'source': row[1],
                'data_type': row[2],
                'title': row[3],
                'content': row[4][:500] + '...' if len(row[4]) > 500 else row[4],  # 限制长度
                'quality_score': row[5],
                'collected_at': row[6]
            })
    
    # 保存样本数据
    sample_file = Path("collected_data/sample_data.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"📄 样本数据已导出到: {sample_file}")
    print(f"📊 包含 {len(data_types)} 种数据类型的样本")
    
    conn.close()

def main():
    print("🚀 IdeaEden 数据验证工具")
    print("选择操作:")
    print("1. 验证收集的数据")
    print("2. 导出样本数据")
    print("3. 全部执行")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == '1':
        verify_collected_data()
    elif choice == '2':
        export_sample_data()
    elif choice == '3':
        verify_collected_data()
        print("\n" + "="*60)
        export_sample_data()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()