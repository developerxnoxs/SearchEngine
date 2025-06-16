import random
import requests
from abc import ABC, abstractmethod
from selectolax.parser import HTMLParser


class SearchEngineBase(ABC):
    def __init__(self):
        self.results = []
        
    def build_url(self, query, start, num_results, lang, region):
        pass
    
    def parse_results(self, html, num_results, fetched):
        pass

    def search(self, query, num_results=10, lang="en", proxy=None, safe="active",
               timeout=5, ssl_verify=False, region=None, start_num=0):
        fetched = 0
        start = start_num

        while fetched < num_results:
            url = self.build_url(query, start, num_results, lang, region)
            headers = {
                "User-Agent": self.get_random_user_agent(),
                "Accept": "*/*"
            }
            proxies = {"http": proxy, "https": proxy} if proxy else None

            try:
                resp = requests.get(url, headers=headers, timeout=timeout,
                                    verify=ssl_verify, proxies=proxies)
                html = resp.text
            except Exception:
                break

            if not html:
                break

            self.parse_results(html, num_results, fetched)
            start += 10

        return self

    def urls(self):
        return [item["url"] for item in self.results]

    def data(self):
        return self.results

    def json(self):
        import json
        return json.dumps(self.results, indent=2, ensure_ascii=False)

    def get_random_user_agent(self):
        return f"Lynx/{random.randint(2,3)}.{random.randint(8,9)}.{random.randint(0,2)} " \
               f"libwww-FM/{random.randint(2,3)}.{random.randint(13,15)} " \
               f"SSL-MM/{random.randint(1,2)}.{random.randint(3,5)} " \
               f"OpenSSL/{random.randint(1,3)}.{random.randint(0,4)}.{random.randint(0,9)}"