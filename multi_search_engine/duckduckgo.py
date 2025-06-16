import requests
from bs4 import BeautifulSoup
from .base import SearchEngineBase

class DuckDuckGoSearch(SearchEngineBase):
    def __init__(self, delay=1, proxy=None, user_agent=None):
        super().__init__()
        self.delay = delay
        self.proxy = proxy
        self.user_agent = user_agent or "Mozilla/5.0"

    def search(self, query: str, limit: int = 10):
        headers = {"User-Agent": self.user_agent}
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        url = f"https://html.duckduckgo.com/html/?q={query}"
        resp = requests.post(url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(resp.text, "html.parser")

        for result in soup.select('.result'):
            link = result.find('a', class_='result__a')
            if link:
                self.results.append({"url": link['href'], "title": link.text})
                if len(self.results) >= limit:
                    break
        return self
