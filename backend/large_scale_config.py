"""
大规模数据收集配置文件
目标：收集10,000+条高质量训练数据
"""

# 目标数据量配置
TARGET_DATA_COUNTS = {
    'reddit': 4000,        # Reddit数据：4000条
    'hacker_news': 2000,   # Hacker News：2000条
    'arxiv': 1500,         # 学术论文：1500条
    'github': 1500,        # GitHub项目：1500条
    'news': 2000,          # 新闻文章：2000条
    'total_target': 11000  # 总目标：11000条
}

# Reddit扩展配置
REDDIT_CONFIG = {
    'subreddits': [
        # 创业和商业
        'startups', 'entrepreneur', 'business', 'smallbusiness', 'venturecapital',
        'investing', 'stocks', 'finance', 'personalfinance', 'ecommerce',
        
        # 技术和编程
        'technology', 'programming', 'webdev', 'coding', 'softwareengineering',
        'MachineLearning', 'artificial', 'datascience', 'analytics', 'automation',
        
        # 行业特定
        'fintech', 'blockchain', 'cryptocurrency', 'SaaS', 'marketing',
        'digitalnomad', 'freelance', 'productivity', 'growth', 'innovation',
        
        # 新兴技术
        'cloudcomputing', 'cybersecurity', 'iot', 'biotech', 'cleantech',
        'edtech', 'healthtech', 'proptech', 'foodtech', 'mobility',
        
        # 市场和分析
        'marketresearch', 'competitoranalysis', 'customerexperience', 'ux',
        'design', 'product', 'lean', 'agile', 'scrum'
    ],
    
    'keywords': [
        # 核心创业关键词
        'startup', 'entrepreneur', 'business model', 'market analysis',
        'product launch', 'funding', 'investment', 'venture capital',
        'seed funding', 'series a', 'ipo', 'acquisition', 'merger',
        
        # 技术创业
        'AI startup', 'tech startup', 'SaaS', 'fintech', 'edtech',
        'healthtech', 'proptech', 'cleantech', 'biotech', 'foodtech',
        'mobility startup', 'logistics tech', 'supply chain',
        
        # 商业策略
        'digital transformation', 'innovation', 'disruption', 'scaling',
        'growth hacking', 'customer acquisition', 'product market fit',
        'user retention', 'churn rate', 'lifetime value', 'conversion',
        
        # 市场和竞争
        'market research', 'competitor analysis', 'market size', 'tam sam som',
        'go to market', 'pricing strategy', 'revenue model', 'monetization',
        'business development', 'partnership', 'strategic alliance',
        
        # 运营和管理
        'team building', 'hiring', 'company culture', 'remote work',
        'project management', 'agile development', 'lean startup',
        'mvp', 'prototype', 'user testing', 'feedback loop'
    ],
    
    'time_filters': ['week', 'month', 'year'],
    'sort_options': ['relevance', 'hot', 'top', 'new'],
    'posts_per_request': 100,
    'max_requests_per_subreddit': 10
}

# Hacker News配置
HACKER_NEWS_CONFIG = {
    'endpoints': [
        'topstories',    # 热门故事
        'newstories',    # 最新故事
        'beststories',   # 最佳故事
        'askstories',    # Ask HN
        'showstories',   # Show HN
        'jobstories'     # 工作相关
    ],
    'max_items_per_endpoint': 500,
    'min_score': 10,
    'concurrent_requests': 50
}

# arXiv配置
ARXIV_CONFIG = {
    'search_queries': [
        'startup OR entrepreneurship',
        'business model OR market analysis',
        'artificial intelligence OR machine learning',
        'fintech OR financial technology',
        'blockchain OR cryptocurrency',
        'digital transformation',
        'innovation management',
        'venture capital OR investment',
        'e-commerce OR marketplace',
        'data science OR analytics',
        'software engineering',
        'cybersecurity',
        'cloud computing',
        'internet of things',
        'biotechnology'
    ],
    'max_results_per_query': 100,
    'categories': [
        'cs.AI',  # Artificial Intelligence
        'cs.CE',  # Computational Engineering
        'cs.CY',  # Computers and Society
        'cs.DB',  # Databases
        'cs.HC',  # Human-Computer Interaction
        'cs.IR',  # Information Retrieval
        'cs.LG',  # Machine Learning
        'cs.SE',  # Software Engineering
        'econ.EM', # Econometrics
        'q-fin.CP', # Computational Finance
        'q-fin.EC', # Economics
        'q-fin.GN', # General Finance
        'q-fin.PM', # Portfolio Management
        'q-fin.ST'  # Statistical Finance
    ]
}

