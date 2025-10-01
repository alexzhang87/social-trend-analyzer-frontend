import json
import random
from datetime import datetime, timedelta

def add_vision_pro_data():
    """向数据集添加Vision Pro相关数据"""
    
    # 读取现有数据集
    with open('large_mock_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Vision Pro相关帖子数据
    vision_pro_posts = [
        {
            "platform": "twitter",
            "id": "tweet_vp_1",
            "author": "TechReviewer",
            "text": "Vision Pro的空间计算体验真的很震撼！未来已来 🥽✨",
            "url": "https://twitter.com/TechReviewer/status/vp1",
            "created_at": "2025-08-20T10:00:00",
            "sentiment": "positive",
            "likes": 1250,
            "retweets": 340,
            "replies": 89,
            "views": 15600,
            "verified": True,
            "follower_count": 45000,
            "keywords_matched": ["Vision Pro"],
            "language": "zh"
        },
        {
            "platform": "twitter",
            "id": "tweet_vp_2",
            "author": "AppleFan2024",
            "text": "Vision Pro price is still too high for most consumers. Waiting for Gen 2 💰",
            "url": "https://twitter.com/AppleFan2024/status/vp2",
            "created_at": "2025-08-19T14:30:00",
            "sentiment": "neutral",
            "likes": 890,
            "retweets": 156,
            "replies": 234,
            "views": 8900,
            "verified": False,
            "follower_count": 12000,
            "keywords_matched": ["Vision Pro"],
            "language": "en"
        },
        {
            "platform": "reddit",
            "id": "reddit_vp_1",
            "author": "VREnthusiast",
            "text": "r/apple - Vision Pro开发者体验分享：空间应用开发的新纪元",
            "url": "https://reddit.com/r/apple/comments/vp1",
            "created_at": "2025-08-18T16:45:00",
            "sentiment": "positive",
            "upvotes": 2340,
            "comments": 567,
            "views": 23400,
            "verified": False,
            "follower_count": 8900,
            "keywords_matched": ["Vision Pro"],
            "language": "zh"
        },
        {
            "platform": "twitter",
            "id": "tweet_vp_3",
            "author": "SkepticalUser",
            "text": "Vision Pro feels like a tech demo rather than a finished product. Too many limitations.",
            "url": "https://twitter.com/SkepticalUser/status/vp3",
            "created_at": "2025-08-17T09:15:00",
            "sentiment": "negative",
            "likes": 445,
            "retweets": 78,
            "replies": 156,
            "views": 5600,
            "verified": False,
            "follower_count": 3400,
            "keywords_matched": ["Vision Pro"],
            "language": "en"
        },
        {
            "platform": "reddit",
            "id": "reddit_vp_2",
            "author": "DevCommunity",
            "text": "r/programming - Vision Pro原生应用开发指南：从零到发布",
            "url": "https://reddit.com/r/programming/comments/vp2",
            "created_at": "2025-08-16T11:20:00",
            "sentiment": "positive",
            "upvotes": 1890,
            "comments": 234,
            "views": 18900,
            "verified": False,
            "follower_count": 15600,
            "keywords_matched": ["Vision Pro"],
            "language": "zh"
        }
    ]
    
    # 添加到数据集
    dataset['data'].extend(vision_pro_posts)
    
    # 更新统计信息
    if 'keywords' not in dataset:
        dataset['keywords'] = []
    if 'Vision Pro' not in dataset['keywords']:
        dataset['keywords'].append('Vision Pro')
    
    # 保存更新后的数据集
    with open('large_mock_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已添加 {len(vision_pro_posts)} 条Vision Pro相关帖子")
    print(f"📊 数据集总帖子数: {len(dataset['data'])}")

if __name__ == "__main__":
    add_vision_pro_data()