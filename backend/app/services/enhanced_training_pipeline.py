"""
增强训练管道 - 集成免费数据源
基于现有ModelTrainingPipeline扩展，支持免费数据源集成
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import pandas as pd
from .free_data_integration_service import FreeDataIntegrationService

logger = logging.getLogger(__name__)

class EnhancedTrainingPipeline:
    """增强训练管道 - 支持免费数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_integration_service = FreeDataIntegrationService()
        
        # 训练配置
        self.model_name = config.get("model_name", "microsoft/DialoGPT-medium")
        self.output_dir = Path(config.get("output_dir", "./models/enhanced_model"))
        self.data_dir = Path(config.get("data_dir", "./data/training"))
        
        # 创建目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 训练参数
        self.training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            num_train_epochs=config.get("num_epochs", 3),
            per_device_train_batch_size=config.get("batch_size", 4),
            per_device_eval_batch_size=config.get("eval_batch_size", 4),
            warmup_steps=config.get("warmup_steps", 500),
            logging_steps=config.get("logging_steps", 100),
            save_steps=config.get("save_steps", 1000),
            evaluation_strategy="steps",
            eval_steps=config.get("eval_steps", 500),
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            gradient_accumulation_steps=config.get("gradient_accumulation_steps", 2),
            learning_rate=config.get("learning_rate", 5e-5),
            weight_decay=config.get("weight_decay", 0.01),
            adam_epsilon=config.get("adam_epsilon", 1e-8),
            max_grad_norm=config.get("max_grad_norm", 1.0),
            fp16=config.get("fp16", True),
            logging_dir=str(self.output_dir / "logs"),
            report_to=[]  # 禁用wandb等外部报告
        )

    async def run_enhanced_training(self) -> Dict[str, Any]:
        """运行增强训练流程"""
        logger.info("开始增强训练流程...")
        
        try:
            # 1. 集成免费数据源
            logger.info("步骤1: 集成免费数据源")
            integration_result = await self.data_integration_service.integrate_all_sources()
            
            # 2. 加载和预处理数据
            logger.info("步骤2: 加载和预处理训练数据")
            train_dataset, eval_dataset = await self.prepare_training_data(
                integration_result["output_file"]
            )
            
            # 3. 初始化模型和tokenizer
            logger.info("步骤3: 初始化模型和tokenizer")
            model, tokenizer = self.initialize_model_and_tokenizer()
            
            # 4. 配置训练器
            logger.info("步骤4: 配置训练器")
            trainer = self.setup_trainer(model, tokenizer, train_dataset, eval_dataset)
            
            # 5. 执行训练
            logger.info("步骤5: 开始模型训练")
            training_result = trainer.train()
            
            # 6. 保存模型
            logger.info("步骤6: 保存训练后的模型")
            self.save_model(trainer, tokenizer)
            
            # 7. 评估模型
            logger.info("步骤7: 评估模型性能")
            evaluation_result = self.evaluate_model(trainer, eval_dataset)
            
            # 8. 生成训练报告
            training_report = self.generate_training_report(
                integration_result,
                training_result,
                evaluation_result
            )
            
            logger.info("增强训练流程完成!")
            return training_report
            
        except Exception as e:
            logger.error(f"增强训练失败: {str(e)}")
            raise

    async def prepare_training_data(self, data_file: str) -> tuple:
        """准备训练数据"""
        logger.info(f"从 {data_file} 加载训练数据")
        
        # 加载集成的数据
        with open(data_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # 转换为训练格式
        training_examples = []
        for item in raw_data:
            # 创建对话格式的训练样本
            conversation = self.format_conversation(item)
            training_examples.append({
                "text": conversation,
                "source": item.get("source", "unknown"),
                "quality_score": item.get("quality_score", 0.8)
            })
        
        # 按质量分数排序，优先使用高质量数据
        training_examples.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # 分割训练集和验证集 (90% / 10%)
        split_idx = int(len(training_examples) * 0.9)
        train_data = training_examples[:split_idx]
        eval_data = training_examples[split_idx:]
        
        logger.info(f"训练数据准备完成: {len(train_data)} 训练样本, {len(eval_data)} 验证样本")
        
        # 转换为Dataset对象
        train_dataset = Dataset.from_pandas(pd.DataFrame(train_data))
        eval_dataset = Dataset.from_pandas(pd.DataFrame(eval_data))
        
        return train_dataset, eval_dataset

    def format_conversation(self, item: Dict) -> str:
        """格式化对话为训练文本"""
        instruction = item.get("instruction", "")
        input_text = item.get("input", "")
        output = item.get("output", "")
        
        # 创建对话格式
        if input_text:
            conversation = f"Human: {instruction}\n{input_text}\n\nAssistant: {output}"
        else:
            conversation = f"Human: {instruction}\n\nAssistant: {output}"
        
        return conversation

    def initialize_model_and_tokenizer(self):
        """初始化模型和tokenizer"""
        logger.info(f"加载模型: {self.model_name}")
        
        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.training_args.fp16 else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # 调整模型配置
        model.config.pad_token_id = tokenizer.pad_token_id
        
        return model, tokenizer

    def setup_trainer(self, model, tokenizer, train_dataset, eval_dataset):
        """设置训练器"""
        
        def tokenize_function(examples):
            """tokenize函数"""
            # tokenize文本
            tokenized = tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # 设置labels为input_ids的副本（用于语言建模）
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # 应用tokenization
        train_dataset = train_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        
        eval_dataset = eval_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=eval_dataset.column_names
        )
        
        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # 不使用masked language modeling
        )
        
        # 创建训练器
        trainer = Trainer(
            model=model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )
        
        return trainer

    def save_model(self, trainer, tokenizer):
        """保存训练后的模型"""
        logger.info(f"保存模型到: {self.output_dir}")
        
        # 保存模型
        trainer.save_model()
        tokenizer.save_pretrained(self.output_dir)
        
        # 保存训练配置
        config_file = self.output_dir / "training_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        logger.info("模型保存完成")

    def evaluate_model(self, trainer, eval_dataset) -> Dict[str, Any]:
        """评估模型性能"""
        logger.info("开始模型评估...")
        
        # 运行评估
        eval_result = trainer.evaluate()
        
        # 计算困惑度
        perplexity = torch.exp(torch.tensor(eval_result["eval_loss"]))
        
        evaluation_metrics = {
            "eval_loss": eval_result["eval_loss"],
            "perplexity": float(perplexity),
            "eval_samples": len(eval_dataset),
            "evaluation_time": datetime.utcnow().isoformat()
        }
        
        logger.info(f"评估完成 - 困惑度: {perplexity:.2f}")
        return evaluation_metrics

    def generate_training_report(self, integration_result, training_result, evaluation_result) -> Dict[str, Any]:
        """生成训练报告"""
        
        report = {
            "training_summary": {
                "model_name": self.model_name,
                "output_dir": str(self.output_dir),
                "training_completed_at": datetime.utcnow().isoformat(),
                "total_training_steps": training_result.global_step,
                "final_loss": training_result.training_loss
            },
            "data_integration": {
                "total_samples": integration_result["total_samples"],
                "source_breakdown": integration_result["source_breakdown"],
                "quality_distribution": integration_result["quality_distribution"]
            },
            "model_performance": evaluation_result,
            "training_configuration": {
                "epochs": self.training_args.num_train_epochs,
                "batch_size": self.training_args.per_device_train_batch_size,
                "learning_rate": self.training_args.learning_rate,
                "warmup_steps": self.training_args.warmup_steps
            },
            "recommendations": self.generate_recommendations(evaluation_result)
        }
        
        # 保存报告
        report_file = self.output_dir / "training_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"训练报告已保存: {report_file}")
        return report

    def generate_recommendations(self, evaluation_result) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        perplexity = evaluation_result.get("perplexity", float('inf'))
        
        if perplexity > 50:
            recommendations.append("困惑度较高，建议增加训练轮数或调整学习率")
        elif perplexity < 10:
            recommendations.append("模型性能良好，可以考虑部署到生产环境")
        
        if evaluation_result.get("eval_loss", 0) > 2.0:
            recommendations.append("验证损失较高，建议检查数据质量或调整模型架构")
        
        recommendations.extend([
            "定期使用新的免费数据源更新训练数据",
            "监控模型在实际咨询场景中的表现",
            "考虑实施在线学习机制以持续改进模型"
        ])
        
        return recommendations

