#!/usr/bin/env python3
"""
轻量级AI专家顾问模型训练脚本
使用更小的模型和简化的训练流程
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
import logging
from pathlib import Path
import os
from tqdm import tqdm
import time

# 禁用wandb
os.environ["WANDB_DISABLED"] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleExpertDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=256):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # 专家类型映射
        self.expert_to_id = {
            "data_insight": 0,
            "business_strategy": 1,
            "user_insight": 2,
            "competitive_intelligence": 3,
            "failure_prevention": 4
        }
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # 编码输入
        input_text = item['input']
        
        # 分词
        encoding = self.tokenizer(
            input_text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # 专家类型标签
        expert_label = self.expert_to_id.get(item['expert_type'], 0)
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'expert_label': torch.tensor(expert_label, dtype=torch.long),
            'quality_score': torch.tensor(item['quality_score'], dtype=torch.float)
        }

class LightweightExpertModel(nn.Module):
    def __init__(self, model_name="distilbert-base-uncased", num_experts=5):
        super().__init__()
        
        # 使用轻量级的预训练模型
        self.base_model = AutoModel.from_pretrained(model_name)
        
        # 专家分类器
        self.expert_classifier = nn.Sequential(
            nn.Linear(self.base_model.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_experts)
        )
        
        # 质量评分器
        self.quality_scorer = nn.Sequential(
            nn.Linear(self.base_model.config.hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, input_ids, attention_mask):
        # 获取基础模型输出
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # 使用[CLS] token的表示
        pooled_output = outputs.last_hidden_state[:, 0, :]
        
        # 专家分类
        expert_logits = self.expert_classifier(pooled_output)
        
        # 质量评分
        quality_scores = self.quality_scorer(pooled_output)
        
        return expert_logits, quality_scores

def train_lightweight_model():
    logger.info("开始轻量级AI专家顾问模型训练...")
    
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
    
    # 初始化tokenizer和模型
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = LightweightExpertModel(model_name, num_experts=5)
    
    # 创建数据集和数据加载器
    train_dataset = SimpleExpertDataset(train_data, tokenizer)
    val_dataset = SimpleExpertDataset(val_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
    
    # 优化器和损失函数
    optimizer = optim.AdamW(model.parameters(), lr=2e-5)
    expert_criterion = nn.CrossEntropyLoss()
    quality_criterion = nn.MSELoss()
    
    # 训练参数
    num_epochs = 2
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    logger.info(f"使用设备: {device}")
    logger.info(f"训练轮数: {num_epochs}")
    
    # 训练循环
    for epoch in range(num_epochs):
        logger.info(f"开始第 {epoch + 1}/{num_epochs} 轮训练")
        
        model.train()
        total_loss = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}")
        
        for batch_idx, batch in enumerate(progress_bar):
            # 移动数据到设备
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            expert_labels = batch['expert_label'].to(device)
            quality_scores = batch['quality_score'].to(device)
            
            # 前向传播
            expert_logits, predicted_quality = model(input_ids, attention_mask)
            
            # 计算损失
            expert_loss = expert_criterion(expert_logits, expert_labels)
            quality_loss = quality_criterion(predicted_quality.squeeze(), quality_scores)
            total_loss_batch = expert_loss + quality_loss
            
            # 反向传播
            optimizer.zero_grad()
            total_loss_batch.backward()
            optimizer.step()
            
            total_loss += total_loss_batch.item()
            
            # 更新进度条
            progress_bar.set_postfix({
                'Loss': f'{total_loss_batch.item():.4f}',
                'Avg Loss': f'{total_loss / (batch_idx + 1):.4f}'
            })
        
        # 验证
        model.eval()
        val_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                expert_labels = batch['expert_label'].to(device)
                quality_scores = batch['quality_score'].to(device)
                
                expert_logits, predicted_quality = model(input_ids, attention_mask)
                
                expert_loss = expert_criterion(expert_logits, expert_labels)
                quality_loss = quality_criterion(predicted_quality.squeeze(), quality_scores)
                val_loss += (expert_loss + quality_loss).item()
                
                # 计算准确率
                predictions = torch.argmax(expert_logits, dim=1)
                correct_predictions += (predictions == expert_labels).sum().item()
                total_predictions += expert_labels.size(0)
        
        avg_val_loss = val_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions
        
        logger.info(f"轮次 {epoch + 1} 完成:")
        logger.info(f"  训练损失: {total_loss / len(train_loader):.4f}")
        logger.info(f"  验证损失: {avg_val_loss:.4f}")
        logger.info(f"  验证准确率: {accuracy:.4f}")
    
    # 保存模型
    model_save_path = f"lightweight_expert_model_{int(time.time())}.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer_name': model_name,
        'expert_to_id': train_dataset.expert_to_id
    }, model_save_path)
    
    logger.info(f"模型已保存到: {model_save_path}")
    logger.info("轻量级训练完成!")
    
    return model_save_path

if __name__ == "__main__":
    try:
        model_path = train_lightweight_model()
        print(f"\n🎉 训练成功完成!")
        print(f"📁 模型保存路径: {model_path}")
        print(f"🚀 可以使用该模型进行推理测试")
    except Exception as e:
        logger.error(f"训练失败: {e}")
        raise