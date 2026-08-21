import feedparser
import requests
import logging

logger = logging.getLogger(__name__)

class NewsReader:
    @staticmethod
    def get_news(feed_url="https://lenta.ru/rss", limit=5):
        try:
            feed = feedparser.parse(feed_url)
            news = []
            for entry in feed.entries[:limit]:
                news.append(f"• {entry.title}")
            return "\n".join(news) if news else "Нет новостей"
        except Exception as e:
            return f"❌ Ошибка получения новостей: {e}"