# GitHub配置
GITHUB_CONFIG = {
    'search_queries': [
        'startup',
        'business',
        'fintech',
        'saas',
        'marketplace',
        'e-commerce',
        'ai-startup',
        'machine-learning',
        'data-science',
        'blockchain',
        'cryptocurrency',
        'automation',
        'analytics',
        'dashboard',
        'crm',
        'erp',
        'project-management'
    ],
    'languages': [
        'Python', 'JavaScript', 'TypeScript', 'Java', 'Go',
        'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin'
    ],
    'min_stars': 50,
    'max_results_per_query': 100,
    'include_readme': True
}

# 新闻RSS配置
NEWS_RSS_CONFIG = {
    'feeds': [
        # 科技新闻
        'https://techcrunch.com/feed/',
        'https://www.theverge.com/rss/index.xml',
        'https://www.wired.com/feed/rss',
        'https://feeds.feedburner.com/venturebeat/SZYF',
        'https://feeds.feedburner.com/oreilly/radar',
        
        # 商业新闻
        'https://www.entrepreneur.com/latest.rss',
        'https://feeds.feedburner.com/fastcompany/headlines',
        'https://feeds.feedburner.com/inc/headlines',
        'https://feeds.feedburner.com/forbes/business',
        
        # 创业和投资
        'https://feeds.feedburner.com/crunchbase-news',
        'https://feeds.feedburner.com/angellist',
        'https://feeds.feedburner.com/producthunt',
        
        # 行业特定
        'https://feeds.feedburner.com/fintech-news',
        'https://feeds.feedburner.com/ai-news',
        'https://feeds.feedburner.com/blockchain-news'
    ],
    'max_articles_per_feed': 200,
    'min_content_length': 100
}

# 数据质量配置
QUALITY_CONFIG = {
    'min_text_length': 50,
    'max_text_length': 10000,
    'quality_thresholds': {
        'high': 0.7,
        'medium': 0.4,
        'low': 0.0
    },
    'required_fields': ['text', 'metadata', 'quality_score', 'category', 'type'],
    'filter_duplicates': True,
    'similarity_threshold': 0.85
}

# 并发和速率限制配置
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 20,
    'request_delay': {
        'reddit': 1.0,      # 1秒延迟
        'hacker_news': 0.5, # 0.5秒延迟
        'arxiv': 3.0,       # 3秒延迟（严格限制）
        'github': 1.0,      # 1秒延迟
        'news': 0.5         # 0.5秒延迟
    },
    'retry_attempts': 3,
    'retry_delay': 5.0,
    'timeout': 30.0
}

# 输出配置
OUTPUT_CONFIG = {
    'base_directory': 'collected_data',
    'file_formats': ['json', 'csv'],
    'include_metadata': True,
    'compress_output': True,
    'split_by_source': True,
    'max_file_size_mb': 100
}

# 监控和日志配置
MONITORING_CONFIG = {
    'log_level': 'INFO',
    'progress_update_interval': 100,  # 每100条数据更新一次进度
    'save_checkpoint_interval': 1000, # 每1000条数据保存一次检查点
    'enable_metrics': True,
    'metrics_file': 'collection_metrics.json'
}

# 数据增强配置
ENHANCEMENT_CONFIG = {
    'enable_sentiment_analysis': True,
    'enable_keyword_extraction': True,
    'enable_category_classification': True,
    'enable_quality_scoring': True,
    'enable_deduplication': True,
    'enable_text_cleaning': True
}

# 预计收集时间和资源
ESTIMATION_CONFIG = {
    'estimated_duration_hours': 4,
    'estimated_api_calls': 50000,
    'estimated_storage_gb': 2,
    'recommended_memory_gb': 4,
    'recommended_cpu_cores': 4
}