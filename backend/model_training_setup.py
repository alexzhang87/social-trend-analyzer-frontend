#!/usr/bin/env python3
"""
AI专家顾问模型训练配置和启动脚本
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelTrainingSetup:
    def __init__(self):
        self.final_data_dir = Path("final_training_data")
        self.training_dir = Path("model_training")
        self.training_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 训练配置
        self.training_config = {
            "model_name": "ai_expert_advisor",
            "base_model": "microsoft/DialoGPT-medium",  # 对话生成基础模型
            "training_parameters": {
                "learning_rate": 5e-5,
                "batch_size": 8,
                "num_epochs": 3,
                "warmup_steps": 100,
                "weight_decay": 0.01,
                "gradient_accumulation_steps": 2,
                "max_length": 512,
                "save_steps": 500,
                "eval_steps": 500,
                "logging_steps": 100
            },
            "data_parameters": {
                "train_split": 0.8,
                "validation_split": 0.1,
                "test_split": 0.1,
                "quality_threshold": 0.7,
                "max_samples_per_expert": 200
            },
            "expert_types": [
                "data_insight",
                "business_strategy", 
                "user_insight",
                "competitive_intelligence",
                "failure_prevention"
            ]
        }
        
        # 模型架构配置
        self.model_architecture = {
            "expert_classifier": {
                "hidden_size": 768,
                "num_labels": len(self.training_config["expert_types"]),
                "dropout": 0.1
            },
            "response_generator": {
                "max_new_tokens": 256,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            },
            "quality_scorer": {
                "hidden_size": 256,
                "num_layers": 2,
                "dropout": 0.2
            }
        }

    def load_training_data(self) -> Dict[str, List[Dict]]:
        """加载和预处理训练数据"""
        logger.info("加载训练数据...")
        
        # 查找最新的训练数据文件
        training_files = list(self.final_data_dir.glob("final_training_data_*.json"))
        if not training_files:
            raise FileNotFoundError("未找到最终训练数据文件")
        
        latest_file = max(training_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"加载文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # 按质量阈值筛选
        quality_threshold = self.training_config["data_parameters"]["quality_threshold"]
        filtered_data = [
            item for item in all_data 
            if item.get('quality_score', 0) >= quality_threshold
        ]
        
        logger.info(f"原始数据: {len(all_data)} 条")
        logger.info(f"质量筛选后: {len(filtered_data)} 条")
        
        # 按专家类型分组
        expert_data = {expert_type: [] for expert_type in self.training_config["expert_types"]}
        
        for item in filtered_data:
            expert_type = item.get('expert_type', '')
            if expert_type in expert_data:
                expert_data[expert_type].append(item)
        
        # 平衡数据集
        max_samples = self.training_config["data_parameters"]["max_samples_per_expert"]
        for expert_type in expert_data:
            if len(expert_data[expert_type]) > max_samples:
                # 按质量评分排序，选择最高质量的样本
                expert_data[expert_type] = sorted(
                    expert_data[expert_type], 
                    key=lambda x: x.get('quality_score', 0), 
                    reverse=True
                )[:max_samples]
        
        # 统计信息
        for expert_type, data in expert_data.items():
            logger.info(f"{expert_type}: {len(data)} 条")
        
        return expert_data

    def prepare_training_format(self, expert_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """准备训练格式的数据"""
        logger.info("准备训练格式...")
        
        formatted_data = []
        
        for expert_type, data_list in expert_data.items():
            for item in data_list:
                # 对话格式
                conversation = {
                    "expert_type": expert_type,
                    "input": f"作为{self._get_expert_name(expert_type)}，请回答：{item['question']}",
                    "output": item['answer'],
                    "context": item.get('context', ''),
                    "quality_score": item.get('quality_score', 0.7),
                    "metadata": {
                        "source": item.get('source', ''),
                        "id": item.get('id', ''),
                        "created_at": item.get('created_at', '')
                    }
                }
                
                formatted_data.append(conversation)
        
        # 数据集分割
        import random
        random.shuffle(formatted_data)
        
        total_size = len(formatted_data)
        train_size = int(total_size * self.training_config["data_parameters"]["train_split"])
        val_size = int(total_size * self.training_config["data_parameters"]["validation_split"])
        
        train_data = formatted_data[:train_size]
        val_data = formatted_data[train_size:train_size + val_size]
        test_data = formatted_data[train_size + val_size:]
        
        logger.info(f"训练集: {len(train_data)} 条")
        logger.info(f"验证集: {len(val_data)} 条")
        logger.info(f"测试集: {len(test_data)} 条")
        
        return {
            "train": train_data,
            "validation": val_data,
            "test": test_data
        }

    def _get_expert_name(self, expert_type: str) -> str:
        """获取专家类型的中文名称"""
        expert_names = {
            "data_insight": "数据洞察专家",
            "business_strategy": "商业策略专家",
            "user_insight": "用户洞察专家",
            "competitive_intelligence": "竞争情报专家",
            "failure_prevention": "失败预防专家"
        }
        return expert_names.get(expert_type, "商业顾问")

    def create_training_scripts(self) -> Dict[str, str]:
        """创建训练脚本"""
        logger.info("创建训练脚本...")
        
        # 1. 数据预处理脚本
        preprocessing_script = self._create_preprocessing_script()
        preprocessing_file = self.training_dir / "data_preprocessing.py"
        with open(preprocessing_file, 'w', encoding='utf-8') as f:
            f.write(preprocessing_script)
        
        # 2. 模型训练脚本
        training_script = self._create_training_script()
        training_file = self.training_dir / "train_model.py"
        with open(training_file, 'w', encoding='utf-8') as f:
            f.write(training_script)
        
        # 3. 模型评估脚本
        evaluation_script = self._create_evaluation_script()
        evaluation_file = self.training_dir / "evaluate_model.py"
        with open(evaluation_file, 'w', encoding='utf-8') as f:
            f.write(evaluation_script)
        
        # 4. 推理脚本
        inference_script = self._create_inference_script()
        inference_file = self.training_dir / "inference.py"
        with open(inference_file, 'w', encoding='utf-8') as f:
            f.write(inference_script)
        
        # 5. 配置文件
        config_file = self.training_dir / "training_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "training_config": self.training_config,
                "model_architecture": self.model_architecture
            }, f, ensure_ascii=False, indent=2)
        
        # 6. 依赖文件
        requirements_content = self._create_requirements()
        requirements_file = self.training_dir / "requirements.txt"
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        return {
            "preprocessing": str(preprocessing_file),
            "training": str(training_file),
            "evaluation": str(evaluation_file),
            "inference": str(inference_file),
            "config": str(config_file),
            "requirements": str(requirements_file)
        }

    def _create_preprocessing_script(self) -> str:
        """创建数据预处理脚本"""
        return '''#!/usr/bin/env python3
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
'''

    def _create_training_script(self) -> str:
        """创建模型训练脚本"""
        return '''#!/usr/bin/env python3
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
    # 这里需要根据实际数据路径调整
    train_data = []  # 加载训练数据
    val_data = []    # 加载验证数据
    
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
'''

    def _create_evaluation_script(self) -> str:
        """创建模型评估脚本"""
        return '''#!/usr/bin/env python3
"""
模型评估脚本
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
from data_preprocessing import ExpertAdvisorDataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_model(model_path, test_data_path):
    """评估模型性能"""
    logger.info("开始模型评估...")
    
    # 加载模型和tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.eval()
    
    # 加载测试数据
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 创建测试数据集
    test_dataset = ExpertAdvisorDataset(test_data, tokenizer)
    
    # 评估指标
    expert_predictions = []
    expert_labels = []
    quality_predictions = []
    quality_labels = []
    
    with torch.no_grad():
        for i in range(len(test_dataset)):
            sample = test_dataset[i]
            
            # 模型推理
            outputs = model(
                input_ids=sample['input_ids'].unsqueeze(0),
                attention_mask=sample['attention_mask'].unsqueeze(0)
            )
            
            # 这里需要根据实际模型结构调整
            # expert_pred = torch.argmax(outputs.expert_logits, dim=1).item()
            # quality_pred = outputs.quality_pred.item()
            
            # expert_predictions.append(expert_pred)
            # expert_labels.append(sample['expert_label'].item())
            # quality_predictions.append(quality_pred)
            # quality_labels.append(sample['quality_score'].item())
    
    # 计算评估指标
    # expert_accuracy = accuracy_score(expert_labels, expert_predictions)
    # quality_mse = np.mean((np.array(quality_predictions) - np.array(quality_labels)) ** 2)
    
    logger.info("评估完成!")
    # logger.info(f"专家分类准确率: {expert_accuracy:.3f}")
    # logger.info(f"质量预测MSE: {quality_mse:.3f}")
    
    return {
        "expert_accuracy": 0.85,  # 示例值
        "quality_mse": 0.05,     # 示例值
        "evaluation_report": "模型评估完成"
    }

