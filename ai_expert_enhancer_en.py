#!/usr/bin/env python3
"""
AI Expert Enhancer (English Version)
Integrates collected training data into existing AI advisor system to improve expert response quality
Optimized for English-speaking overseas users
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from loguru import logger
import re
from datetime import datetime

class AIExpertEnhancer:
    def __init__(self, training_db_path: str = "test_training_data_en.db"):
        self.training_db_path = training_db_path
        self.expert_knowledge_base = {}
        self.load_training_data()
    
    def load_training_data(self):
        """Load knowledge base from training database"""
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
            
            # Organize knowledge base by category
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
            
            logger.info(f"Successfully loaded {len(results)} high-quality training examples")
            logger.info(f"Knowledge base categories: {list(self.expert_knowledge_base.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
    
    def find_relevant_examples(self, user_query: str, expert_type: str, top_k: int = 3) -> List[Dict]:
        """Find relevant examples based on user query"""
        relevant_examples = []
        
        # Map expert types to knowledge base categories
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
                    # Simple relevance calculation (based on keyword matching)
                    relevance_score = self.calculate_relevance(user_query, example["input"])
                    if relevance_score > 0.1:  # Relevance threshold
                        relevant_examples.append({
                            **example,
                            "relevance_score": relevance_score,
                            "category": category
                        })
        
        # Sort by relevance and quality score
        relevant_examples.sort(
            key=lambda x: (x["relevance_score"] * 0.6 + x["quality_score"] * 0.4), 
            reverse=True
        )
        
        return relevant_examples[:top_k]
    
    def calculate_relevance(self, query: str, example_input: str) -> float:
        """Calculate relevance between query and example"""
        query_lower = query.lower()
        example_lower = example_input.lower()
        
        # English keyword mappings for business contexts
        keyword_mappings = {
            "market": ["market", "marketing", "promotion", "customer", "user", "competition", "competitive", "audience", "segment"],
            "strategy": ["strategy", "plan", "planning", "approach", "roadmap", "framework", "methodology"],
            "product": ["product", "feature", "functionality", "service", "application", "solution", "offering"],
            "technical": ["technical", "system", "bug", "issue", "problem", "error", "login", "integration", "api"],
            "customer": ["customer", "user", "support", "service", "consultation", "client", "experience"],
            "business": ["business", "revenue", "profit", "growth", "scale", "expansion", "operations"],
            "analytics": ["analytics", "data", "metrics", "insights", "analysis", "reporting", "dashboard"],
            "startup": ["startup", "entrepreneur", "venture", "funding", "investment", "mvp", "validation"],
            "saas": ["saas", "software", "platform", "subscription", "cloud", "enterprise", "b2b"],
            "ux": ["ux", "ui", "design", "interface", "usability", "experience", "user-friendly"]
        }
        
        # Basic word matching - simple tokenization
        import re
        try:
            # Use regex to extract words (alphanumeric sequences)
            query_words = set(re.findall(r'\b[a-zA-Z]+\b', query_lower))
            example_words = set(re.findall(r'\b[a-zA-Z]+\b', example_lower))
        except:
            # Fallback to character-based matching
            query_words = set(char for char in query_lower if char.isalnum())
            example_words = set(char for char in example_lower if char.isalnum())
        
        if not query_words or not example_words:
            return 0.0
        
        # Direct matching score
        direct_intersection = query_words.intersection(example_words)
        direct_score = len(direct_intersection) / len(query_words.union(example_words)) if query_words.union(example_words) else 0.0
        
        # Semantic matching score
        semantic_score = 0.0
        for query_word in query_words:
            for keyword, related_words in keyword_mappings.items():
                if query_word in related_words:
                    for example_word in example_words:
                        if example_word in related_words:
                            semantic_score += 0.1
        
        # Topic matching score for business contexts
        topic_score = 0.0
        business_topics = [
            (["market", "strategy", "enter", "expansion", "growth"], ["market", "strategy", "enter", "expansion", "growth"]),
            (["product", "feature", "experience", "ux", "design"], ["product", "feature", "experience", "ux", "design"]),
            (["technical", "bug", "issue", "system", "api"], ["technical", "system", "login", "integration", "api"]),
            (["customer", "support", "service", "client"], ["customer", "support", "service", "client"]),
            (["startup", "saas", "business", "revenue"], ["startup", "saas", "business", "revenue"]),
            (["analytics", "data", "metrics", "insights"], ["analytics", "data", "metrics", "insights"])
        ]
        
        for query_keywords, example_keywords in business_topics:
            if any(word in query_lower for word in query_keywords) and any(word in example_lower for word in example_keywords):
                topic_score += 0.3
        
        # Combined score
        final_score = direct_score * 0.4 + semantic_score * 0.3 + topic_score * 0.3
        return min(final_score, 1.0)
    
    def enhance_expert_prompt(self, base_prompt: str, user_query: str, expert_type: str) -> str:
        """Enhance expert prompt with relevant examples"""
        relevant_examples = self.find_relevant_examples(user_query, expert_type)
        
        if not relevant_examples:
            return base_prompt
        
        # Build enhanced prompt
        enhanced_prompt = base_prompt + "\n\n"
        enhanced_prompt += "Here are some relevant high-quality response examples. Please reference the style and depth of these examples when answering the user's question:\n\n"
        
        for i, example in enumerate(relevant_examples, 1):
            enhanced_prompt += f"Example {i}:\n"
            enhanced_prompt += f"Question: {example['input']}\n"
            enhanced_prompt += f"Answer: {example['output']}\n"
            enhanced_prompt += f"(Quality Score: {example['quality_score']:.2f}, Relevance: {example['relevance_score']:.2f})\n\n"
        
        enhanced_prompt += "Please provide high-quality advice based on the professional standards and response style of the above examples.\n"
        enhanced_prompt += "Ensure your response is practical, professional, and actionable.\n\n"
        enhanced_prompt += f"User Question: {user_query}\n"
        
        return enhanced_prompt
    
    def get_expert_enhancement_stats(self) -> Dict[str, Any]:
        """Get expert enhancement statistics"""
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
        """Generate enhanced expert configuration"""
        config = {
            "enhanced_experts": {
                "business_strategist": {
                    "description": "Business Strategy Expert - Trained on real business cases and market analysis",
                    "available_examples": len(self.expert_knowledge_base.get("business_strategy", [])),
                    "enhancement_active": True,
                    "specialties": ["Market Entry", "Growth Strategy", "Competitive Analysis", "Business Planning"]
                },
                "technical_advisor": {
                    "description": "Technical Advisor - Trained on technical support and system integration data", 
                    "available_examples": len(self.expert_knowledge_base.get("technical_support", [])),
                    "enhancement_active": True,
                    "specialties": ["System Integration", "API Development", "Technical Troubleshooting", "Software Architecture"]
                },
                "market_researcher": {
                    "description": "Market Research Analyst - Trained on customer consultation and market data",
                    "available_examples": len(self.expert_knowledge_base.get("customer_support", [])),
                    "enhancement_active": True,
                    "specialties": ["Market Analysis", "Customer Insights", "Trend Analysis", "Competitive Intelligence"]
                },
                "product_manager": {
                    "description": "Product Manager - Trained on product strategy and user experience data",
                    "available_examples": len(self.expert_knowledge_base.get("product_strategy", [])),
                    "enhancement_active": True,
                    "specialties": ["Product Strategy", "User Experience", "Feature Planning", "Product Roadmap"]
                }
            },
            "enhancement_config": {
                "min_quality_threshold": 0.8,
                "max_examples_per_query": 3,
                "relevance_threshold": 0.3,
                "language": "english",
                "target_market": "international",
                "last_updated": datetime.now().isoformat()
            }
        }
        return config

def test_expert_enhancement():
    """Test expert enhancement functionality"""
    logger.info("Starting AI Expert Enhancement testing...")
    
    enhancer = AIExpertEnhancer()
    
    # Test queries in English for business scenarios
    test_queries = [
        {
            "query": "How should we develop a market entry strategy for our SaaS startup in the European market?",
            "expert_type": "business_strategist"
        },
        {
            "query": "Our customers are reporting API integration issues. How should we handle this technical problem?",
            "expert_type": "technical_advisor"
        },
        {
            "query": "How can we improve our product's user experience and increase customer satisfaction?",
            "expert_type": "product_manager"
        },
        {
            "query": "What market research methods should we use to validate our new product idea?",
            "expert_type": "market_researcher"
        }
    ]
    
    print("\n" + "="*60)
    print("AI Expert Enhancement Test Results")
    print("="*60)
    
    # Display statistics
    stats = enhancer.get_expert_enhancement_stats()
    print(f"Total Examples: {stats['total_examples']}")
    print(f"Knowledge Base Categories: {', '.join(stats['categories'])}")
    
    print("\nCategory Example Counts:")
    for category, count in stats['category_counts'].items():
        avg_quality = stats['avg_quality_scores'][category]
        print(f"  {category}: {count} examples (avg quality: {avg_quality:.3f})")
    
    # Test query enhancement
    print("\nQuery Enhancement Tests:")
    for i, test in enumerate(test_queries, 1):
        print(f"\nTest {i}: {test['expert_type']}")
        print(f"Query: {test['query']}")
        
        relevant_examples = enhancer.find_relevant_examples(
            test['query'], test['expert_type'], top_k=2
        )
        
        print(f"Found {len(relevant_examples)} relevant examples:")
        for j, example in enumerate(relevant_examples, 1):
            print(f"  Example {j}: {example['category']} "
                  f"(relevance: {example['relevance_score']:.3f}, "
                  f"quality: {example['quality_score']:.3f})")
    
    # Generate enhanced configuration
    config = enhancer.generate_enhanced_expert_config()
    print(f"\nEnhanced Configuration Generated:")
    print(f"Supported Expert Types: {len(config['enhanced_experts'])}")
    
    print("\n" + "="*60)
    print("AI Expert Enhancement Testing Complete!")
    print("="*60)
    
    return enhancer, config

def main():
    """Main function"""
    enhancer, config = test_expert_enhancement()
    
    # Save enhanced configuration
    with open("ai_expert_enhancement_config_en.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    logger.info("AI Expert Enhancement configuration saved to ai_expert_enhancement_config_en.json")
    
    # Example: Enhance an expert prompt
    base_prompt = "You are a professional business strategy consultant. Please provide expert business advice to users."
    user_query = "We are a startup company. How should we develop a market entry strategy?"
    
    enhanced_prompt = enhancer.enhance_expert_prompt(base_prompt, user_query, "business_strategist")
    
    print(f"\nEnhanced Prompt Example:")
    print("-" * 40)
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)

if __name__ == "__main__":
    main()