#!/usr/bin/env python3
"""
AI专家增强器
将收集的训练数据集成到现有AI顾问系统中，提升专家回答质量
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from loguru import logger
import re
from datetime import datetime

class AIExpertEnhancer:
    def __init__(self, training_db_path: str = "test_training_data.db"):
        self.training_db_path = training_db_path
        self.expert_knowledge_base = {}
        self.load_training_data()
    
    def load_training_data(self):
        """从训练数据库加载知识库"""
        try:
            conn = sqlite3.connect(self.training_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, instruction, input_text, output_text, 
                       business_relevance, quality_score
                FROM training_data 
                WHERE quality_score >= 0.8
                ORDER BY quality_score DESC, business_relevance DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            # 按类别组织知识库
            for row in results:
                category = row[0]
                if category not in self.expert_knowledge_base:
                    self.expert_knowledge_base[category] = []
                
                self.expert_knowledge_base[category].append({
                    "instruction": row[1],
                    "input": row[2],
                    "output": row[3],
                    "business_relevance": row[4],
                    "quality_score": row[5]
                })
            
            logger.info(f"成功加载 {len(results)} 条高质量训练数据")
            logger.info(f"知识库类别: {list(self.expert_knowledge_base.keys())}")
            
        except Exception as e:
            logger.error(f"加载训练数据失败: {e}")
    
    def find_relevant_examples(self, user_query: str, expert_type: str, top_k: int = 3) -> List[Dict]:
        """根据用户查询找到相关的示例"""
        relevant_examples = []
        
        # 映射专家类型到知识库类别
        expert_category_mapping = {
            "business_strategist": ["business_strategy", "product_strategy"],
            "technical_advisor": ["technical_support"],
            "market_researcher": ["product_consultation", "customer_support"],
            "product_manager": ["product_strategy", "product_consultation"],
            "customer_support": ["customer_support", "technical_support"]
        }
        
        categories = expert_category_mapping.get(expert_type, [])
        
        for category in categories:
            if category in self.expert_knowledge_base:
                for example in self.expert_knowledge_base[category]:
                    # 简单的相关性计算（基于关键词匹配）
                    relevance_score = self.calculate_relevance(user_query, example["input"])
                    if relevance_score > 0.1:  # 相关性阈值
                        relevant_examples.append({
                            **example,
                            "relevance_score": relevance_score,
                            "category": category
                        })
        
        # 按相关性和质量分数排序
        relevant_examples.sort(
            key=lambda x: (x["relevance_score"] * 0.6 + x["quality_score"] * 0.4), 
            reverse=True
        )
        
        return relevant_examples[:top_k]
    
    def calculate_relevance(self, query: str, example_input: str) -> float:
        """计算查询与示例的相关性"""
        query_lower = query.lower()
        example_lower = example_input.lower()
        
        # 关键词映射表
        keyword_mappings = {
            "市场": ["市场", "营销", "推广", "客户", "用户", "竞争"],
            "策略": ["策略", "计划", "方案", "规划", "战略"],
            "产品": ["产品", "功能", "特性", "服务", "应用"],
            "技术": ["技术", "系统", "bug", "问题", "故障", "登录"],
            "客户": ["客户", "用户", "支持", "服务", "咨询"],
            "退货": ["退货", "退款", "政策", "流程"],
            "体验": ["体验", "界面", "使用", "操作", "满意"]
        }
        
        # 基础词汇匹配 - 简单分词
        import jieba
        try:
            query_words = set(jieba.lcut(query_lower))
            example_words = set(jieba.lcut(example_lower))
        except:
            # 如果jieba不可用，使用简单的字符分割
            query_words = set(char for char in query_lower if char.isalnum())
            example_words = set(char for char in example_lower if char.isalnum())
        
        if not query_words or not example_words:
            return 0.0
        
        # 直接匹配分数
        direct_intersection = query_words.intersection(example_words)
        direct_score = len(direct_intersection) / len(query_words.union(example_words)) if query_words.union(example_words) else 0.0
        
        # 语义匹配分数
        semantic_score = 0.0
        for query_word in query_words:
            for keyword, related_words in keyword_mappings.items():
                if query_word in related_words:
                    for example_word in example_words:
                        if example_word in related_words:
                            semantic_score += 0.1
        
        # 主题匹配分数
        topic_score = 0.0
        if any(word in query_lower for word in ["市场", "策略", "进入"]) and any(word in example_lower for word in ["市场", "策略", "进入"]):
            topic_score += 0.3
        if any(word in query_lower for word in ["产品", "功能", "体验"]) and any(word in example_lower for word in ["产品", "功能", "体验"]):
            topic_score += 0.3
        if any(word in query_lower for word in ["技术", "bug", "问题"]) and any(word in example_lower for word in ["技术", "系统", "登录"]):
            topic_score += 0.3
        if any(word in query_lower for word in ["客户", "支持", "服务"]) and any(word in example_lower for word in ["客户", "支持", "服务"]):
            topic_score += 0.3
        
        # 综合分数
        final_score = direct_score * 0.4 + semantic_score * 0.3 + topic_score * 0.3
        return min(final_score, 1.0)
    
    def enhance_expert_prompt(self, base_prompt: str, user_query: str, expert_type: str) -> str:
        """增强专家提示词"""
        relevant_examples = self.find_relevant_examples(user_query, expert_type)
        
        if not relevant_examples:
            return base_prompt
        
        # 构建增强的提示词
        enhanced_prompt = base_prompt + "\n\n"
        enhanced_prompt += "以下是一些相关的高质量回答示例，请参考这些示例的风格和深度来回答用户问题：\n\n"
        
        for i, example in enumerate(relevant_examples, 1):
            enhanced_prompt += f"示例 {i}:\n"
            enhanced_prompt += f"问题: {example['input']}\n"
            enhanced_prompt += f"回答: {example['output']}\n"
            enhanced_prompt += f"(质量分数: {example['quality_score']:.2f}, 相关性: {example['relevance_score']:.2f})\n\n"
        
        enhanced_prompt += "请基于以上示例的专业水准和回答风格，为用户提供高质量的建议。\n"
        enhanced_prompt += "确保回答具有实用性、专业性和可操作性。\n\n"
        enhanced_prompt += f"用户问题: {user_query}\n"
        
        return enhanced_prompt
    
    def get_expert_enhancement_stats(self) -> Dict[str, Any]:
        """获取专家增强统计信息"""
        stats = {
            "total_examples": sum(len(examples) for examples in self.expert_knowledge_base.values()),
            "categories": list(self.expert_knowledge_base.keys()),
            "category_counts": {
                category: len(examples) 
                for category, examples in self.expert_knowledge_base.items()
            },
            "avg_quality_scores": {
                category: sum(ex["quality_score"] for ex in examples) / len(examples)
                for category, examples in self.expert_knowledge_base.items()
            }
        }
        return stats
    
    def generate_enhanced_expert_config(self) -> Dict[str, Any]:
        """生成增强的专家配置"""
        config = {
            "enhanced_experts": {
                "business_strategist": {
                    "description": "商业策略专家 - 基于真实案例训练",
                    "available_examples": len(self.expert_knowledge_base.get("business_strategy", [])),
                    "enhancement_active": True
                },
                "technical_advisor": {
                    "description": "技术顾问 - 基于技术支持数据训练", 
                    "available_examples": len(self.expert_knowledge_base.get("technical_support", [])),
                    "enhancement_active": True
                },
                "market_researcher": {
                    "description": "市场研究员 - 基于客户咨询数据训练",
                    "available_examples": len(self.expert_knowledge_base.get("customer_support", [])),
                    "enhancement_active": True
                },
                "product_manager": {
                    "description": "产品经理 - 基于产品策略数据训练",
                    "available_examples": len(self.expert_knowledge_base.get("product_strategy", [])),
                    "enhancement_active": True
                }
            },
            "enhancement_config": {
                "min_quality_threshold": 0.8,
                "max_examples_per_query": 3,
                "relevance_threshold": 0.3,
                "last_updated": datetime.now().isoformat()
            }
        }
        return config

def test_expert_enhancement():
    """测试专家增强功能"""
    logger.info("开始测试AI专家增强功能...")
    
    enhancer = AIExpertEnhancer()
    
    # 测试查询
    test_queries = [
        {
            "query": "我们公司想要进入新市场，应该如何制定策略？",
            "expert_type": "business_strategist"
        },
        {
            "query": "客户反馈产品有bug，我们应该如何处理？",
            "expert_type": "technical_advisor"
        },
        {
            "query": "如何提升产品的用户体验？",
            "expert_type": "product_manager"
        }
    ]
    
    print("\n" + "="*60)
    print("AI专家增强测试结果")
    print("="*60)
    
    # 显示统计信息
    stats = enhancer.get_expert_enhancement_stats()
    print(f"总示例数: {stats['total_examples']}")
    print(f"知识库类别: {', '.join(stats['categories'])}")
    
    print("\n各类别示例数量:")
    for category, count in stats['category_counts'].items():
        avg_quality = stats['avg_quality_scores'][category]
        print(f"  {category}: {count} 条 (平均质量: {avg_quality:.3f})")
    
    # 测试查询增强
    print("\n查询增强测试:")
    for i, test in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {test['expert_type']}")
        print(f"查询: {test['query']}")
        
        relevant_examples = enhancer.find_relevant_examples(
            test['query'], test['expert_type'], top_k=2
        )
        
        print(f"找到 {len(relevant_examples)} 个相关示例:")
        for j, example in enumerate(relevant_examples, 1):
            print(f"  示例 {j}: {example['category']} "
                  f"(相关性: {example['relevance_score']:.3f}, "
                  f"质量: {example['quality_score']:.3f})")
    
    # 生成增强配置
    config = enhancer.generate_enhanced_expert_config()
    print(f"\n增强配置生成完成:")
    print(f"支持的专家类型: {len(config['enhanced_experts'])}")
    
    print("\n" + "="*60)
    print("AI专家增强测试完成！")
    print("="*60)
    
    return enhancer, config

def main():
    """主函数"""
    enhancer, config = test_expert_enhancement()
    
    # 保存增强配置
    with open("ai_expert_enhancement_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    logger.info("AI专家增强配置已保存到 ai_expert_enhancement_config.json")
    
    # 示例：增强一个专家提示词
    base_prompt = "你是一个专业的商业策略顾问，请为用户提供专业的商业建议。"
    user_query = "我们是一家初创公司，如何制定市场进入策略？"
    
    enhanced_prompt = enhancer.enhance_expert_prompt(base_prompt, user_query, "business_strategist")
    
    print(f"\n增强后的提示词示例:")
    print("-" * 40)
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)

if __name__ == "__main__":
    main()