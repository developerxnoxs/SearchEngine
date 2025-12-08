# Multi Search Engine

[![PyPI version](https://badge.fury.io/py/multi-search-engine.svg)](https://badge.fury.io/py/multi-search-engine)
[![Python Versions](https://img.shields.io/pypi/pyversions/multi-search-engine.svg)](https://pypi.org/project/multi-search-engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/yourusername/multi-search-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/multi-search-engine/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/multi-search-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/multi-search-engine)
[![Downloads](https://pepy.tech/badge/multi-search-engine)](https://pepy.tech/project/multi-search-engine)

A powerful Python library for searching across multiple search engines with a unified interface. Supports Google, Bing, DuckDuckGo, Yahoo, Mojeek, and Brave with built-in caching, rate limiting, and proxy support.

## Features

- **6 Search Engines**: Google, Bing, DuckDuckGo, Yahoo, Mojeek, Brave
- **Unified Interface**: Same API for all search engines
- **Caching**: File-based and memory-based caching
- **Rate Limiting**: Built-in rate limiter with exponential backoff
- **Proxy Support**: Works with custom proxies and ScraperAPI
- **Result Filtering**: Filter by keyword, domain, or limit count
- **Export Options**: Export to JSON or dictionary format
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Comprehensive exception handling

## Installation

```bash
pip install multi-search-engine
```

## Quick Start

```python
from multi_search_engine import DuckDuckGoSearch

# Create search engine instance
ddg = DuckDuckGoSearch()

# Perform search
results = ddg.search("Python programming", num_results=10)

# Process results
for result in results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Description: {result.description}")
    print()
```

## Supported Search Engines

| Engine | Class | No Proxy | With ScraperAPI | Recommendation |
|--------|-------|----------|-----------------|----------------|
| DuckDuckGo | `DuckDuckGoSearch` | Stable | Stable | Direct (no proxy needed) |
| Yahoo | `YahooSearch` | Stable | Stable | Direct (no proxy needed) |
| Mojeek | `MojeekSearch` | Stable | Stable | Direct (no proxy needed) |
| Brave | `BraveSearch` | Stable | Stable | Direct (no proxy needed) |
| Bing | `BingSearch` | May require captcha | OK | Use ScraperAPI |
| Google | `GoogleSearch` | Blocked | OK | ScraperAPI required |

> **Note:** Google and Bing actively block automated requests. Use ScraperAPI for reliable results.

## Usage Examples

### Basic Search

```python
from multi_search_engine import DuckDuckGoSearch, BingSearch, GoogleSearch

# DuckDuckGo (no proxy needed)
ddg = DuckDuckGoSearch()
results = ddg.search("Python programming", num_results=10)

# With search parameters
results = ddg.search(
    query="machine learning",
    page=1,
    num_results=10,
    language="en",
    country="US",
    safe_search=True
)
```

### Using ScraperAPI (for Google/Bing)

```python
from multi_search_engine import GoogleSearch

google = GoogleSearch(scraper_api_key="YOUR_API_KEY")
results = google.search("Python programming")

for result in results:
    print(f"{result.title}: {result.url}")
```

### Caching Results

```python
from multi_search_engine import DuckDuckGoSearch, FileCache, MemoryCache

# File-based cache (persistent)
file_cache = FileCache(cache_dir=".search_cache", default_ttl=3600)
ddg = DuckDuckGoSearch(cache=file_cache)

# Memory cache (session-only)
mem_cache = MemoryCache(default_ttl=600)
ddg = DuckDuckGoSearch(cache=mem_cache)

# Results are automatically cached
results = ddg.search("Python tutorial")
```

### Rate Limiting

```python
from multi_search_engine import BingSearch, RateLimiter

limiter = RateLimiter(
    requests_per_minute=10,
    min_delay=1.0,
    max_delay=60.0
)

bing = BingSearch(rate_limiter=limiter)
results = bing.search("web development")
```

### Using Custom Proxy

```python
from multi_search_engine import YahooSearch

yahoo = YahooSearch(proxy="http://proxy.example.com:8080")
results = yahoo.search("technology news")
```

### Filtering Results

```python
from multi_search_engine import BraveSearch

brave = BraveSearch()
results = brave.search("programming tutorials", num_results=20)

# Filter by keyword
python_results = brave.filter_by_keyword("python")

# Filter by domain
github_results = brave.filter_by_domain("github.com")

# Limit results
top_5 = brave.limit_results(5)
```

### Export Results

```python
from multi_search_engine import DuckDuckGoSearch

ddg = DuckDuckGoSearch()
results = ddg.search("data science")

# Export to list of dictionaries
data = ddg.to_dict_list()

# Export to JSON string
json_str = ddg.to_json(indent=2)

# Save to file
with open("results.json", "w") as f:
    f.write(ddg.to_json())
```

### Error Handling

```python
from multi_search_engine import (
    DuckDuckGoSearch,
    NetworkException,
    ParseException,
    BlockedException
)

ddg = DuckDuckGoSearch()

try:
    results = ddg.search("query")
except NetworkException as e:
    print(f"Network error: {e}")
except ParseException as e:
    print(f"Failed to parse results: {e}")
except BlockedException as e:
    print(f"Blocked by search engine: {e}")
```

## API Reference

### SearchEngine Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_agent` | str | Random | Custom user agent string |
| `proxy` | str | None | Proxy URL |
| `timeout` | int | 30 | Request timeout in seconds |
| `delay` | float | 1.0 | Delay between requests |
| `cache` | CacheInterface | None | Cache instance |
| `rate_limiter` | RateLimiter | None | Rate limiter instance |
| `scraper_api_key` | str | None | ScraperAPI API key |

### Search Method Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | Required | Search query |
| `page` | int | 1 | Page number |
| `num_results` | int | 10 | Results per page |
| `language` | str | None | Language code (e.g., 'en', 'id') |
| `country` | str | None | Country code (e.g., 'US', 'ID') |
| `safe_search` | bool | True | Enable safe search |
| `use_cache` | bool | True | Use cached results |

### SearchResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | str | Result title |
| `url` | str | Result URL |
| `description` | str | Result description/snippet |
| `position` | int | Position in search results |
| `engine` | str | Search engine name |
| `extra` | dict | Additional metadata |

## Project Structure

```
multi-search-engine/
├── multi_search_engine/
│   ├── __init__.py
│   ├── base.py              # Base class and SearchResult
│   ├── cache.py             # FileCache and MemoryCache
│   ├── rate_limiter.py      # RateLimiter
│   ├── exceptions.py        # Custom exceptions
│   └── engines/
│       ├── __init__.py
│       ├── google.py
│       ├── bing.py
│       ├── duckduckgo.py
│       ├── yahoo.py
│       ├── mojeek.py
│       └── brave.py
├── tests/
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## Security

For security concerns, please read our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Acknowledgments

- Thanks to all contributors
- Inspired by the need for a unified search interface
- Built with Python and love
