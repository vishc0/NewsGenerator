import feedparser
import requests
from newspaper import Article
from newspaper.article import ArticleException
from datetime import datetime, timedelta


def fetch_feed(url, since_hours=48):
    d = feedparser.parse(url)
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    entries = []
    for e in d.entries:
        # feedparser may have published_parsed
        pub = None
        if hasattr(e, 'published_parsed') and e.published_parsed:
            pub = datetime(*e.published_parsed[:6])
        elif hasattr(e, 'updated_parsed') and e.updated_parsed:
            pub = datetime(*e.updated_parsed[:6])
        else:
            pub = datetime.utcnow()

        if pub < cutoff:
            continue

        entries.append({
            'title': e.get('title'),
            'link': e.get('link'),
            'published': pub.isoformat(),
            'description': e.get('description', e.get('summary', ''))
        })

    return entries


def fetch_article_text(url):
    # newspaper3k provides robust extraction for many sites
    try:
        art = Article(url)
        art.download()
        art.parse()
        return art.text
    except (ArticleException, requests.RequestException, ConnectionError, OSError, ValueError):
        # Fallback: return empty string if article cannot be fetched
        # The pipeline will handle this gracefully by using RSS description
        return ""
