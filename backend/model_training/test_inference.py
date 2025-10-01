#!/usr/bin/env python3
"""
AI专家顾问模型推理测试脚本
"""

import json
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class ExpertAdvisorInference:
    def __init__(self, model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载模型检查点
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # 初始化tokenizer和模型
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint['tokenizer_name'])
        self.model = LightweightExpertModel(checkpoint['tokenizer_name'], num_experts=5)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # 专家类型映射
        self.expert_to_id = checkpoint['expert_to_id']
        self.id_to_expert = {v: k for k, v in self.expert_to_id.items()}
        
        logger.info(f"模型加载完成，使用设备: {self.device}")
        logger.info(f"支持的专家类型: {list(self.expert_to_id.keys())}")
    
    def predict(self, text):
        """对输入文本进行专家类型预测和质量评分"""
        # 分词
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=256,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            expert_logits, quality_scores = self.model(input_ids, attention_mask)
            
            # 获取预测结果
            expert_probs = torch.softmax(expert_logits, dim=1)
            predicted_expert_id = torch.argmax(expert_probs, dim=1).item()
            predicted_expert = self.id_to_expert[predicted_expert_id]
            confidence = expert_probs[0][predicted_expert_id].item()
            quality_score = quality_scores[0].item()
            
            return {
                'predicted_expert': predicted_expert,
                'confidence': confidence,
                'quality_score': quality_score,
                'all_probabilities': {
                    self.id_to_expert[i]: prob.item() 
                    for i, prob in enumerate(expert_probs[0])
                }
            }
    
    def batch_predict(self, texts):
        """批量预测"""
        results = []
        for text in texts:
            result = self.predict(text)
            result['input_text'] = text
            results.append(result)
        return results

def test_model_performance():
    """测试模型性能"""
    logger.info("开始模型推理测试...")
    
    # 查找最新的模型文件
    model_files = list(Path(".").glob("lightweight_expert_model_*.pth"))
    if not model_files:
        raise FileNotFoundError("找不到训练好的模型文件")
    
    model_file = sorted(model_files)[-1]
    logger.info(f"使用模型文件: {model_file}")
    
    # 初始化推理器
    inference = ExpertAdvisorInference(model_file)
    
    # 测试用例
    test_cases = [
        "如何分析用户行为数据来提升产品转化率？",
        "我们的竞争对手在市场上有什么优势？",
        "如何制定有效的商业策略来扩大市场份额？",
        "用户反馈显示产品体验不佳，如何改进？",
        "这个数据集包含了什么样的商业洞察？",
        "我们的产品为什么会失败？有什么预防措施？",
        "如何进行市场细分和目标用户定位？",
        "竞争对手的定价策略是什么？",
        "如何利用数据驱动决策？",
        "用户留存率低的原因是什么？"
    ]
    
    logger.info(f"开始测试 {len(test_cases)} 个用例...")
    
    # 批量预测
    results = inference.batch_predict(test_cases)
    
    # 分析结果
    expert_counts = {}
    total_confidence = 0
    total_quality = 0
    
    print("\n" + "="*80)
    print("AI专家顾问模型推理测试结果")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        expert = result['predicted_expert']
        confidence = result['confidence']
        quality = result['quality_score']
        
        expert_counts[expert] = expert_counts.get(expert, 0) + 1
        total_confidence += confidence
        total_quality += quality
        
        print(f"\n测试用例 {i}:")
        print(f"输入: {result['input_text']}")
        print(f"预测专家: {expert}")
        print(f"置信度: {confidence:.3f}")
        print(f"质量评分: {quality:.3f}")
        print("所有专家概率:")
        for exp, prob in result['all_probabilities'].items():
            print(f"  {exp}: {prob:.3f}")
    
    # 统计信息
    avg_confidence = total_confidence / len(results)
    avg_quality = total_quality / len(results)
    
    print("\n" + "="*80)
    print("统计信息")
    print("="*80)
    print(f"平均置信度: {avg_confidence:.3f}")
    print(f"平均质量评分: {avg_quality:.3f}")
    print("\n专家类型分布:")
    for expert, count in expert_counts.items():
        percentage = (count / len(results)) * 100
        print(f"  {expert}: {count} 次 ({percentage:.1f}%)")
    
    # 保存测试结果
    test_report = {
        'model_file': str(model_file),
        'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_cases': len(test_cases),
        'average_confidence': avg_confidence,
        'average_quality': avg_quality,
        'expert_distribution': expert_counts,
        'detailed_results': results
    }
    
    report_file = f"inference_test_report_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"测试报告已保存到: {report_file}")
    
    return test_report

if __name__ == "__main__":
    try:
        report = test_model_performance()
        print(f"\n🎉 推理测试完成!")
        print(f"📊 平均置信度: {report['average_confidence']:.3f}")
        print(f"⭐ 平均质量评分: {report['average_quality']:.3f}")
        print(f"📁 详细报告: inference_test_report_{int(time.time())}.json")
    except Exception as e:
        logger.error(f"推理测试失败: {e}")
        raise