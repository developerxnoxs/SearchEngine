import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote_plus
from .base import SearchEngineBase

class GoogleSearch(SearchEngineBase):

    def search(self, query: str, limit: int = 10):
        self.results = []
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        for start in range(0, limit * 10, 10):
            url = f"https://www.google.com/search?q={quote_plus(query)}&start={start}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.select('a[href^="/url?q="]'):
                href = a.get('href')
                parsed = parse_qs(urlparse(href).query)
                actual_url = parsed.get('q', [None])[0]

                title_tag = a.select_one('h3')
                if actual_url and title_tag:
                    self.results.append({
                        "title": title_tag.get_text(strip=True),
                        "url": actual_url
                    })

                if len(self.results) >= limit:
                    break

            if len(self.results) >= limit:
                break

        return self
