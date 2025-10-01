#!/usr/bin/env python3
"""
AI专家顾问模型性能分析脚本
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_report():
    """加载最新的测试报告"""
    report_files = list(Path(".").glob("inference_test_report_*.json"))
    if not report_files:
        raise FileNotFoundError("找不到推理测试报告文件")
    
    latest_report = sorted(report_files)[-1]
    logger.info(f"加载测试报告: {latest_report}")
    
    with open(latest_report, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_model_performance(report):
    """分析模型性能"""
    print("="*80)
    print("AI专家顾问模型性能分析报告")
    print("="*80)
    
    # 基本信息
    print(f"模型文件: {report['model_file']}")
    print(f"测试时间: {report['test_time']}")
    print(f"测试用例数量: {report['test_cases']}")
    print()
    
    # 整体性能指标
    print("整体性能指标:")
    print(f"  平均置信度: {report['average_confidence']:.3f}")
    print(f"  平均质量评分: {report['average_quality']:.3f}")
    print()
    
    # 专家类型分布
    print("专家类型分布:")
    total_predictions = sum(report['expert_distribution'].values())
    for expert, count in report['expert_distribution'].items():
        percentage = (count / total_predictions) * 100
        print(f"  {expert}: {count} 次 ({percentage:.1f}%)")
    print()
    
    # 详细分析
    results = report['detailed_results']
    
    # 置信度分析
    confidences = [r['confidence'] for r in results]
    quality_scores = [r['quality_score'] for r in results]
    
    print("置信度统计:")
    print(f"  最高置信度: {max(confidences):.3f}")
    print(f"  最低置信度: {min(confidences):.3f}")
    print(f"  置信度标准差: {np.std(confidences):.3f}")
    print()
    
    print("质量评分统计:")
    print(f"  最高质量评分: {max(quality_scores):.3f}")
    print(f"  最低质量评分: {min(quality_scores):.3f}")
    print(f"  质量评分标准差: {np.std(quality_scores):.3f}")
    print()
    
    # 分析每个专家类型的概率分布
    expert_probs = {}
    for result in results:
        for expert, prob in result['all_probabilities'].items():
            if expert not in expert_probs:
                expert_probs[expert] = []
            expert_probs[expert].append(prob)
    
    print("各专家类型平均概率:")
    for expert, probs in expert_probs.items():
        avg_prob = np.mean(probs)
        std_prob = np.std(probs)
        print(f"  {expert}: {avg_prob:.3f} ± {std_prob:.3f}")
    print()
    
    return {
        'confidences': confidences,
        'quality_scores': quality_scores,
        'expert_probs': expert_probs,
        'results': results
    }

def create_visualizations(analysis_data, report):
    """创建可视化图表"""
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('AI专家顾问模型性能分析', fontsize=16, fontweight='bold')
    
    # 1. 置信度分布
    axes[0, 0].hist(analysis_data['confidences'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('置信度分布')
    axes[0, 0].set_xlabel('置信度')
    axes[0, 0].set_ylabel('频次')
    axes[0, 0].axvline(np.mean(analysis_data['confidences']), color='red', linestyle='--', 
                       label=f'平均值: {np.mean(analysis_data["confidences"]):.3f}')
    axes[0, 0].legend()
    
    # 2. 质量评分分布
    axes[0, 1].hist(analysis_data['quality_scores'], bins=10, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 1].set_title('质量评分分布')
    axes[0, 1].set_xlabel('质量评分')
    axes[0, 1].set_ylabel('频次')
    axes[0, 1].axvline(np.mean(analysis_data['quality_scores']), color='red', linestyle='--',
                       label=f'平均值: {np.mean(analysis_data["quality_scores"]):.3f}')
    axes[0, 1].legend()
    
    # 3. 专家类型分布
    expert_dist = report['expert_distribution']
    axes[1, 0].pie(expert_dist.values(), labels=expert_dist.keys(), autopct='%1.1f%%', startangle=90)
    axes[1, 0].set_title('专家类型预测分布')
    
    # 4. 各专家类型平均概率
    expert_names = list(analysis_data['expert_probs'].keys())
    avg_probs = [np.mean(analysis_data['expert_probs'][expert]) for expert in expert_names]
    
    bars = axes[1, 1].bar(expert_names, avg_probs, color='coral', alpha=0.7)
    axes[1, 1].set_title('各专家类型平均概率')
    axes[1, 1].set_xlabel('专家类型')
    axes[1, 1].set_ylabel('平均概率')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # 添加数值标签
    for bar, prob in zip(bars, avg_probs):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{prob:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # 保存图表
    chart_file = f"performance_analysis_{int(report['test_time'].replace('-', '').replace(':', '').replace(' ', '_'))}.png"
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    logger.info(f"性能分析图表已保存到: {chart_file}")
    
    plt.show()
    
    return chart_file

def generate_recommendations(analysis_data, report):
    """生成改进建议"""
    print("="*80)
    print("模型改进建议")
    print("="*80)
    
    avg_confidence = report['average_confidence']
    avg_quality = report['average_quality']
    
    recommendations = []
    
    # 置信度分析
    if avg_confidence < 0.7:
        recommendations.append("🔸 置信度偏低，建议增加训练数据或调整模型架构")
    elif avg_confidence > 0.9:
        recommendations.append("⚠️ 置信度过高，可能存在过拟合，建议检查训练数据质量")
    else:
        recommendations.append("✅ 置信度在合理范围内")
    
    # 质量评分分析
    if avg_quality < 0.7:
        recommendations.append("🔸 质量评分偏低，建议改进训练数据标注质量")
    elif avg_quality > 0.9:
        recommendations.append("⚠️ 质量评分过高，可能存在标注偏差")
    else:
        recommendations.append("✅ 质量评分在合理范围内")
    
    # 专家类型分布分析
    expert_dist = report['expert_distribution']
    if len(expert_dist) == 1:
        recommendations.append("🔸 模型只预测一种专家类型，建议检查训练数据平衡性")
    elif max(expert_dist.values()) / sum(expert_dist.values()) > 0.8:
        recommendations.append("🔸 专家类型分布不均衡，建议平衡各类型的训练数据")
    else:
        recommendations.append("✅ 专家类型分布相对均衡")
    
    # 置信度变异性分析
    confidence_std = np.std(analysis_data['confidences'])
    if confidence_std > 0.2:
        recommendations.append("🔸 置信度变异性较大，建议检查输入数据的一致性")
    else:
        recommendations.append("✅ 置信度变异性在合理范围内")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print()
    
    return recommendations

def main():
    """主函数"""
    try:
        # 加载测试报告
        report = load_test_report()
        
        # 分析性能
        analysis_data = analyze_model_performance(report)
        
        # 创建可视化图表
        chart_file = create_visualizations(analysis_data, report)
        
        # 生成改进建议
        recommendations = generate_recommendations(analysis_data, report)
        
        # 生成综合报告
        comprehensive_report = {
            'original_report': report,
            'analysis': {
                'confidence_stats': {
                    'mean': np.mean(analysis_data['confidences']),
                    'std': np.std(analysis_data['confidences']),
                    'min': min(analysis_data['confidences']),
                    'max': max(analysis_data['confidences'])
                },
                'quality_stats': {
                    'mean': np.mean(analysis_data['quality_scores']),
                    'std': np.std(analysis_data['quality_scores']),
                    'min': min(analysis_data['quality_scores']),
                    'max': max(analysis_data['quality_scores'])
                },
                'expert_avg_probs': {
                    expert: np.mean(probs) 
                    for expert, probs in analysis_data['expert_probs'].items()
                }
            },
            'recommendations': recommendations,
            'chart_file': chart_file
        }
        
        # 保存综合报告
        comprehensive_file = f"comprehensive_analysis_{int(report['test_time'].replace('-', '').replace(':', '').replace(' ', '_'))}.json"
        with open(comprehensive_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"综合分析报告已保存到: {comprehensive_file}")
        
        print("="*80)
        print("🎉 性能分析完成!")
        print(f"📊 综合报告: {comprehensive_file}")
        print(f"📈 可视化图表: {chart_file}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"性能分析失败: {e}")
        raise

if __name__ == "__main__":
    main()