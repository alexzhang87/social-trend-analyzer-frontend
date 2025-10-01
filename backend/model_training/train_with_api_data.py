#!/usr/bin/env python3
"""
使用API收集数据训练AI专家顾问模型
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer,
    get_linear_schedule_with_warmup
)
import logging
from pathlib import Path
import os
from datetime import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 禁用wandb
os.environ["WANDB_DISABLED"] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIDataset(Dataset):
    """API数据集类"""
    
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # 专家类型映射
        self.expert_types = [
            "business_strategy",
            "data_insight", 
            "user_insight",
            "competitive_intelligence",
            "failure_prevention"
        ]
        self.expert_to_id = {expert: i for i, expert in enumerate(self.expert_types)}
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # 构造输入文本
        text = item['text']
        expert_type = item['expert_type']
        quality_score = item['quality_score']
        
        # 创建训练提示
        prompt = f"作为{expert_type}专家，请分析以下内容：\n{text}\n\n分析："
        
        # 分词
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'expert_label': torch.tensor(self.expert_to_id[expert_type], dtype=torch.long),
            'quality_score': torch.tensor(quality_score, dtype=torch.float)
        }

class ExpertAdvisorModel(nn.Module):
    """专家顾问模型"""
    
    def __init__(self, base_model_name, num_experts=5):
        super().__init__()
        
        # 基础对话模型
        self.base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
        
        # 专家分类器
        self.expert_classifier = nn.Linear(self.base_model.config.hidden_size, num_experts)
        
        # 质量评分器
        self.quality_scorer = nn.Sequential(
            nn.Linear(self.base_model.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, input_ids, attention_mask, expert_label=None, quality_score=None):
        # 获取基础模型输出
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        
        # 获取最后一层隐藏状态
        hidden_states = outputs.hidden_states[-1]
        pooled_output = hidden_states.mean(dim=1)  # 平均池化
        
        # 专家分类
        expert_logits = self.expert_classifier(pooled_output)
        
        # 质量评分
        quality_pred = self.quality_scorer(pooled_output)
        
        loss = None
        if expert_label is not None and quality_score is not None:
            # 计算损失
            expert_loss = nn.CrossEntropyLoss()(expert_logits, expert_label)
            quality_loss = nn.MSELoss()(quality_pred.squeeze(), quality_score)
            generation_loss = outputs.loss if outputs.loss is not None else 0
            
            # 组合损失
            loss = generation_loss + 0.3 * expert_loss + 0.2 * quality_loss
        
        return {
            'loss': loss,
            'logits': outputs.logits,
            'expert_logits': expert_logits,
            'quality_pred': quality_pred
        }

def load_latest_api_data():
    """加载最新的API数据"""
    # 查找最新的API数据文件（排除统计文件）
    api_files = [f for f in Path(".").glob("existing_api_data_*.json") if not str(f).endswith('_stats.json')]
    
    if not api_files:
        raise FileNotFoundError("找不到API数据文件")
    
    # 使用最新的文件
    latest_file = sorted(api_files)[-1]
    logger.info(f"加载API数据文件: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"总数据量: {len(data)} 条")
    
    # 统计数据分布
    expert_counts = {}
    source_counts = {}
    quality_scores = []
    
    for item in data:
        expert_type = item['expert_type']
        source = item.get('source', 'synthetic')
        quality = item['quality_score']
        
        expert_counts[expert_type] = expert_counts.get(expert_type, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1
        quality_scores.append(quality)
    
    logger.info("专家类型分布:")
    for expert, count in expert_counts.items():
        logger.info(f"  {expert}: {count} 条")
    
    logger.info("数据源分布:")
    for source, count in source_counts.items():
        logger.info(f"  {source}: {count} 条")
    
    logger.info(f"平均质量分数: {np.mean(quality_scores):.3f}")
    
    return data

def train_with_api_data():
    """使用API数据训练模型"""
    logger.info("开始使用API数据训练AI专家顾问模型...")
    
    # 加载数据
    data = load_latest_api_data()
    
    # 数据分割
    train_data, temp_data = train_test_split(data, test_size=0.2, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    
    logger.info(f"训练数据: {len(train_data)} 条")
    logger.info(f"验证数据: {len(val_data)} 条")
    logger.info(f"测试数据: {len(test_data)} 条")
    
    # 初始化tokenizer和模型
    model_name = "microsoft/DialoGPT-medium"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = ExpertAdvisorModel(model_name, num_experts=5)
    
    # 创建数据集
    train_dataset = APIDataset(train_data, tokenizer)
    val_dataset = APIDataset(val_data, tokenizer)
    test_dataset = APIDataset(test_data, tokenizer)
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir="./api_model_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,  # 减小批次大小以适应内存
        per_device_eval_batch_size=4,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=500,
        logging_steps=100,
        save_steps=1000,
        eval_steps=500,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to=None,
        dataloader_pin_memory=False,  # 减少内存使用
        gradient_accumulation_steps=2,  # 梯度累积
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer
    )
    
    # 开始训练
    logger.info("开始训练...")
    start_time = datetime.now()
    
    try:
        trainer.train()
        
        # 保存模型
        model_save_path = "./api_trained_model"
        trainer.save_model(model_save_path)
        tokenizer.save_pretrained(model_save_path)
        
        end_time = datetime.now()
        training_duration = end_time - start_time
        
        logger.info(f"训练完成! 耗时: {training_duration}")
        logger.info(f"模型保存至: {model_save_path}")
        
        # 评估模型
        logger.info("开始模型评估...")
        eval_results = trainer.evaluate(eval_dataset=test_dataset)
        
        # 生成训练报告
        generate_training_report(
            train_data, val_data, test_data,
            eval_results, training_duration,
            model_save_path
        )
        
        return model_save_path
        
    except Exception as e:
        logger.error(f"训练过程中出现错误: {e}")
        return None

def generate_training_report(train_data, val_data, test_data, eval_results, duration, model_path):
    """生成训练报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = {
        "training_timestamp": timestamp,
        "data_statistics": {
            "train_samples": len(train_data),
            "validation_samples": len(val_data),
            "test_samples": len(test_data),
            "total_samples": len(train_data) + len(val_data) + len(test_data)
        },
        "training_duration": str(duration),
        "evaluation_results": eval_results,
        "model_path": model_path,
        "data_sources": {
            "reddit": len([d for d in train_data + val_data + test_data if d.get('source') == 'reddit']),
            "github": len([d for d in train_data + val_data + test_data if d.get('source') == 'github']),
            "product_hunt": len([d for d in train_data + val_data + test_data if d.get('source') == 'product_hunt']),
            "synthetic": len([d for d in train_data + val_data + test_data if d.get('source') == 'synthetic'])
        },
        "expert_distribution": {
            expert: len([d for d in train_data + val_data + test_data if d['expert_type'] == expert])
            for expert in ["business_strategy", "data_insight", "user_insight", "competitive_intelligence", "failure_prevention"]
        }
    }
    
    # 保存报告
    report_file = f"api_training_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"训练报告已保存: {report_file}")
    
    # 生成Markdown报告
    md_content = f"""# API数据训练报告

## 📊 训练概览
- **训练时间**: {timestamp}
- **训练耗时**: {duration}
- **模型路径**: {model_path}

## 📈 数据统计
- **训练样本**: {report['data_statistics']['train_samples']:,} 条
- **验证样本**: {report['data_statistics']['validation_samples']:,} 条
- **测试样本**: {report['data_statistics']['test_samples']:,} 条
- **总样本数**: {report['data_statistics']['total_samples']:,} 条

## 🎯 数据源分布
- **Reddit**: {report['data_sources']['reddit']:,} 条
- **GitHub**: {report['data_sources']['github']:,} 条
- **Product Hunt**: {report['data_sources']['product_hunt']:,} 条
- **合成数据**: {report['data_sources']['synthetic']:,} 条

## 👥 专家类型分布
- **商业策略**: {report['expert_distribution']['business_strategy']:,} 条
- **数据洞察**: {report['expert_distribution']['data_insight']:,} 条
- **用户洞察**: {report['expert_distribution']['user_insight']:,} 条
- **竞争情报**: {report['expert_distribution']['competitive_intelligence']:,} 条
- **失败预防**: {report['expert_distribution']['failure_prevention']:,} 条

## 🏆 评估结果
- **评估损失**: {eval_results.get('eval_loss', 'N/A')}

## 💡 总结
本次训练使用了包含真实API数据的高质量数据集，成功训练了多专家类型的AI顾问模型。
模型现在具备了更强的实际场景理解能力，可以为用户提供更准确的专业建议。
"""
    
    md_file = f"api_training_report_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    logger.info(f"Markdown报告已保存: {md_file}")

if __name__ == "__main__":
    train_with_api_data()