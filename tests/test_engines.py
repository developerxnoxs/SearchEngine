"""
Unit tests untuk Multi Search Engine Library
"""

import pytest
from unittest.mock import Mock, patch
from multi_search_engine import (
    GoogleSearch,
    BingSearch,
    DuckDuckGoSearch,
    YahooSearch,
    MojeekSearch,
    BraveSearch,
    SearchResult,
    FileCache,
    MemoryCache,
    RateLimiter,
    NetworkException,
    ParseException,
    BlockedException
)


class TestSearchResult:
    """Test SearchResult dataclass"""
    
    def test_create_search_result(self):
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            description="Test description"
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.description == "Test description"
        assert result.position == 0
        assert result.engine == ""
    
    def test_to_dict(self):
        result = SearchResult(
            title="Test",
            url="https://example.com",
            description="Desc",
            position=1,
            engine="google"
        )
        d = result.to_dict()
        assert d["title"] == "Test"
        assert d["url"] == "https://example.com"
        assert d["position"] == 1
        assert d["engine"] == "google"


class TestMemoryCache:
    """Test MemoryCache"""
    
    def test_set_and_get(self):
        cache = MemoryCache()
        cache.set("key1", {"data": "value"})
        result = cache.get("key1")
        assert result == {"data": "value"}
    
    def test_get_nonexistent(self):
        cache = MemoryCache()
        result = cache.get("nonexistent")
        assert result is None
    
    def test_delete(self):
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self):
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestRateLimiter:
    """Test RateLimiter"""
    
    def test_create_rate_limiter(self):
        limiter = RateLimiter(requests_per_minute=10)
        assert limiter.requests_per_minute == 10
    
    def test_wait_doesnt_block_first_request(self):
        limiter = RateLimiter(requests_per_minute=60)
        import time
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        assert elapsed < 1.0


class TestSearchEngineBase:
    """Test base functionality of search engines"""
    
    def test_duckduckgo_engine_name(self):
        ddg = DuckDuckGoSearch()
        assert ddg.ENGINE_NAME == "duckduckgo"
    
    def test_google_engine_name(self):
        google = GoogleSearch()
        assert google.ENGINE_NAME == "google"
    
    def test_bing_engine_name(self):
        bing = BingSearch()
        assert bing.ENGINE_NAME == "bing"
    
    def test_yahoo_engine_name(self):
        yahoo = YahooSearch()
        assert yahoo.ENGINE_NAME == "yahoo"
    
    def test_mojeek_engine_name(self):
        mojeek = MojeekSearch()
        assert mojeek.ENGINE_NAME == "mojeek"
    
    def test_brave_engine_name(self):
        brave = BraveSearch()
        assert brave.ENGINE_NAME == "brave"


class TestSearchEngineWithMock:
    """Test search engines with mocked HTTP responses"""
    
    @patch('requests.get')
    def test_duckduckgo_search_mock(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <body>
        <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com">
            Test Result
        </a>
        <div class="result__snippet">Test description</div>
        </body>
        </html>
        '''
        mock_get.return_value = mock_response
        
        ddg = DuckDuckGoSearch(delay=0)
        results = ddg.search("test query", use_cache=False)
        
        assert mock_get.called
    
    @patch('requests.get')
    def test_network_error_handling(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        ddg = DuckDuckGoSearch(delay=0)
        
        with pytest.raises(NetworkException):
            ddg.search("test query", use_cache=False)
    
    @patch('requests.get')
    def test_rate_limit_handling(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        ddg = DuckDuckGoSearch(delay=0)
        
        with pytest.raises(BlockedException):
            ddg.search("test query", use_cache=False)


class TestFilterMethods:
    """Test filter methods"""
    
    def test_filter_by_keyword(self):
        ddg = DuckDuckGoSearch()
        ddg._results = [
            SearchResult(title="Python Tutorial", url="https://example.com/1", description="Learn Python"),
            SearchResult(title="Java Guide", url="https://example.com/2", description="Learn Java"),
            SearchResult(title="Python Advanced", url="https://example.com/3", description="Advanced topics"),
        ]
        
        filtered = ddg.filter_by_keyword("python")
        assert len(filtered) == 2
    
    def test_filter_by_domain(self):
        ddg = DuckDuckGoSearch()
        ddg._results = [
            SearchResult(title="Result 1", url="https://github.com/test", description=""),
            SearchResult(title="Result 2", url="https://example.com/test", description=""),
            SearchResult(title="Result 3", url="https://github.com/another", description=""),
        ]
        
        filtered = ddg.filter_by_domain("github.com")
        assert len(filtered) == 2
    
    def test_limit_results(self):
        ddg = DuckDuckGoSearch()
        ddg._results = [
            SearchResult(title=f"Result {i}", url=f"https://example.com/{i}", description="")
            for i in range(10)
        ]
        
        limited = ddg.limit_results(3)
        assert len(limited) == 3


class TestExportMethods:
    """Test export methods"""
    
    def test_to_dict_list(self):
        ddg = DuckDuckGoSearch()
        ddg._results = [
            SearchResult(title="Test", url="https://example.com", description="Desc", position=1, engine="duckduckgo")
        ]
        
        result = ddg.to_dict_list()
        assert len(result) == 1
        assert result[0]["title"] == "Test"
        assert result[0]["engine"] == "duckduckgo"
    
    def test_to_json(self):
        import json
        ddg = DuckDuckGoSearch()
        ddg._results = [
            SearchResult(title="Test", url="https://example.com", description="Desc")
        ]
        
        json_str = ddg.to_json()
        parsed = json.loads(json_str)
        assert len(parsed) == 1
        assert parsed[0]["title"] == "Test"
