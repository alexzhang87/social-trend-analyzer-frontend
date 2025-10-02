import typing
import requests
from datetime import datetime, timezone

PUSHSHIFT_URL = "https://api.pushshift.io/reddit/search/submission/"
HEADERS = {"User-Agent": "IdeaEden-DataCollector/1.0"}


def fetch_reddit_search(query: str, limit: int = 100, subreddit: typing.Optional[str] = None) -> typing.List[dict]:
    """
    使用 Pushshift 获取 Reddit 搜索结果，返回标准化原始数据列表。
    字段: source, id, text, author, created_at, url, lang, metadata
    """
    params = {
        "q": query,
        "size": min(limit, 500),
        "sort": "desc",
        "sort_type": "created_utc",
    }
    if subreddit:
        params["subreddit"] = subreddit

    r = requests.get(PUSHSHIFT_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    items: typing.List[dict] = []
    for obj in data.get("data", [])[:limit]:
        try:
            created = obj.get("created_utc")
            created_iso = datetime.fromtimestamp(created, tz=timezone.utc).isoformat() if created else None
            item = {
                "source": "reddit",
                "id": str(obj.get("id")),
                "text": obj.get("selftext") or obj.get("title") or "",
                "author": obj.get("author"),
                "created_at": created_iso,
                "url": obj.get("full_link") or (f"https://www.reddit.com/{obj.get('permalink')}" if obj.get('permalink') else None),
                "lang": obj.get("lang") or None,
                "metadata": {
                    "subreddit": obj.get("subreddit"),
                    "score": obj.get("score"),
                    "num_comments": obj.get("num_comments"),
                    "flair": obj.get("link_flair_text"),
                },
            }
            items.append(item)
        except Exception:
            continue
    return items


__all__ = ["fetch_reddit_search"]