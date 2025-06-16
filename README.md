# Multi Search Engine (Python)

Library untuk scraping hasil pencarian dari Google, Bing, dan DuckDuckGo.

## Instalasi
```bash
pip install multi_search_engine
```

## Contoh Penggunaan
```python
from multi_search_engine.google import GoogleSearch

search = GoogleSearch().search("site:example.com", 5)
print(search.urls())
```