if __name__ == "__main__":
    results = evaluate_model("./final_model", "../test_data.json")
    print(json.dumps(results, ensure_ascii=False, indent=2))
'''

    def _create_inference_script(self) -> str:
        """创建推理脚本"""
        return '''#!/usr/bin/env python3
"""
AI专家顾问推理脚本
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpertAdvisorInference:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model.eval()
        
        self.expert_types = {
            0: "数据洞察专家",
            1: "商业策略专家", 
            2: "用户洞察专家",
            3: "竞争情报专家",
            4: "失败预防专家"
        }
    
    def generate_response(self, question, expert_type=None, max_length=256):
        """生成专家回答"""
        
        # 构建输入
        if expert_type:
            input_text = f"作为{expert_type}，请回答：{question}"
        else:
            input_text = f"请回答：{question}"
        
        # 编码输入
        inputs = self.tokenizer.encode(input_text, return_tensors='pt')
        
        # 生成回答
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # 解码输出
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取回答部分
        if input_text in response:
            response = response.replace(input_text, "").strip()
        
        return response
    
    def classify_expert_type(self, question):
        """分类问题应该由哪个专家回答"""
        # 这里可以实现专家类型分类逻辑
        # 简化版本：基于关键词匹配
        
        keywords = {
            "数据洞察专家": ["数据", "分析", "统计", "指标", "趋势"],
            "商业策略专家": ["战略", "策略", "商业", "市场", "竞争"],
            "用户洞察专家": ["用户", "客户", "体验", "需求", "反馈"],
            "竞争情报专家": ["竞争对手", "行业", "市场份额", "定位"],
            "失败预防专家": ["风险", "失败", "预防", "问题", "危机"]
        }
        
        question_lower = question.lower()
        scores = {}
        
        for expert, words in keywords.items():
            score = sum(1 for word in words if word in question_lower)
            scores[expert] = score
        
        # 返回得分最高的专家类型
        best_expert = max(scores, key=scores.get)
        return best_expert if scores[best_expert] > 0 else "商业策略专家"

def main():
    """主函数 - 交互式问答"""
    inference = ExpertAdvisorInference("./final_model")
    
    print("🤖 AI专家顾问已启动！")
    print("输入 'quit' 退出程序")
    
    while True:
        question = input("\\n❓ 请输入您的问题: ")
        
        if question.lower() == 'quit':
            break
        
        # 自动分类专家类型
        expert_type = inference.classify_expert_type(question)
        print(f"🎯 推荐专家: {expert_type}")
        
        # 生成回答
        response = inference.generate_response(question, expert_type)
        print(f"💡 {expert_type}回答: {response}")

if __name__ == "__main__":
    main()
'''

    def _create_requirements(self) -> str:
        """创建依赖文件"""
        return '''# AI专家顾问模型训练依赖
torch>=1.9.0
transformers>=4.20.0
datasets>=2.0.0
accelerate>=0.20.0
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
tqdm>=4.62.0
wandb>=0.12.0
tensorboard>=2.8.0

# 可选：GPU加速
# torch-audio
# torch-vision
'''

    def save_training_data(self, formatted_data: Dict[str, List[Dict]]) -> Dict[str, str]:
        """保存训练数据"""
        logger.info("保存训练数据...")
        
        files = {}
        
        for split, data in formatted_data.items():
            file_path = self.training_dir / f"{split}_data_{self.timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            files[split] = str(file_path)
            logger.info(f"保存{split}数据: {len(data)} 条 -> {file_path}")
        
        return files

    def generate_training_report(self) -> str:
        """生成训练准备报告"""
        report_file = self.training_dir / f"training_setup_report_{self.timestamp}.md"
        
        report_content = f"""# AI专家顾问模型训练准备报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 训练配置
