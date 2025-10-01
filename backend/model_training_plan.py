#!/usr/bin/env python3
"""
模型训练计划和监控系统
用于大规模数据训练和模型性能评估
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import Dataset
import wandb
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelTrainingPipeline:
    """模型训练管道"""
    
    def __init__(self, data_dir="collected_data", output_dir="model_outputs"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 数据统计
        self.data_stats = {
            "total_samples": 0,
            "train_samples": 0,
            "val_samples": 0,
            "test_samples": 0,
            "data_sources": {},
            "quality_distribution": {}
        }
        
        # 训练配置
        self.training_config = {
            "model_name": "microsoft/DialoGPT-medium",
            "max_length": 512,
            "batch_size": 8,
            "learning_rate": 5e-5,
            "num_epochs": 3,
            "warmup_steps": 500,
            "logging_steps": 100,
            "save_steps": 1000,
            "eval_steps": 500
        }
        
        # 评估指标
        self.evaluation_metrics = {
            "before_training": {},
            "after_training": {},
            "improvement": {}
        }
    
    def load_and_prepare_data(self):
        """加载和准备训练数据"""
        logger.info("开始加载和准备训练数据...")
        
        all_data = []
        
        # 1. 加载Hugging Face数据集
        hf_datasets = [
            "bitext_Bitext_retail_banking_llm_chatbot_training_dataset_retail_banking.csv",
            "bitext_Bitext_telco_llm_chatbot_training_dataset_telco.csv", 
            "bitext_Bitext_customer_support_llm_chatbot_training_dataset_customer_support.csv",
            "lmsys_chatbot_arena_conversations_chatbot_arena.csv",
            "banking77_banking77.csv"
        ]
        
        for dataset_file in hf_datasets:
            file_path = self.data_dir / dataset_file
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    logger.info(f"加载 {dataset_file}: {len(df)} 条数据")
                    
                    # 根据不同数据集格式处理
                    if "bitext" in dataset_file:
                        # Bitext格式: instruction -> response
                        for _, row in df.iterrows():
                            all_data.append({
                                "input": row.get("instruction", ""),
                                "output": row.get("response", ""),
                                "source": "bitext",
                                "category": row.get("category", "general"),
                                "quality": "high"
                            })
                    elif "lmsys" in dataset_file:
                        # LMSYS格式: conversation data
                        for _, row in df.iterrows():
                            try:
                                conversation = eval(row.get("conversation", "[]"))
                                if len(conversation) >= 2:
                                    all_data.append({
                                        "input": conversation[0].get("content", ""),
                                        "output": conversation[1].get("content", ""),
                                        "source": "lmsys",
                                        "category": "conversation",
                                        "quality": "high"
                                    })
                            except:
                                continue
                    elif "banking77" in dataset_file:
                        # Banking77格式: text classification
                        for _, row in df.iterrows():
                            all_data.append({
                                "input": row.get("text", ""),
                                "output": f"这是关于{row.get('label', '银行业务')}的询问。",
                                "source": "banking77",
                                "category": "classification",
                                "quality": "high"
                            })
                            
                    self.data_stats["data_sources"][dataset_file] = len(df)
                    
                except Exception as e:
                    logger.error(f"加载 {dataset_file} 失败: {e}")
        
        # 2. 加载处理后的JSON数据
        json_files = [
            "multi_source_training_20250930_134601.json",
            "academic_reports_training_20250930_134542.json"
        ]
        
        for json_file in json_files:
            file_path = self.data_dir / json_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    logger.info(f"加载 {json_file}: {len(data)} 条数据")
                    
                    for item in data:
                        all_data.append({
                            "input": item.get("text", "")[:200],  # 取前200字符作为输入
                            "output": item.get("text", "")[200:],  # 剩余作为输出
                            "source": item.get("type", "unknown"),
                            "category": item.get("category", "general"),
                            "quality": item.get("quality", "medium")
                        })
                    
                    self.data_stats["data_sources"][json_file] = len(data)
                    
                except Exception as e:
                    logger.error(f"加载 {json_file} 失败: {e}")
        
        # 3. 数据清洗和过滤
        logger.info("开始数据清洗和过滤...")
        cleaned_data = []
        
        for item in all_data:
            # 过滤空数据
            if not item["input"].strip() or not item["output"].strip():
                continue
            
            # 长度过滤
            if len(item["input"]) < 10 or len(item["output"]) < 10:
                continue
            
            # 长度截断
            item["input"] = item["input"][:400]
            item["output"] = item["output"][:400]
            
            cleaned_data.append(item)
        
        logger.info(f"数据清洗完成，保留 {len(cleaned_data)} 条有效数据")
        
        # 4. 数据分割
        train_data, temp_data = train_test_split(cleaned_data, test_size=0.2, random_state=42)
        val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
        
        self.data_stats.update({
            "total_samples": len(cleaned_data),
            "train_samples": len(train_data),
            "val_samples": len(val_data),
            "test_samples": len(test_data)
        })
        
        # 质量分布统计
        quality_counts = {}
        for item in cleaned_data:
            quality = item["quality"]
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        self.data_stats["quality_distribution"] = quality_counts
        
        logger.info(f"数据分割完成 - 训练集: {len(train_data)}, 验证集: {len(val_data)}, 测试集: {len(test_data)}")
        
        return train_data, val_data, test_data
    
    def prepare_datasets(self, train_data, val_data, test_data):
        """准备Hugging Face数据集格式"""
        logger.info("准备数据集格式...")
        
        def format_data(data):
            formatted = []
            for item in data:
                text = f"用户: {item['input']}\n助手: {item['output']}"
                formatted.append({"text": text})
            return formatted
        
        train_dataset = Dataset.from_list(format_data(train_data))
        val_dataset = Dataset.from_list(format_data(val_data))
        test_dataset = Dataset.from_list(format_data(test_data))
        
        return train_dataset, val_dataset, test_dataset
    
    def evaluate_baseline(self, test_data):
        """评估基线模型性能"""
        logger.info("评估基线模型性能...")
        
        try:
            # 加载预训练模型
            tokenizer = AutoTokenizer.from_pretrained(self.training_config["model_name"])
            model = AutoModelForCausalLM.from_pretrained(self.training_config["model_name"])
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # 评估样本
            sample_inputs = [item["input"] for item in test_data[:100]]  # 取100个样本
            sample_outputs = [item["output"] for item in test_data[:100]]
            
            generated_outputs = []
            
            for input_text in sample_inputs:
                try:
                    inputs = tokenizer.encode(f"用户: {input_text}\n助手:", return_tensors="pt")
                    
                    with torch.no_grad():
                        outputs = model.generate(
                            inputs,
                            max_length=inputs.shape[1] + 100,
                            num_return_sequences=1,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id
                        )
                    
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    generated_text = generated_text.split("助手:")[-1].strip()
                    generated_outputs.append(generated_text)
                    
                except Exception as e:
                    logger.warning(f"生成失败: {e}")
                    generated_outputs.append("")
            
            # 计算基线指标
            baseline_metrics = self.calculate_metrics(sample_outputs, generated_outputs)
            self.evaluation_metrics["before_training"] = baseline_metrics
            
            logger.info(f"基线模型评估完成: {baseline_metrics}")
            
        except Exception as e:
            logger.error(f"基线评估失败: {e}")
            self.evaluation_metrics["before_training"] = {"error": str(e)}
    
    def calculate_metrics(self, true_outputs, generated_outputs):
        """计算评估指标"""
        from rouge_score import rouge_scorer
        from nltk.translate.bleu_score import sentence_bleu
        
        metrics = {
            "avg_length": np.mean([len(text) for text in generated_outputs]),
            "non_empty_ratio": sum(1 for text in generated_outputs if text.strip()) / len(generated_outputs),
            "rouge_scores": {},
            "bleu_scores": []
        }
        
        try:
            # ROUGE分数
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
            
            for true_text, gen_text in zip(true_outputs, generated_outputs):
                if gen_text.strip():
                    scores = scorer.score(true_text, gen_text)
                    for key in rouge_scores:
                        rouge_scores[key].append(scores[key].fmeasure)
            
            for key in rouge_scores:
                if rouge_scores[key]:
                    metrics["rouge_scores"][key] = np.mean(rouge_scores[key])
            
            # BLEU分数
            for true_text, gen_text in zip(true_outputs, generated_outputs):
                if gen_text.strip():
                    bleu = sentence_bleu([true_text.split()], gen_text.split())
                    metrics["bleu_scores"].append(bleu)
            
            if metrics["bleu_scores"]:
                metrics["avg_bleu"] = np.mean(metrics["bleu_scores"])
            
        except Exception as e:
            logger.warning(f"指标计算部分失败: {e}")
        
        return metrics
    
    def train_model(self, train_dataset, val_dataset):
        """训练模型"""
        logger.info("开始模型训练...")
        
        try:
            # 初始化wandb（如果可用）
            try:
                wandb.init(project="model-training", config=self.training_config)
            except:
                logger.warning("Wandb初始化失败，跳过在线监控")
            
            # 加载模型和分词器
            tokenizer = AutoTokenizer.from_pretrained(self.training_config["model_name"])
            model = AutoModelForCausalLM.from_pretrained(self.training_config["model_name"])
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # 数据预处理
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    truncation=True,
                    padding=True,
                    max_length=self.training_config["max_length"]
                )
            
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # 训练参数
            training_args = TrainingArguments(
                output_dir=str(self.output_dir / "checkpoints"),
                num_train_epochs=self.training_config["num_epochs"],
                per_device_train_batch_size=self.training_config["batch_size"],
                per_device_eval_batch_size=self.training_config["batch_size"],
                learning_rate=self.training_config["learning_rate"],
                warmup_steps=self.training_config["warmup_steps"],
                logging_steps=self.training_config["logging_steps"],
                save_steps=self.training_config["save_steps"],
                eval_steps=self.training_config["eval_steps"],
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                report_to="wandb" if "wandb" in globals() else None,
                logging_dir=str(self.output_dir / "logs"),
                save_total_limit=3,
                dataloader_num_workers=0,  # Windows兼容性
            )
            
            # 训练器
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
            )
            
            # 开始训练
            logger.info("开始训练...")
            trainer.train()
            
            # 保存模型
            model_save_path = self.output_dir / "final_model"
            trainer.save_model(str(model_save_path))
            tokenizer.save_pretrained(str(model_save_path))
            
            logger.info(f"模型训练完成，保存至: {model_save_path}")
            
            return str(model_save_path)
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            return None
    
    def evaluate_trained_model(self, model_path, test_data):
        """评估训练后的模型"""
        logger.info("评估训练后的模型...")
        
        try:
            # 加载训练后的模型
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # 评估样本
            sample_inputs = [item["input"] for item in test_data[:100]]
            sample_outputs = [item["output"] for item in test_data[:100]]
            
            generated_outputs = []
            
            for input_text in sample_inputs:
                try:
                    inputs = tokenizer.encode(f"用户: {input_text}\n助手:", return_tensors="pt")
                    
                    with torch.no_grad():
                        outputs = model.generate(
                            inputs,
                            max_length=inputs.shape[1] + 100,
                            num_return_sequences=1,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id
                        )
                    
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    generated_text = generated_text.split("助手:")[-1].strip()
                    generated_outputs.append(generated_text)
                    
                except Exception as e:
                    logger.warning(f"生成失败: {e}")
                    generated_outputs.append("")
            
            # 计算训练后指标
            trained_metrics = self.calculate_metrics(sample_outputs, generated_outputs)
            self.evaluation_metrics["after_training"] = trained_metrics
            
            # 计算改进
            if "before_training" in self.evaluation_metrics:
                improvement = {}
                before = self.evaluation_metrics["before_training"]
                after = self.evaluation_metrics["after_training"]
                
                for key in ["avg_length", "non_empty_ratio", "avg_bleu"]:
                    if key in before and key in after:
                        improvement[key] = after[key] - before[key]
                
                self.evaluation_metrics["improvement"] = improvement
            
            logger.info(f"训练后模型评估完成: {trained_metrics}")
            
        except Exception as e:
            logger.error(f"训练后评估失败: {e}")
            self.evaluation_metrics["after_training"] = {"error": str(e)}
    
    def generate_training_report(self):
        """生成训练报告"""
        logger.info("生成训练报告...")
        
        report = {
            "training_timestamp": datetime.now().isoformat(),
            "data_statistics": self.data_stats,
            "training_configuration": self.training_config,
            "evaluation_metrics": self.evaluation_metrics,
            "summary": {
                "total_data_collected": self.data_stats["total_samples"],
                "training_completed": "after_training" in self.evaluation_metrics,
                "performance_improved": False
            }
        }
        
        # 判断性能是否改进
        if "improvement" in self.evaluation_metrics:
            improvements = self.evaluation_metrics["improvement"]
            if any(v > 0 for v in improvements.values() if isinstance(v, (int, float))):
                report["summary"]["performance_improved"] = True
        
        # 保存报告
        report_path = self.output_dir / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"训练报告已保存: {report_path}")
        return report_path
    
    def run_complete_pipeline(self):
        """运行完整的训练管道"""
        logger.info("开始运行完整的模型训练管道...")
        
        try:
            # 1. 加载和准备数据
            train_data, val_data, test_data = self.load_and_prepare_data()
            
            # 2. 准备数据集
            train_dataset, val_dataset, test_dataset = self.prepare_datasets(train_data, val_data, test_data)
            
            # 3. 评估基线
            self.evaluate_baseline(test_data)
            
            # 4. 训练模型
            model_path = self.train_model(train_dataset, val_dataset)
            
            # 5. 评估训练后模型
            if model_path:
                self.evaluate_trained_model(model_path, test_data)
            
            # 6. 生成报告
            report_path = self.generate_training_report()
            
            logger.info("完整训练管道执行完成！")
            return report_path
            
        except Exception as e:
            logger.error(f"训练管道执行失败: {e}")
            return None

def main():
    """主函数"""
    print("🚀 开始大规模模型训练...")
    
    # 创建训练管道
    pipeline = ModelTrainingPipeline()
    
    # 运行完整管道
    report_path = pipeline.run_complete_pipeline()
    
    if report_path:
        print(f"✅ 训练完成！报告已保存至: {report_path}")
        
        # 显示数据统计
        print("\n📊 数据统计:")
        print(f"总数据量: {pipeline.data_stats['total_samples']:,} 条")
        print(f"训练集: {pipeline.data_stats['train_samples']:,} 条")
        print(f"验证集: {pipeline.data_stats['val_samples']:,} 条")
        print(f"测试集: {pipeline.data_stats['test_samples']:,} 条")
        
        print("\n📈 数据来源分布:")
        for source, count in pipeline.data_stats['data_sources'].items():
            print(f"  {source}: {count:,} 条")
        
        print("\n🎯 质量分布:")
        for quality, count in pipeline.data_stats['quality_distribution'].items():
            print(f"  {quality}: {count:,} 条")
        
        # 显示评估结果
        if "before_training" in pipeline.evaluation_metrics:
            print("\n📋 训练前后对比:")
            before = pipeline.evaluation_metrics.get("before_training", {})
            after = pipeline.evaluation_metrics.get("after_training", {})
            improvement = pipeline.evaluation_metrics.get("improvement", {})
            
            for metric in ["avg_length", "non_empty_ratio", "avg_bleu"]:
                if metric in before and metric in after:
                    print(f"  {metric}:")
                    print(f"    训练前: {before[metric]:.4f}")
                    print(f"    训练后: {after[metric]:.4f}")
                    if metric in improvement:
                        print(f"    改进: {improvement[metric]:+.4f}")
    else:
        print("❌ 训练失败，请检查日志")

if __name__ == "__main__":
    main()