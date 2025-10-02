import typing
from datetime import datetime

try:
    import snscrape.modules.twitter as sntwitter
except Exception as e:
    raise RuntimeError(f"snscrape.twitter 未安装或不可用: {e}")


def fetch_twitter_search(query: str, limit: int = 100) -> typing.List[dict]:
    """
    使用 snsrape 获取 Twitter 搜索结果，返回标准化的原始数据记录列表。
    标准字段: source, id, text, author, created_at, url, lang, metadata
    """
    items: typing.List[dict] = []
    scraper = sntwitter.TwitterSearchScraper(query)
    for i, tweet in enumerate(scraper.get_items()):
        try:
            author = getattr(tweet, 'user', None)
            item = {
                "source": "twitter",
                "id": str(getattr(tweet, 'id', None)),
                "text": getattr(tweet, 'rawContent', '') or getattr(tweet, 'content', ''),
                "author": getattr(author, 'username', None) if author else None,
                "created_at": getattr(tweet, 'date', None).isoformat() if getattr(tweet, 'date', None) else None,
                "url": getattr(tweet, 'url', None),
                "lang": getattr(tweet, 'lang', None),
                "metadata": {
                    "replyCount": getattr(tweet, 'replyCount', None),
                    "retweetCount": getattr(tweet, 'retweetCount', None),
                    "likeCount": getattr(tweet, 'likeCount', None),
                    "hashtags": getattr(tweet, 'hashtags', None) or [],
                },
            }
            items.append(item)
        except Exception:
            # 跳过单条解析异常，保证持续采集
            continue
        if i + 1 >= limit:
            break
    return items


__all__ = ["fetch_twitter_search"]