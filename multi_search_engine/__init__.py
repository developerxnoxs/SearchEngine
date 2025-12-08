"""
Multi Search Engine Library untuk Python

Library Python untuk melakukan pencarian di berbagai mesin pencari
(Google, Bing, DuckDuckGo, Yahoo, Mojeek, Brave) dengan interface OOP yang sederhana.
"""

from .engines.google import GoogleSearch
from .engines.bing import BingSearch
from .engines.duckduckgo import DuckDuckGoSearch
from .engines.yahoo import YahooSearch
from .engines.mojeek import MojeekSearch
from .engines.brave import BraveSearch
from .base import SearchEngine, SearchResult, PageContent
from .cache import FileCache, MemoryCache, CacheInterface
from .rate_limiter import RateLimiter
from .exceptions import (
    SearchEngineException,
    NetworkException,
    ParseException,
    RateLimitException,
    BlockedException
)
from .helpers import quick_search, search_all_engines, get_available_engines, SearchAllResult, visit_url

__version__ = "1.1.0"
__author__ = "developerxnoxs"

__all__ = [
    "GoogleSearch",
    "BingSearch", 
    "DuckDuckGoSearch",
    "YahooSearch",
    "MojeekSearch",
    "BraveSearch",
    "SearchEngine",
    "SearchResult",
    "FileCache",
    "MemoryCache",
    "CacheInterface",
    "RateLimiter",
    "SearchEngineException",
    "NetworkException",
    "ParseException",
    "RateLimitException",
    "BlockedException",
    "quick_search",
    "search_all_engines",
    "get_available_engines",
    "SearchAllResult",
    "visit_url",
    "PageContent"
]
