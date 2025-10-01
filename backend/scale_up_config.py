#!/usr/bin/env python3
"""
大规模数据收集配置文件
定义扩展Reddit数据收集到万条级别的策略和参数
"""

# 目标数据量配置
TARGET_DATA_VOLUMES = {
    'reddit_total': 8000,      # Reddit总目标
    'reddit_per_subreddit': 200,  # 每个subreddit目标
    'reddit_per_keyword': 50,     # 每个关键词目标
    'minimum_quality_score': 0.5,  # 最低质量分
    'minimum_text_length': 100     # 最低文本长度
}

# 扩展的高价值Subreddit列表（按优先级排序）
PRIORITY_SUBREDDITS = {
    # 第一优先级：核心创业和商业
    'tier_1': [
        'startups', 'entrepreneur', 'business', 'smallbusiness',
        'venturecapital', 'investing', 'stocks', 'finance',
        'personalfinance', 'ecommerce', 'marketing', 'sales'
    ],
    
    # 第二优先级：技术和产品
    'tier_2': [
        'technology', 'programming', 'webdev', 'coding',
        'MachineLearning', 'artificial', 'datascience',
        'SaaS', 'fintech', 'edtech', 'healthtech'
    ],
    
    # 第三优先级：新兴领域
    'tier_3': [
        'blockchain', 'cryptocurrency', 'automation', 'iot',
        'cybersecurity', 'cloudcomputing', 'biotech', 'cleantech',
        'digitalnomad', 'remotework', 'freelance', 'productivity'
    ],
    
    # 第四优先级：行业特定
    'tier_4': [
        'proptech', 'foodtech', 'mobility', 'logistics',
        'supplychain', 'manufacturing', 'retail', 'analytics',
        'growth', 'innovation', 'lean', 'agile', 'scrum'
    ]
}

# 扩展的高价值关键词（按类别组织）
KEYWORD_CATEGORIES = {
    # 创业核心词汇
    'startup_core': [
        'startup', 'entrepreneur', 'business model', 'market analysis',
        'product launch', 'funding', 'investment', 'venture capital',
        'seed funding', 'series a', 'series b', 'ipo', 'acquisition'
    ],
    
    # 技术创新
    'tech_innovation': [
        'AI startup', 'tech startup', 'artificial intelligence',
        'machine learning', 'deep learning', 'automation',
        'blockchain', 'cryptocurrency', 'web3', 'metaverse'
    ],
    
    # 商业策略
    'business_strategy': [
        'digital transformation', 'innovation', 'disruption',
        'scaling', 'growth hacking', 'customer acquisition',
        'product market fit', 'user retention', 'monetization'
    ],
    
    # 市场和竞争
    'market_competition': [
        'market research', 'competitor analysis', 'market size',
        'go to market', 'pricing strategy', 'revenue model',
        'business development', 'partnership'
    ],
    
    # 运营管理
    'operations': [
        'team building', 'hiring', 'company culture',
        'remote work', 'project management', 'agile development',
        'lean startup', 'mvp', 'prototype', 'user testing'
    ]
}

# 收集策略配置
COLLECTION_STRATEGIES = {
    # 多维度收集
    'post_types': ['hot', 'new', 'top', 'rising'],
    'time_filters': ['day', 'week', 'month', 'year'],
    'sort_methods': ['relevance', 'hot', 'top', 'new', 'comments'],
    
    # 批量参数
    'batch_sizes': {
        'subreddit_posts': 50,    # 每次获取subreddit帖子数
        'search_results': 25,     # 每次搜索结果数
        'concurrent_requests': 3,  # 并发请求数
    },
    
    # 速率限制
    'rate_limits': {
        'request_delay': 0.5,     # 请求间隔（秒）
        'subreddit_delay': 2.0,   # subreddit间隔（秒）
        'keyword_delay': 1.0,     # 关键词间隔（秒）
        'error_backoff': 5.0      # 错误后退避时间（秒）
    }
}

