import webbrowser
import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class WebSearch:
    """Модуль для поиска информации в интернете"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search(self, query: str, num_results: int = 3) -> str:
        """Ищет информацию в интернете через DuckDuckGo"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={query}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return "❌ Не удалось выполнить поиск (ошибка соединения)"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result')
            
            if not results:
                return "❌ Ничего не найдено"
            
            summary = []
            for i, result in enumerate(results[:num_results]):
                title = result.find('a', class_='result__a')
                snippet = result.find('a', class_='result__snippet')
                
                if title and snippet:
                    summary.append(f"{i+1}. {title.text.strip()}\n   {snippet.text.strip()}\n")
            
            if summary:
                return "🔍 Результаты поиска:\n\n" + "\n".join(summary)
            else:
                return "❌ Не удалось извлечь информацию"
                
        except requests.exceptions.Timeout:
            return "❌ Таймаут подключения. Проверьте интернет."
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return f"❌ Ошибка при поиске: {str(e)}"

    def open_browser_search(self, query: str):
        """Открывает браузер с результатами поиска"""
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"🌐 Открыл поиск в браузере по запросу: {query}"

    def get_weather(self, city: str = "Moscow") -> str:
        """Получает погоду для указанного города (чистый текст без HTML)"""
        try:
            # Пробуем разные форматы запроса
            formats = [
                f"https://wttr.in/{city}?format=%C+%t+%w+%h",
                f"https://wttr.in/{city}?format=%C+%t",
                f"https://wttr.in/{city}?0T"
            ]
            
            for url in formats:
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                
                text = response.text.strip()
                
                # Если это HTML — парсим
                if "<html" in text.lower():
                    soup = BeautifulSoup(text, 'html.parser')
                    term_div = soup.find('div', class_='term-container')
                    if term_div:
                        content = term_div.get_text(strip=True)
                        # Убираем лишние пробелы
                        content = re.sub(r'\s+', ' ', content)
                        if content:
                            return f"🌤️ Погода в {city}: {content}"
                    continue
                
                # Если это простой текст
                if text and len(text) < 500:
                    return f"🌤️ Погода в {city}: {text}"
            
            return "❌ Не удалось получить погоду. Проверьте название города."
            
        except requests.exceptions.Timeout:
            return "❌ Таймаут подключения. Проверьте интернет."
        except Exception as e:
            logger.error(f"Ошибка погоды: {e}")
            return f"❌ Ошибка: {str(e)}"