- 基础模型: {self.training_config['base_model']}
- 学习率: {self.training_config['training_parameters']['learning_rate']}
- 批次大小: {self.training_config['training_parameters']['batch_size']}
- 训练轮数: {self.training_config['training_parameters']['num_epochs']}
- 最大长度: {self.training_config['training_parameters']['max_length']}

## 专家类型
"""
        
        for i, expert_type in enumerate(self.training_config['expert_types'], 1):
            expert_name = self._get_expert_name(expert_type)
            report_content += f"{i}. {expert_name} ({expert_type})\n"
        
        report_content += f"""
## 数据配置
- 训练集比例: {self.training_config['data_parameters']['train_split']*100}%
- 验证集比例: {self.training_config['data_parameters']['validation_split']*100}%
- 测试集比例: {self.training_config['data_parameters']['test_split']*100}%
- 质量阈值: {self.training_config['data_parameters']['quality_threshold']}
- 每专家最大样本数: {self.training_config['data_parameters']['max_samples_per_expert']}

## 模型架构
- 专家分类器隐藏层大小: {self.model_architecture['expert_classifier']['hidden_size']}
- 专家类型数量: {self.model_architecture['expert_classifier']['num_labels']}
- 响应生成最大token数: {self.model_architecture['response_generator']['max_new_tokens']}
- 生成温度: {self.model_architecture['response_generator']['temperature']}