# 数据质量配置
QUALITY_FILTERS = {
    'text_requirements': {
        'min_length': 100,        # 最小文本长度
        'max_length': 10000,      # 最大文本长度
        'min_words': 20,          # 最小单词数
    },
    
    'metadata_requirements': {
        'min_score': 5,           # 最小Reddit分数
        'min_comments': 2,        # 最小评论数
        'max_age_days': 365,      # 最大帖子年龄（天）
    },
    
    'content_filters': {
        'exclude_deleted': True,   # 排除已删除内容
        'exclude_removed': True,   # 排除已移除内容
        'exclude_nsfw': True,      # 排除NSFW内容
        'require_english': True    # 要求英文内容
    }
}

# 输出配置
OUTPUT_CONFIG = {
    'save_intervals': {
        'checkpoint_every': 500,   # 每500条保存检查点
        'backup_every': 1000,      # 每1000条备份
    },
    
    'file_formats': {
        'raw_data': True,          # 保存原始数据
        'training_data': True,     # 保存训练格式
        'statistics': True,        # 保存统计信息
        'quality_report': True     # 保存质量报告
    },
    
    'compression': {
        'enable': True,            # 启用压缩
        'format': 'gzip'           # 压缩格式
    }
}

# 监控和日志配置
MONITORING_CONFIG = {
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'file_logging': True,
        'console_logging': True
    },
    
    'progress_tracking': {
        'update_interval': 100,    # 每100条更新进度
        'eta_calculation': True,   # 计算预计完成时间
        'speed_monitoring': True   # 监控收集速度
    },
    
    'error_handling': {
        'max_retries': 3,          # 最大重试次数
        'retry_delay': 2.0,        # 重试延迟
        'continue_on_error': True  # 遇到错误继续执行
    }
}

# 预计资源需求
RESOURCE_ESTIMATES = {
    'time_estimates': {
        'total_hours': '4-8',      # 预计总时间
        'per_1000_items': '30-60min',  # 每1000条用时
    },
    
    'storage_estimates': {
        'raw_data_mb': 50,         # 原始数据大小（MB）
        'processed_data_mb': 30,   # 处理后数据大小（MB）
        'total_storage_mb': 100    # 总存储需求（MB）
    },
    
    'api_usage': {
        'reddit_requests': 2000,   # 预计Reddit API请求数
        'rate_limit_safe': True    # 是否在速率限制内
    }
}

def get_all_subreddits():
    """获取所有subreddit列表"""
    all_subreddits = []
    for tier_subreddits in PRIORITY_SUBREDDITS.values():
        all_subreddits.extend(tier_subreddits)
    return all_subreddits

def get_all_keywords():
    """获取所有关键词列表"""
    all_keywords = []
    for category_keywords in KEYWORD_CATEGORIES.values():
        all_keywords.extend(category_keywords)
    return all_keywords

def get_collection_plan():
    """获取收集计划摘要"""
    total_subreddits = len(get_all_subreddits())
    total_keywords = len(get_all_keywords())
    
    return {
        'target_data_volume': TARGET_DATA_VOLUMES['reddit_total'],
        'total_subreddits': total_subreddits,
        'total_keywords': total_keywords,
        'estimated_requests': total_subreddits * 4 + total_keywords * 2,  # 粗略估计
        'estimated_time_hours': RESOURCE_ESTIMATES['time_estimates']['total_hours'],
        'estimated_storage_mb': RESOURCE_ESTIMATES['storage_estimates']['total_storage_mb']
    }

if __name__ == "__main__":
    # 打印配置摘要
    plan = get_collection_plan()
    print("🎯 大规模Reddit数据收集计划")
    print("=" * 40)
    print(f"目标数据量: {plan['target_data_volume']:,} 条")
    print(f"Subreddit数量: {plan['total_subreddits']} 个")
    print(f"关键词数量: {plan['total_keywords']} 个")
    print(f"预计API请求: {plan['estimated_requests']:,} 次")
    print(f"预计时间: {plan['estimated_time_hours']} 小时")
    print(f"预计存储: {plan['estimated_storage_mb']} MB")
    print("=" * 40)
    
    print("\n📋 Subreddit分层:")
    for tier, subreddits in PRIORITY_SUBREDDITS.items():
        print(f"{tier}: {len(subreddits)} 个 - {', '.join(subreddits[:5])}...")
    
    print("\n🔍 关键词分类:")
    for category, keywords in KEYWORD_CATEGORIES.items():
        print(f"{category}: {len(keywords)} 个 - {', '.join(keywords[:3])}...")