#!/usr/bin/env python3
"""
调试相关性计算算法
"""

import re

def calculate_relevance_debug(query: str, example_input: str) -> float:
    """计算查询与示例的相关性（带调试信息）"""
    print(f"\n调试相关性计算:")
    print(f"查询: {query}")
    print(f"示例: {example_input}")
    
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
    
    # 基础词汇匹配 - 使用jieba分词
    import jieba
    try:
        query_words = set(jieba.lcut(query_lower))
        example_words = set(jieba.lcut(example_lower))
    except:
        # 如果jieba不可用，使用简单的字符分割
        query_words = set(char for char in query_lower if char.isalnum())
        example_words = set(char for char in example_lower if char.isalnum())
    
    print(f"查询词汇: {query_words}")
    print(f"示例词汇: {example_words}")
    
    if not query_words or not example_words:
        print("词汇为空，返回0")
        return 0.0
    
    # 直接匹配分数
    direct_intersection = query_words.intersection(example_words)
    direct_score = len(direct_intersection) / len(query_words.union(example_words)) if query_words.union(example_words) else 0.0
    print(f"直接匹配词汇: {direct_intersection}")
    print(f"直接匹配分数: {direct_score:.3f}")
    
    # 语义匹配分数
    semantic_score = 0.0
    semantic_matches = []
    for query_word in query_words:
        for keyword, related_words in keyword_mappings.items():
            if query_word in related_words:
                for example_word in example_words:
                    if example_word in related_words:
                        semantic_score += 0.1
                        semantic_matches.append(f"{query_word}-{example_word}({keyword})")
    
    print(f"语义匹配: {semantic_matches}")
    print(f"语义匹配分数: {semantic_score:.3f}")
    
    # 主题匹配分数
    topic_score = 0.0
    topic_matches = []
    
    if any(word in query_lower for word in ["市场", "策略", "进入"]) and any(word in example_lower for word in ["市场", "策略", "进入"]):
        topic_score += 0.3
        topic_matches.append("市场策略主题")
    if any(word in query_lower for word in ["产品", "功能", "体验"]) and any(word in example_lower for word in ["产品", "功能", "体验"]):
        topic_score += 0.3
        topic_matches.append("产品功能主题")
    if any(word in query_lower for word in ["技术", "bug", "问题"]) and any(word in example_lower for word in ["技术", "系统", "登录"]):
        topic_score += 0.3
        topic_matches.append("技术问题主题")
    if any(word in query_lower for word in ["客户", "支持", "服务"]) and any(word in example_lower for word in ["客户", "支持", "服务"]):
        topic_score += 0.3
        topic_matches.append("客户服务主题")
    
    print(f"主题匹配: {topic_matches}")
    print(f"主题匹配分数: {topic_score:.3f}")
    
    # 综合分数
    final_score = direct_score * 0.4 + semantic_score * 0.3 + topic_score * 0.3
    print(f"最终分数: {final_score:.3f}")
    
    return min(final_score, 1.0)

def main():
    # 测试查询
    test_cases = [
        {
            "query": "我们公司想要进入新市场，应该如何制定策略？",
            "examples": [
                "我们是一家SaaS公司，想进入东南亚市场，应该如何制定进入策略？",
                "初创公司如何制定有效的市场开拓策略？",
                "我们的产品在竞争激烈的市场中如何找到差异化定位？"
            ]
        },
        {
            "query": "客户反馈产品有bug，我们应该如何处理？",
            "examples": [
                "系统登录不了，提示密码错误，但我确定密码是对的",
                "如何提升客户服务质量和用户满意度？"
            ]
        },
        {
            "query": "如何提升产品的用户体验？",
            "examples": [
                "用户反馈产品界面复杂，如何优化用户体验？",
                "这个产品有什么主要功能？适合什么场景使用？",
                "如何规划产品功能优先级和开发路线图？"
            ]
        }
    ]
    
    print("="*60)
    print("相关性计算调试测试")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"查询: {test_case['query']}")
        
        for j, example in enumerate(test_case['examples'], 1):
            print(f"\n  示例 {j}:")
            score = calculate_relevance_debug(test_case['query'], example)
            print(f"  相关性分数: {score:.3f} {'✓' if score > 0.1 else '✗'}")

if __name__ == "__main__":
    main()