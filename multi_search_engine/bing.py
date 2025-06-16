import requests
from bs4 import BeautifulSoup
from time import sleep
from .base import SearchEngineBase

class BingSearch(SearchEngineBase):
    def __init__(self, delay=1, proxy=None, user_agent=None):
        super().__init__()
        self.delay = delay
        self.proxy = proxy
        self.user_agent = user_agent or "Mozilla/5.0"

    def search(self, query: str, limit: int = 10):
        headers = {"User-Agent": self.user_agent}
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        for start in range(0, limit * 10, 10):
            url = f"https://www.bing.com/search?q={query}&first={start + 1}"
            try:
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                if resp.status_code != 200:
                    print(f"Request failed with status: {resp.status_code}")
                    break
                soup = BeautifulSoup(resp.text, "html.parser")

                for li in soup.select("li.b_algo"):
                    a = li.find("a")
                    if a and a.get("href"):
                        self.results.append({
                            "url": a["href"],
                            "title": a.get_text(strip=True)
                        })
                        if len(self.results) >= limit:
                            return self

                sleep(self.delay)

            except Exception as e:
                print(f"Error: {e}")
                break

        return self