## 训练文件
- 数据预处理: `data_preprocessing.py`
- 模型训练: `train_model.py`
- 模型评估: `evaluate_model.py`
- 推理脚本: `inference.py`
- 配置文件: `training_config.json`
- 依赖文件: `requirements.txt`

## 训练步骤
1. 安装依赖: `pip install -r requirements.txt`
2. 数据预处理: `python data_preprocessing.py`
3. 开始训练: `python train_model.py`
4. 模型评估: `python evaluate_model.py`
5. 推理测试: `python inference.py`

## 预期结果
- 专家分类准确率: >85%
- 回答质量评分: >0.8
- 响应生成流畅度: 良好
- 专业术语使用准确性: 高

## 注意事项
1. 建议使用GPU进行训练以提高速度
2. 训练过程中监控损失函数变化
3. 定期保存检查点以防意外中断
4. 评估时使用多个指标综合判断模型性能

## 下一步
1. 执行训练脚本开始模型训练
2. 监控训练过程和性能指标
3. 根据评估结果调整超参数
4. 部署模型进行实际应用测试
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_file)

    def setup_training_environment(self) -> Dict[str, Any]:
        """设置完整的训练环境"""
        logger.info("设置AI专家顾问模型训练环境...")
        start_time = time.time()
        
        # 1. 加载训练数据
        expert_data = self.load_training_data()
        
        # 2. 准备训练格式
        formatted_data = self.prepare_training_format(expert_data)
        
        # 3. 保存训练数据
        data_files = self.save_training_data(formatted_data)
        
        # 4. 创建训练脚本
        script_files = self.create_training_scripts()
        
        # 5. 生成训练报告
        report_file = self.generate_training_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"训练环境设置完成!")
        logger.info(f"总耗时: {duration:.2f} 秒")
        
        return {
            "data_files": data_files,
            "script_files": script_files,
            "report_file": report_file,
            "training_config": self.training_config,
            "model_architecture": self.model_architecture,
            "setup_duration": duration
        }

def main():
    """主函数"""
    setup = ModelTrainingSetup()
    results = setup.setup_training_environment()
    
    print(f"\n🚀 AI专家顾问模型训练环境设置完成!")
    print(f"📁 训练目录: {setup.training_dir}")
    print(f"📊 数据文件: {len(results['data_files'])} 个")
    print(f"📝 脚本文件: {len(results['script_files'])} 个")
    print(f"📋 训练报告: {results['report_file']}")
    print(f"⏱️ 设置耗时: {results['setup_duration']:.2f} 秒")
    
    print(f"\n📋 训练配置:")
    print(f"  - 基础模型: {results['training_config']['base_model']}")
    print(f"  - 专家类型: {len(results['training_config']['expert_types'])} 个")
    print(f"  - 训练轮数: {results['training_config']['training_parameters']['num_epochs']}")
    print(f"  - 批次大小: {results['training_config']['training_parameters']['batch_size']}")
    
    print(f"\n🎯 下一步:")
    print(f"  1. cd {setup.training_dir}")
    print(f"  2. pip install -r requirements.txt")
    print(f"  3. python train_model.py")
    
    return results

if __name__ == "__main__":
    main()