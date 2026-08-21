from src.web_search import WebSearch
from src.news_reader import NewsReader

class NetworkHandler:
    def __init__(self, agent):
        self.agent = agent
        self.web = WebSearch()

    def search_web(self, query, open_browser=False):
        if open_browser:
            return self.web.open_browser_search(query)
        else:
            return self.web.search(query)

    def get_weather(self, city):
        return self.web.get_weather(city)

    def get_news(self, feed_url=None):
        if feed_url:
            return NewsReader.get_news(feed_url=feed_url)
        else:
            return NewsReader.get_news()

    def handle(self, user_goal: str, use_voice: bool) -> str:
        # Этот обработчик не используется напрямую в маршрутизации, так как поиск и погода обрабатываются в agent.py,
        # но мы можем оставить его для полноты.
        return None