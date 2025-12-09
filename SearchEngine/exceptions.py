"""
Custom exceptions untuk Multi Search Engine Library
"""


class SearchEngineException(Exception):
    """Base exception untuk semua error search engine"""
    pass


class NetworkException(SearchEngineException):
    """Exception untuk error jaringan/HTTP"""
    pass


class ParseException(SearchEngineException):
    """Exception untuk error parsing HTML"""
    pass


class RateLimitException(SearchEngineException):
    """Exception ketika terkena rate limit"""
    pass


class BlockedException(SearchEngineException):
    """Exception ketika di-block oleh search engine"""
    pass


class CacheException(SearchEngineException):
    """Exception untuk error cache"""
    pass


class ConfigurationException(SearchEngineException):
    """Exception untuk error konfigurasi"""
    pass
