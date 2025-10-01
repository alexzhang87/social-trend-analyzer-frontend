#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stack Overflow 数据获取和处理集成脚本

功能：
1. 通过 API 获取 Stack Overflow 数据
2. 数据清理和质量评估
3. 生成训练数据集
4. 生成详细报告

使用方法：
python run_stackoverflow_collection.py --tags python,javascript --max-questions 1000

作者：AI Assistant
创建时间：2024年
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# 导入自定义模块
from stackoverflow_data_collector import StackOverflowDataCollector
from stackoverflow_data_processor import StackOverflowDataProcessor

def setup_logging(output_dir: Path):
    """设置日志配置"""
    log_file = output_dir / f"stackoverflow_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Stack Overflow 数据获取和处理工具')
    
    # 数据获取参数
    parser.add_argument('--tags', type=str, default='python,javascript,java,c++,react',
                       help='要获取的标签，用逗号分隔 (默认: python,javascript,java,c++,react)')
    parser.add_argument('--max-questions', type=int, default=1000,
                       help='每个标签最大获取问题数 (默认: 1000)')
    parser.add_argument('--min-score', type=int, default=1,
                       help='最小问题分数 (默认: 1)')
    parser.add_argument('--include-answers', action='store_true', default=True,
                       help='是否包含答案 (默认: True)')
    
    # 输出参数
    parser.add_argument('--output-dir', type=str, default='stackoverflow_data',
                       help='输出目录 (默认: stackoverflow_data)')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='both',
                       help='输出格式 (默认: both)')
    
    # 处理参数
    parser.add_argument('--skip-collection', action='store_true',
                       help='跳过数据收集，只处理现有数据')
    parser.add_argument('--skip-processing', action='store_true',
                       help='跳过数据处理，只收集原始数据')
    
    # 质量控制参数
    parser.add_argument('--min-quality-score', type=float, default=60.0,
                       help='最小质量分数 (默认: 60.0)')
    parser.add_argument('--quality-levels', type=str, default='high,medium',
                       help='包含的质量等级，用逗号分隔 (默认: high,medium)')
    
    return parser.parse_args()

