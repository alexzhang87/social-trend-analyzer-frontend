#!/usr/bin/env python3
"""
AI专家顾问模型训练脚本
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer,
    get_linear_schedule_with_warmup
)
from data_preprocessing import ExpertAdvisorDataset, create_dataloaders
import logging
from pathlib import Path
import os

# 禁用wandb
os.environ["WANDB_DISABLED"] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpertAdvisorModel(nn.Module):
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

def train_model():
    """训练模型"""
    logger.info("开始训练AI专家顾问模型...")
    
    # 加载配置
    with open("training_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化tokenizer和模型
    tokenizer = AutoTokenizer.from_pretrained(config['training_config']['base_model'])
    tokenizer.pad_token = tokenizer.eos_token
    
    model = ExpertAdvisorModel(
        config['training_config']['base_model'],
        len(config['training_config']['expert_types'])
    )
    
    # 加载数据
    logger.info("加载训练数据...")
    
    # 查找最新的数据文件
    train_files = list(Path(".").glob("train_data_*.json"))
    val_files = list(Path(".").glob("validation_data_*.json"))
    
    if not train_files or not val_files:
        raise FileNotFoundError("找不到训练数据文件")
    
    # 使用最新的文件
    train_file = sorted(train_files)[-1]
    val_file = sorted(val_files)[-1]
    
    logger.info(f"加载训练文件: {train_file}")
    logger.info(f"加载验证文件: {val_file}")
    
    with open(train_file, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    
    with open(val_file, 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    
    logger.info(f"训练数据: {len(train_data)} 条")
    logger.info(f"验证数据: {len(val_data)} 条")
    
    # 创建数据加载器
    train_loader, val_loader = create_dataloaders(
        train_data, val_data, tokenizer,
        config['training_config']['training_parameters']['batch_size']
    )
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir="./model_output",
        num_train_epochs=config['training_config']['training_parameters']['num_epochs'],
        per_device_train_batch_size=config['training_config']['training_parameters']['batch_size'],
        per_device_eval_batch_size=config['training_config']['training_parameters']['batch_size'],
        learning_rate=config['training_config']['training_parameters']['learning_rate'],
        weight_decay=config['training_config']['training_parameters']['weight_decay'],
        warmup_steps=config['training_config']['training_parameters']['warmup_steps'],
        logging_steps=config['training_config']['training_parameters']['logging_steps'],
        save_steps=config['training_config']['training_parameters']['save_steps'],
        eval_steps=config['training_config']['training_parameters']['eval_steps'],
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to=None
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_loader.dataset,
        eval_dataset=val_loader.dataset,
        tokenizer=tokenizer
    )
    
    # 开始训练
    logger.info("开始训练...")
    trainer.train()
    
    # 保存模型
    trainer.save_model("./final_model")
    tokenizer.save_pretrained("./final_model")
    
    logger.info("训练完成!")

if __name__ == "__main__":
    train_model()
