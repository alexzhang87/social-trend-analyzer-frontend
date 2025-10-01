#!/usr/bin/env python3
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
        question = input("\n❓ 请输入您的问题: ")
        
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
