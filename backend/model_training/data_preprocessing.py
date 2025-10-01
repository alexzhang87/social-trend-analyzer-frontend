#!/usr/bin/env python3
"""
数据预处理脚本
"""

import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from pathlib import Path

class ExpertAdvisorDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
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
        
        # 编码输入和输出
        input_text = item['input']
        output_text = item['output']
        
        # 组合输入输出用于训练
        full_text = f"{input_text} {self.tokenizer.eos_token} {output_text}"
        
        # 分词
        encoding = self.tokenizer(
            full_text,
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

def create_dataloaders(train_data, val_data, tokenizer, batch_size=8):
    """创建数据加载器"""
    train_dataset = ExpertAdvisorDataset(train_data, tokenizer)
    val_dataset = ExpertAdvisorDataset(val_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader

if __name__ == "__main__":
    # 测试数据预处理
    from transformers import AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    tokenizer.pad_token = tokenizer.eos_token
    
    # 加载数据
    with open("../final_training_data/final_training_data_latest.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建数据集
    dataset = ExpertAdvisorDataset(data[:10], tokenizer)
    print(f"数据集大小: {len(dataset)}")
    print(f"样本示例: {dataset[0]}")
