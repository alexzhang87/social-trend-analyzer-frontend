"""
免费训练数据源集成服务
用于集成Hugging Face、Stack Overflow、SCORE等免费数据源
"""

import asyncio
import aiohttp
import json
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from datasets import load_dataset
import sqlite3
import xml.etree.ElementTree as ET
from transformers import AutoTokenizer
import torch

logger = logging.getLogger(__name__)

class FreeDataIntegrationService:
    """免费数据源集成服务"""
    
    def __init__(self):
        self.data_dir = Path("./data/training")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据源配置
        self.huggingface_datasets = {
            "customer_support": {
                "dataset_name": "microsoft/DialoGPT-medium",
                "subset": None,
                "quality_threshold": 0.8
            },
            "chatbot_arena": {
                "dataset_name": "lmsys/chatbot_arena_conversations", 
                "subset": None,
                "quality_threshold": 0.9
            },
            "banking_conversations": {
                "dataset_name": "banking77",
                "subset": None,
                "quality_threshold": 0.85
            }
        }
        
        # 质量控制参数
        self.min_length = 50
        self.max_length = 2048
        self.quality_threshold = 0.8
        
        # 初始化tokenizer用于长度检查
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    async def integrate_all_sources(self) -> Dict[str, Any]:
        """集成所有免费数据源"""
        logger.info("开始集成免费训练数据源...")
        
        all_training_data = []
        source_stats = {}
        
        try:
            # 1. 集成Hugging Face数据
            hf_data = await self.integrate_huggingface_data()
            all_training_data.extend(hf_data["data"])
            source_stats["huggingface"] = hf_data["stats"]
            
            # 2. 集成Stack Overflow数据
            so_data = await self.integrate_stackoverflow_data()
            all_training_data.extend(so_data["data"])
            source_stats["stackoverflow"] = so_data["stats"]
            
            # 3. 集成SCORE数据
            score_data = await self.integrate_score_data()
            all_training_data.extend(score_data["data"])
            source_stats["score"] = score_data["stats"]
            
            # 4. 统一质量控制和去重
            cleaned_data = self.apply_quality_control(all_training_data)
            deduplicated_data = self.remove_duplicates(cleaned_data)
            
            # 5. 保存处理后的数据
            output_file = self.data_dir / "integrated_training_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(deduplicated_data, f, ensure_ascii=False, indent=2)
            
            # 6. 生成统计报告
            final_stats = {
                "total_samples": len(deduplicated_data),
                "source_breakdown": source_stats,
                "quality_distribution": self.analyze_quality_distribution(deduplicated_data),
                "output_file": str(output_file),
                "processing_time": datetime.utcnow().isoformat()
            }
            
            logger.info(f"数据集成完成，共处理 {final_stats['total_samples']} 条训练样本")
            return final_stats
            
        except Exception as e:
            logger.error(f"数据集成失败: {str(e)}")
            raise

    async def integrate_huggingface_data(self) -> Dict[str, Any]:
        """集成Hugging Face数据集"""
        logger.info("开始集成Hugging Face数据集...")
        
        all_data = []
        stats = {}
        
        for dataset_key, config in self.huggingface_datasets.items():
            try:
                logger.info(f"加载数据集: {config['dataset_name']}")
                
                # 加载数据集
                dataset = load_dataset(
                    config["dataset_name"],
                    config.get("subset"),
                    split="train[:10000]"  # 限制样本数量用于测试
                )
                
                # 处理数据
                processed_data = self.process_huggingface_dataset(dataset, dataset_key)
                
                # 过滤质量
                filtered_data = [
                    item for item in processed_data 
                    if item.get("quality_score", 0) >= config["quality_threshold"]
                ]
                
                all_data.extend(filtered_data)
                stats[dataset_key] = {
                    "raw_samples": len(dataset),
                    "processed_samples": len(processed_data),
                    "filtered_samples": len(filtered_data),
                    "quality_threshold": config["quality_threshold"]
                }
                
                logger.info(f"数据集 {dataset_key} 处理完成: {len(filtered_data)} 条样本")
                
            except Exception as e:
                logger.error(f"处理数据集 {dataset_key} 失败: {str(e)}")
                stats[dataset_key] = {"error": str(e)}
        
        return {"data": all_data, "stats": stats}

    def process_huggingface_dataset(self, dataset, dataset_key: str) -> List[Dict]:
        """处理Hugging Face数据集"""
        processed_data = []
        
        for item in dataset:
            try:
                # 根据数据集类型提取对话
                if dataset_key == "customer_support":
                    qa_pairs = self.extract_customer_support_pairs(item)
                elif dataset_key == "chatbot_arena":
                    qa_pairs = self.extract_arena_pairs(item)
                elif dataset_key == "banking_conversations":
                    qa_pairs = self.extract_banking_pairs(item)
                else:
                    qa_pairs = self.extract_generic_pairs(item)
                
                # 转换为创业咨询格式
                for pair in qa_pairs:
                    adapted_pair = self.adapt_to_startup_consulting(pair, dataset_key)
                    if adapted_pair:
                        processed_data.append(adapted_pair)
                        
            except Exception as e:
                logger.warning(f"处理样本失败: {str(e)}")
                continue
        
        return processed_data

    def extract_customer_support_pairs(self, item: Dict) -> List[Dict]:
        """提取客户支持对话对"""
        pairs = []
        
        if "conversation" in item:
            conversation = item["conversation"]
            for i in range(0, len(conversation)-1, 2):
                if i+1 < len(conversation):
                    question = conversation[i].get("text", "")
                    answer = conversation[i+1].get("text", "")
                    
                    if len(question) > 20 and len(answer) > 20:
                        pairs.append({
                            "input": question,
                            "output": answer,
                            "source": "customer_support"
                        })
        
        return pairs

    def extract_arena_pairs(self, item: Dict) -> List[Dict]:
        """提取聊天机器人竞技场对话对"""
        pairs = []
        
        if "conversation" in item:
            messages = item["conversation"]
            for i in range(0, len(messages)-1, 2):
                if i+1 < len(messages):
                    user_msg = messages[i].get("content", "")
                    assistant_msg = messages[i+1].get("content", "")
                    
                    if len(user_msg) > 20 and len(assistant_msg) > 20:
                        pairs.append({
                            "input": user_msg,
                            "output": assistant_msg,
                            "source": "chatbot_arena",
                            "quality_score": item.get("rating", 0.8)
                        })
        
        return pairs

    def extract_banking_pairs(self, item: Dict) -> List[Dict]:
        """提取银行业对话对"""
        pairs = []
        
        if "text" in item and "label" in item:
            # 将分类任务转换为问答任务
            question = f"What type of banking inquiry is this: {item['text']}"
            answer = f"This is a {item['label']} inquiry."
            
            pairs.append({
                "input": question,
                "output": answer,
                "source": "banking_conversations"
            })
        
        return pairs

    def extract_generic_pairs(self, item: Dict) -> List[Dict]:
        """提取通用对话对"""
        pairs = []
        
        # 尝试多种可能的字段名
        possible_fields = [
            ("question", "answer"),
            ("input", "output"),
            ("prompt", "response"),
            ("text", "label")
        ]
        
        for input_field, output_field in possible_fields:
            if input_field in item and output_field in item:
                pairs.append({
                    "input": str(item[input_field]),
                    "output": str(item[output_field]),
                    "source": "generic"
                })
                break
        
        return pairs

    def adapt_to_startup_consulting(self, pair: Dict, dataset_key: str) -> Optional[Dict]:
        """将对话对适配为创业咨询格式"""
        try:
            input_text = pair["input"]
            output_text = pair["output"]
            
            # 长度检查
            if len(input_text) < self.min_length or len(output_text) < self.min_length:
                return None
            
            if len(input_text) > self.max_length or len(output_text) > self.max_length:
                return None
            
            # 根据数据源类型进行适配
            if dataset_key == "customer_support":
                adapted_input = self.adapt_customer_support_to_startup(input_text)
                adapted_output = self.adapt_support_response_to_consulting(output_text)
            elif dataset_key == "banking_conversations":
                adapted_input = self.adapt_banking_to_startup_finance(input_text)
                adapted_output = self.adapt_banking_response_to_startup_advice(output_text)
            else:
                adapted_input = self.add_startup_context(input_text)
                adapted_output = self.add_consulting_tone(output_text)
            
            # 计算质量分数
            quality_score = self.calculate_quality_score(adapted_input, adapted_output)
            
            return {
                "instruction": adapted_input,
                "input": "",
                "output": adapted_output,
                "source": f"hf_{dataset_key}",
                "domain": "startup_consulting",
                "quality_score": quality_score,
                "original_source": pair.get("source", "unknown"),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"适配失败: {str(e)}")
            return None

    def adapt_customer_support_to_startup(self, text: str) -> str:
        """将客户支持问题适配为创业咨询问题"""
        # 关键词替换映射
        replacements = {
            "customer": "user",
            "product issue": "product-market fit challenge",
            "billing": "funding",
            "account": "startup",
            "service": "product",
            "complaint": "feedback",
            "refund": "pivot strategy"
        }
        
        adapted_text = text.lower()
        for old, new in replacements.items():
            adapted_text = adapted_text.replace(old, new)
        
        # 添加创业背景
        if not adapted_text.startswith("as a startup founder"):
            adapted_text = f"As a startup founder, {adapted_text}"
        
        return adapted_text.capitalize()

    def adapt_support_response_to_consulting(self, text: str) -> str:
        """将支持回复适配为咨询建议"""
        # 调整语调为咨询式
        consulting_phrases = [
            "I recommend",
            "Consider",
            "A strategic approach would be",
            "From a business perspective",
            "To optimize your startup"
        ]
        
        adapted_text = text
        
        # 如果没有咨询语调，添加一个
        has_consulting_tone = any(phrase.lower() in adapted_text.lower() for phrase in consulting_phrases)
        if not has_consulting_tone:
            adapted_text = f"I recommend {adapted_text.lower()}"
        
        return adapted_text

    def adapt_banking_to_startup_finance(self, text: str) -> str:
        """将银行业务问题适配为创业财务问题"""
        finance_mappings = {
            "loan": "funding round",
            "credit": "investor confidence",
            "interest rate": "equity dilution",
            "mortgage": "office lease",
            "savings": "runway",
            "investment": "funding strategy"
        }
        
        adapted_text = text.lower()
        for old, new in finance_mappings.items():
            adapted_text = adapted_text.replace(old, new)
        
        return f"Regarding startup finances: {adapted_text}"

    async def integrate_stackoverflow_data(self) -> Dict[str, Any]:
        """集成Stack Overflow数据"""
        logger.info("开始集成Stack Overflow数据...")
        
        # 由于完整的SO数据集很大，这里使用模拟数据
        # 在实际实施中，需要下载和解析XML转储文件
        
        mock_so_data = [
            {
                "instruction": "As a startup founder, how should I design my API architecture for scalability?",
                "input": "",
                "output": "For startup API architecture, I recommend starting with a microservices approach using REST APIs. Focus on horizontal scaling, implement proper caching strategies, and use load balancers. Consider using cloud services like AWS API Gateway for easier management.",
                "source": "stackoverflow_adapted",
                "domain": "startup_tech_consulting",
                "quality_score": 0.9,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "instruction": "What database should I choose for my SaaS startup?",
                "input": "",
                "output": "For SaaS startups, I recommend PostgreSQL for its reliability and ACID compliance. If you need high scalability, consider MongoDB for document storage or Redis for caching. The choice depends on your data structure and scaling requirements.",
                "source": "stackoverflow_adapted", 
                "domain": "startup_tech_consulting",
                "quality_score": 0.85,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        stats = {
            "processed_samples": len(mock_so_data),
            "note": "Using mock data - implement full SO integration in production"
        }
        
        return {"data": mock_so_data, "stats": stats}

    async def integrate_score_data(self) -> Dict[str, Any]:
        """集成SCORE平台数据"""
        logger.info("开始集成SCORE平台数据...")
        
        # 模拟SCORE数据 - 实际实施中需要与SCORE平台合作
        mock_score_data = [
            {
                "instruction": "How do I validate my business idea before launching?",
                "input": "",
                "output": "To validate your business idea, start with customer interviews to understand pain points. Create a minimum viable product (MVP) to test core assumptions. Use surveys and focus groups to gather feedback. Analyze competitor responses and market size. Track key metrics like customer acquisition cost and lifetime value.",
                "source": "score_adapted",
                "domain": "business_consulting",
                "quality_score": 0.95,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "instruction": "What are the key financial metrics I should track as a startup?",
                "input": "",
                "output": "Essential startup financial metrics include: Monthly Recurring Revenue (MRR), Customer Acquisition Cost (CAC), Customer Lifetime Value (CLV), burn rate, runway, gross margin, and churn rate. For SaaS businesses, also track Annual Recurring Revenue (ARR) and Net Revenue Retention.",
                "source": "score_adapted",
                "domain": "business_consulting", 
                "quality_score": 0.92,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        stats = {
            "processed_samples": len(mock_score_data),
            "note": "Using mock data - implement SCORE partnership in production"
        }
        
        return {"data": mock_score_data, "stats": stats}

    def apply_quality_control(self, data: List[Dict]) -> List[Dict]:
        """应用质量控制"""
        cleaned_data = []
        
        for item in data:
            try:
                # 检查必需字段
                if not all(key in item for key in ["instruction", "output"]):
                    continue
                
                # 长度检查
                instruction_len = len(item["instruction"])
                output_len = len(item["output"])
                
                if not (self.min_length <= instruction_len <= self.max_length):
                    continue
                if not (self.min_length <= output_len <= self.max_length):
                    continue
                
                # 质量分数检查
                if item.get("quality_score", 0) < self.quality_threshold:
                    continue
                
                # 内容安全检查
                if not self.is_safe_content(item):
                    continue
                
                cleaned_data.append(item)
                
            except Exception as e:
                logger.warning(f"质量控制检查失败: {str(e)}")
                continue
        
        logger.info(f"质量控制完成: {len(cleaned_data)}/{len(data)} 条样本通过")
        return cleaned_data

    def remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """去除重复数据"""
        seen_instructions = set()
        deduplicated_data = []
        
        for item in data:
            instruction_hash = hash(item["instruction"].lower().strip())
            if instruction_hash not in seen_instructions:
                seen_instructions.add(instruction_hash)
                deduplicated_data.append(item)
        
        logger.info(f"去重完成: {len(deduplicated_data)}/{len(data)} 条样本保留")
        return deduplicated_data

    def calculate_quality_score(self, instruction: str, output: str) -> float:
        """计算质量分数"""
        score = 0.0
        
        # 长度合理性 (0-0.3)
        inst_len = len(instruction)
        out_len = len(output)
        
        if 50 <= inst_len <= 500:
            score += 0.15
        if 100 <= out_len <= 1000:
            score += 0.15
        
        # 内容复杂度 (0-0.3)
        if len(instruction.split()) >= 10:
            score += 0.15
        if len(output.split()) >= 20:
            score += 0.15
        
        # 专业性检查 (0-0.4)
        business_keywords = [
            "startup", "business", "market", "customer", "revenue",
            "strategy", "growth", "funding", "product", "analysis"
        ]
        
        combined_text = (instruction + " " + output).lower()
        keyword_count = sum(1 for keyword in business_keywords if keyword in combined_text)
        score += min(0.4, keyword_count * 0.1)
        
        return min(1.0, score)

    def is_safe_content(self, item: Dict) -> bool:
        """检查内容安全性"""
        unsafe_patterns = [
            r'\b(hate|violence|illegal|harmful)\b',
            r'\b(personal information|private data)\b',
            r'\b(password|credit card|ssn)\b'
        ]
        
        combined_text = (item["instruction"] + " " + item["output"]).lower()
        
        for pattern in unsafe_patterns:
            if re.search(pattern, combined_text):
                return False
        
        return True

    def add_startup_context(self, text: str) -> str:
        """添加创业背景上下文"""
        if not text.lower().startswith(("as a startup", "for my startup", "regarding my business")):
            return f"As a startup founder, {text.lower()}"
        return text

    def add_consulting_tone(self, text: str) -> str:
        """添加咨询语调"""
        consulting_starters = [
            "I recommend", "Consider", "My advice would be",
            "From a strategic perspective", "To optimize your business"
        ]
        
        text_lower = text.lower()
        has_consulting_tone = any(starter.lower() in text_lower for starter in consulting_starters)
        
        if not has_consulting_tone:
            return f"I recommend {text.lower()}"
        
        return text

    def analyze_quality_distribution(self, data: List[Dict]) -> Dict[str, Any]:
        """分析质量分布"""
        quality_scores = [item.get("quality_score", 0) for item in data]
        
        return {
            "mean_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "min_quality": min(quality_scores) if quality_scores else 0,
            "max_quality": max(quality_scores) if quality_scores else 0,
            "high_quality_count": len([s for s in quality_scores if s >= 0.9]),
            "medium_quality_count": len([s for s in quality_scores if 0.7 <= s < 0.9]),
            "low_quality_count": len([s for s in quality_scores if s < 0.7])
        }

# 使用示例
async def main():
    """主函数示例"""
    service = FreeDataIntegrationService()
    
    try:
        # 集成所有免费数据源
        result = await service.integrate_all_sources()
        
        print("数据集成完成!")
        print(f"总样本数: {result['total_samples']}")
        print(f"输出文件: {result['output_file']}")
        print(f"质量分布: {result['quality_distribution']}")
        
    except Exception as e:
        print(f"集成失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())