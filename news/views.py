import time
from django.shortcuts import render
from django.core.cache import cache

try:
    import feedparser
except ImportError:
    feedparser = None

# Live RSS feeds for food & cooking news (no API key required).
FOOD_NEWS_FEEDS = [
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/DiningandWine.xml", "source": "NY Times Food"},
    {"url": "https://www.foodsafetynews.com/feed/", "source": "Food Safety News"},
    {"url": "https://www.bbc.co.uk/food/recipes/rss.xml", "source": "BBC Food"},
    {"url": "https://www.seriouseats.com/feed/all", "source": "Serious Eats"},
]

CACHE_KEY = "food_news_articles"
CACHE_TIMEOUT = 60 * 30  # 30 minutes


def _extract_image(entry):
    """Try a few common RSS/Media-RSS fields to find an article image."""
    try:
        if hasattr(entry, "media_content") and entry.media_content:
            return entry.media_content[0].get("url")
        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url")
        if hasattr(entry, "links"):
            for link in entry.links:
                if "image" in link.get("type", ""):
                    return link.get("href")
        if hasattr(entry, "summary"):
            import re
            match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None


def _clean_summary(entry):
    import re
    text = entry.get("summary", "") or entry.get("description", "")
    text = re.sub("<[^<]+?>", "", text)  # strip HTML tags
    text = text.strip()
    if len(text) > 180:
        text = text[:180].rsplit(" ", 1)[0] + "…"
    return text


def fetch_food_news():
    """Pull the latest items from each configured food-news RSS feed."""
    articles = []
    if feedparser is None:
        return articles

    for feed_info in FOOD_NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:6]:
                articles.append({
                    "title": entry.get("title", "Untitled"),
                    "link": entry.get("link", "#"),
                    "summary": _clean_summary(entry),
                    "published": entry.get("published", ""),
                    "published_parsed": entry.get("published_parsed"),
                    "image": _extract_image(entry),
                    "source": feed_info["source"],
                })
        except Exception:
            # Skip a feed if it's down/unreachable, don't break the whole page.
            continue

    def sort_key(article):
        return article["published_parsed"] or time.gmtime(0)

    articles.sort(key=sort_key, reverse=True)
    return articles


def food_news(request):
    articles = cache.get(CACHE_KEY)
    if articles is None:
        articles = fetch_food_news()
        cache.set(CACHE_KEY, articles, CACHE_TIMEOUT)

    return render(request, "news/food_news.html", {
        "articles": articles,
        "feed_unavailable": feedparser is None,
    })