def collect_stackoverflow_data(args, logger):
    """收集 Stack Overflow 数据"""
    logger.info("开始收集 Stack Overflow 数据...")
    
    # 创建数据收集器
    collector = StackOverflowDataCollector(output_dir=args.output_dir)
    
    # 解析标签
    tags = [tag.strip() for tag in args.tags.split(',')]
    
    collected_files = []
    
    try:
        all_collected_data = []  # 保存所有收集的数据用于生成报告
        
        for tag in tags:
            logger.info(f"收集标签 '{tag}' 的数据...")
            
            # 收集问题数据 (将 max_questions 转换为 max_pages，每页100个问题)
            max_pages = max(1, (args.max_questions + 99) // 100)  # 向上取整
            questions = collector.collect_questions_by_tag(
                tag=tag,
                max_pages=max_pages
            )
            
            # 如果获取的问题数超过限制，截取前 max_questions 个
            if len(questions) > args.max_questions:
                questions = questions[:args.max_questions]
            
            # 如果需要包含答案，获取每个问题的答案
            formatted_data = []
            if questions:
                for question in questions:
                    answers = []
                    if args.include_answers:
                        try:
                            question_id = question.get('question_id')
                            if question_id:
                                answers = collector.get_question_answers(question_id)
                        except Exception as e:
                            logger.warning(f"获取问题 {question_id} 的答案失败: {e}")
                    
                    # 格式化数据
                    formatted_item = collector.format_question_data(question, answers)
                    formatted_data.append(formatted_item)
                
                logger.info(f"标签 '{tag}' 格式化完成，共 {len(formatted_data)} 条数据")
            
            if formatted_data:
                 # 添加到总数据中
                 all_collected_data.extend(formatted_data)
                 
                 # 保存数据
                 if args.format in ['json', 'both']:
                     json_file = collector.save_data(formatted_data, f"stackoverflow_{tag}_questions.json")
                     collected_files.append(json_file)
                     logger.info(f"保存 JSON 文件: {json_file}")
                 
                 if args.format in ['csv', 'both']:
                     csv_file = collector.save_as_csv(formatted_data, f"stackoverflow_{tag}_questions.csv")
                     collected_files.append(csv_file)
                     logger.info(f"保存 CSV 文件: {csv_file}")
                 
                 logger.info(f"标签 '{tag}' 收集完成，获得 {len(formatted_data)} 个问题")
            else:
                logger.warning(f"标签 '{tag}' 没有收集到数据")
        
        # 生成收集报告
        if all_collected_data:
            report = collector.generate_report(all_collected_data)
            report_file = collector.save_report(report)
            logger.info(f"收集报告保存到: {report_file}")
        else:
            report = {'summary': '未收集到任何数据'}
            report_file = None
        
        return collected_files, report, all_collected_data
        
    except Exception as e:
        logger.error(f"数据收集过程中出错: {e}")
        raise

def process_stackoverflow_data(collected_files, all_collected_data, args, logger):
    """处理 Stack Overflow 数据"""
    logger.info("开始处理 Stack Overflow 数据...")
    
    # 创建数据处理器
    processor = StackOverflowDataProcessor(output_dir=args.output_dir)
    
    processed_files = []
    
    try:
        # 由于数据已经在收集阶段被格式化，我们直接使用收集到的数据
        # 进行质量评估和统计分析
        if all_collected_data:
            logger.info(f"分析已收集的 {len(all_collected_data)} 条数据...")
            
            # 直接使用收集到的数据进行质量分析
            processed_items = []
            for item in all_collected_data:
                # 转换为处理器期望的格式
                raw_item = {
                    'question_id': item.get('question_id', ''),
                    'title': item.get('input', ''),
                    'body': item.get('output', ''),
                    'score': item.get('score', 0),
                    'view_count': item.get('view_count', 0),
                    'answer_count': item.get('answer_count', 0),
                    'tags': item.get('tags', []),
                    'creation_date': item.get('creation_date', ''),
                    'link': item.get('link', ''),
                    'quality_score': item.get('quality_score', 0.0)
                }
                
                processed_items.append(raw_item)
                
                # 更新处理器统计
                processor.stats['total_processed'] += 1
                quality_score = item.get('quality_score', 0.0)
                if quality_score >= 0.8:
                    processor.stats['high_quality'] += 1
                elif quality_score >= 0.6:
                    processor.stats['medium_quality'] += 1
                else:
                    processor.stats['low_quality'] += 1
            
            # 创建合并的训练数据集
            training_dataset_file = processor.output_dir / "stackoverflow_training_dataset.json"
            with open(training_dataset_file, 'w', encoding='utf-8') as f:
                json.dump(all_collected_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"训练数据集创建完成: {training_dataset_file}")
            processed_files.append(str(training_dataset_file))
            
            # 应用质量过滤
            filtered_dataset = filter_by_quality(
                str(training_dataset_file), 
                args.min_quality_score,
                args.quality_levels.split(','),
                logger
            )
            
            processed_files.append(filtered_dataset)
        
        # 生成质量报告
        quality_report = processor.generate_quality_report()
        report_file = processor.save_quality_report(quality_report)
        logger.info(f"质量报告保存到: {report_file}")
        
        return processed_files, quality_report
        
    except Exception as e:
        logger.error(f"数据处理过程中出错: {e}")
        raise

def filter_by_quality(dataset_file, min_score, quality_levels, logger):
    """根据质量标准过滤数据集"""
    logger.info(f"应用质量过滤: 最小分数={min_score}, 质量等级={quality_levels}")
    
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 过滤数据
        filtered_data = []
        for item in data:
            if (item['quality_score'] >= min_score and 
                item.get('metadata', {}).get('quality_level') in quality_levels):
                filtered_data.append(item)
        
        # 保存过滤后的数据
        filtered_file = Path(dataset_file).parent / "stackoverflow_filtered_training_dataset.json"
        with open(filtered_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"质量过滤完成: {len(data)} -> {len(filtered_data)} 条数据")
        logger.info(f"过滤后数据集保存到: {filtered_file}")
        
        return str(filtered_file)
        
    except Exception as e:
        logger.error(f"质量过滤过程中出错: {e}")
        raise

def generate_final_report(collection_report, quality_report, processed_files, args, logger):
    """生成最终报告"""
    logger.info("生成最终报告...")
    
    final_report = {
        'collection_summary': collection_report,
        'quality_summary': quality_report,
        'processing_info': {
            'processed_files': processed_files,
            'parameters': {
                'tags': args.tags,
                'max_questions_per_tag': args.max_questions,
                'min_score': args.min_score,
                'min_quality_score': args.min_quality_score,
                'quality_levels': args.quality_levels,
                'output_format': args.format
            }
        },
        'recommendations': [],
        'next_steps': [],
        'timestamp': datetime.now().isoformat()
    }
    
    # 添加建议
    total_questions = collection_report.get('total_questions_collected', 0)
    high_quality_count = quality_report.get('processing_summary', {}).get('high_quality', 0)
    
    if total_questions > 0:
        quality_ratio = high_quality_count / total_questions
        if quality_ratio > 0.7:
            final_report['recommendations'].append("数据质量很好，可以直接用于模型训练")
        elif quality_ratio > 0.4:
            final_report['recommendations'].append("数据质量中等，建议进一步筛选或增加数据源")
        else:
            final_report['recommendations'].append("数据质量较低，建议调整收集策略或寻找更好的数据源")
    
    # 添加后续步骤
    final_report['next_steps'].extend([
        "检查生成的训练数据集格式是否符合模型要求",
        "考虑与其他数据源合并以增加数据多样性",
        "根据具体任务需求调整数据预处理流程",
        "设置数据验证和测试集"
    ])
    
    # 保存最终报告
    output_dir = Path(args.output_dir)
    report_file = output_dir / f"stackoverflow_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"最终报告保存到: {report_file}")
    
    # 打印摘要
    print("\n" + "="*60)
    print("Stack Overflow 数据获取和处理完成")
    print("="*60)
    print(f"总获取问题数: {total_questions}")
    print(f"高质量数据数: {high_quality_count}")
    print(f"处理后文件数: {len(processed_files)}")
    print(f"输出目录: {args.output_dir}")
    print(f"最终报告: {report_file}")
    print("="*60)
    
    return str(report_file)

def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 设置日志
    logger = setup_logging(output_dir)
    
    logger.info("开始 Stack Overflow 数据获取和处理流程")
    logger.info(f"参数: {vars(args)}")
    
    try:
        collected_files = []
        collection_report = {}
        all_collected_data = []
        
        # 步骤1: 数据收集
        if not args.skip_collection:
            collected_files, collection_report, all_collected_data = collect_stackoverflow_data(args, logger)
        else:
            logger.info("跳过数据收集步骤")
            # 查找现有文件
            for file_path in output_dir.glob("stackoverflow_*.json"):
                collected_files.append(str(file_path))
            for file_path in output_dir.glob("stackoverflow_*.csv"):
                collected_files.append(str(file_path))
            
            # 尝试从现有文件加载数据
            for file_path in output_dir.glob("stackoverflow_*_questions.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_collected_data.extend(data)
                except Exception as e:
                    logger.warning(f"无法加载文件 {file_path}: {e}")
        
        processed_files = []
        quality_report = {}
        
        # 步骤2: 数据处理
        if not args.skip_processing and (collected_files or all_collected_data):
            processed_files, quality_report = process_stackoverflow_data(collected_files, all_collected_data, args, logger)
        else:
            if args.skip_processing:
                logger.info("跳过数据处理步骤")
            else:
                logger.warning("没有找到需要处理的文件或数据")
        
        # 步骤3: 生成最终报告
        final_report = generate_final_report(collection_report, quality_report, processed_files, args, logger)
        
        logger.info("Stack Overflow 数据获取和处理流程完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"流程执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()