# Multi Search Engine Library

## Overview
A Python library for searching across multiple search engines (Google, Bing, DuckDuckGo, Yahoo, Mojeek, Brave) with caching, rate limiting, and proxy support.

## Project Structure
```
multi-search-engine/
├── multi_search_engine/
│   ├── __init__.py          # Main exports
│   ├── base.py               # SearchEngine base class, SearchResult
│   ├── cache.py              # FileCache, MemoryCache
│   ├── rate_limiter.py       # RateLimiter
│   ├── exceptions.py         # Custom exceptions
│   └── engines/
│       ├── google.py         # GoogleSearch
│       ├── bing.py           # BingSearch
│       ├── duckduckgo.py     # DuckDuckGoSearch
│       ├── yahoo.py          # YahooSearch
│       ├── mojeek.py         # MojeekSearch
│       └── brave.py          # BraveSearch
├── tests/
│   └── test_engines.py       # Unit tests
├── main.py                   # Demo script
├── test_engines.py           # Integration tests
└── pyproject.toml            # Project configuration
```

## Running the Project
- **Demo**: Run `python main.py` to see the library in action
- **Tests**: Run `pytest tests/` for unit tests

## Supported Search Engines
| Engine | Class | Proxy Required |
|--------|-------|----------------|
| DuckDuckGo | `DuckDuckGoSearch` | No |
| Yahoo | `YahooSearch` | No |
| Mojeek | `MojeekSearch` | No |
| Brave | `BraveSearch` | No |
| Bing | `BingSearch` | Recommended |
| Google | `GoogleSearch` | Required (ScraperAPI) |

## Dependencies
- beautifulsoup4
- requests
- build
- twine
