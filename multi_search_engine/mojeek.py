import requests
from bs4 import BeautifulSoup
from time import sleep
from .base import SearchEngineBase

class MojeekSearch(SearchEngineBase):
    def __init__(self, delay=1, proxy=None, user_agent=None):
        super().__init__()
        self.delay = delay
        self.proxy = proxy
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"
        )

    def search(self, query: str, limit: int = 10):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        for start in range(0, limit, 10):
            url = f"https://www.mojeek.com/search?q={query}&s={start}"
            resp = requests.get(url, headers=headers, proxies=proxies)
            if resp.status_code == 403:
                print("Access denied (403) - Mojeek memblokir scraping.")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            for li in soup.select("li"):
                title_tag = li.select_one("h2 > a.title")
                if title_tag and title_tag.get("href"):
                    self.results.append({
                        "url": title_tag["href"],
                        "title": title_tag.get_text(strip=True)
                    })
                    if len(self.results) >= limit:
                        return self
            sleep(self.delay)
        return self