# 配置示例
DEFAULT_CONFIG = {
    "model_name": "microsoft/DialoGPT-medium",
    "output_dir": "./models/enhanced_startup_consultant",
    "data_dir": "./data/training",
    "num_epochs": 3,
    "batch_size": 4,
    "eval_batch_size": 4,
    "learning_rate": 5e-5,
    "warmup_steps": 500,
    "logging_steps": 100,
    "save_steps": 1000,
    "eval_steps": 500,
    "gradient_accumulation_steps": 2,
    "weight_decay": 0.01,
    "adam_epsilon": 1e-8,
    "max_grad_norm": 1.0,
    "fp16": True
}

# 使用示例
async def main():
    """主函数示例"""
    
    # 创建训练管道
    pipeline = EnhancedTrainingPipeline(DEFAULT_CONFIG)
    
    try:
        # 运行增强训练
        result = await pipeline.run_enhanced_training()
        
        print("增强训练完成!")
        print(f"模型保存位置: {result['training_summary']['output_dir']}")
        print(f"最终困惑度: {result['model_performance']['perplexity']:.2f}")
        print(f"训练样本总数: {result['data_integration']['total_samples']}")
        
        # 打印建议
        print("\n优化建议:")
        for rec in result["recommendations"]:
            print(f"- {rec}")
            
    except Exception as e:
        print(f"训练失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())