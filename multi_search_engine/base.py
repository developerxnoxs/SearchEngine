"""
Base class untuk semua search engines
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
import random
import hashlib
import json

from .exceptions import NetworkException, ParseException, BlockedException
from .cache import CacheInterface
from .rate_limiter import RateLimiter
import re


BLOCKED_PAGE_PATTERNS = [
    (r'<form[^>]*captcha[^>]*>', 'Captcha detected - please use a proxy'),
    (r'<div[^>]*id=["\']captcha["\'][^>]*>', 'Captcha detected - please use a proxy'),
    (r'<div[^>]*class=["\']captcha["\'][^>]*>', 'Captcha detected - please use a proxy'),
    (r'<input[^>]*captcha[^>]*>', 'Captcha detected - please use a proxy'),
    (r'solve\s+the\s+captcha', 'Captcha detected - please use a proxy'),
    (r'complete\s+the\s+captcha', 'Captcha detected - please use a proxy'),
    (r'unusual\s+traffic\s+from', 'Unusual traffic detected - please use a proxy'),
    (r'automated\s+queries', 'Automated queries blocked - please use a proxy'),
    (r'are\s+you\s+a\s+robot', 'Bot detection triggered - please use a proxy'),
    (r'verify\s+you\s+are\s+(a\s+)?human', 'Human verification required - please use a proxy'),
    (r'<title>.*too\s+many\s+requests.*</title>', 'Rate limit reached - please use a proxy or add delay'),
    (r'please\s+complete\s+the\s+security\s+check', 'Security check required - please use a proxy'),
    (r'<title>.*access\s+denied.*</title>', 'Access denied - please use a proxy'),
    (r'<title>.*blocked.*</title>', 'Blocked - please use a proxy'),
    (r'CfConfig.*siteKey', 'Cloudflare/Bing verification required - please use a proxy or ScraperAPI'),
    (r'challenge/verify\?partner', 'Bing verification required - please use a proxy or ScraperAPI'),
]


def detect_blocked_page(html: str) -> Optional[str]:
    """Deteksi halaman yang terblokir - sama seperti PHP"""
    for pattern, message in BLOCKED_PAGE_PATTERNS:
        if re.search(pattern, html, re.IGNORECASE):
            return message
    return None


@dataclass
class PageContent:
    """Representasi konten halaman yang di-visit"""
    url: str
    title: str
    text: str
    html: str
    status_code: int
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konversi ke dictionary"""
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "status_code": self.status_code,
            "success": self.success,
            "error": self.error
        }
    
    def get_text_preview(self, max_length: int = 500) -> str:
        """Dapatkan preview teks dengan panjang tertentu"""
        if len(self.text) <= max_length:
            return self.text
        return self.text[:max_length] + "..."


@dataclass
class SearchResult:
    """Representasi satu hasil pencarian"""
    title: str
    url: str
    description: str
    position: int = 0
    engine: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konversi ke dictionary"""
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "position": self.position,
            "engine": self.engine,
            "extra": self.extra
        }
    
    def visit(self, timeout: int = 30, user_agent: Optional[str] = None) -> PageContent:
        """
        Kunjungi URL dan ambil konten halaman.
        
        Args:
            timeout: Timeout dalam detik (default: 30)
            user_agent: Custom user agent (opsional)
            
        Returns:
            PageContent: Object berisi konten halaman
            
        Contoh:
            >>> result = results[0]
            >>> page = result.visit()
            >>> print(page.title)
            >>> print(page.text[:500])
        """
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        headers = {
            "User-Agent": user_agent or default_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        try:
            response = requests.get(self.url, headers=headers, timeout=timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else ""
            
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            text = ' '.join(soup.get_text(separator=' ').split())
            
            return PageContent(
                url=self.url,
                title=title or self.title,
                text=text,
                html=response.text,
                status_code=response.status_code,
                success=True
            )
        except requests.exceptions.Timeout:
            return PageContent(
                url=self.url, title="", text="", html="",
                status_code=0, success=False, error=f"Timeout setelah {timeout}s"
            )
        except requests.exceptions.RequestException as e:
            return PageContent(
                url=self.url, title="", text="", html="",
                status_code=0, success=False, error=str(e)
            )
    
    def __repr__(self) -> str:
        return f"SearchResult(title='{self.title[:50]}...', url='{self.url}')"


class SearchEngine(ABC):
    """Base class untuk semua search engines"""
    
    ENGINE_NAME = "base"
    BASE_URL = ""
    
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: int = 30,
        delay: float = 1.0,
        cache: Optional[CacheInterface] = None,
        rate_limiter: Optional[RateLimiter] = None,
        scraper_api_key: Optional[str] = None
    ):
        self.user_agent = user_agent or random.choice(self.DEFAULT_USER_AGENTS)
        self.proxy = proxy
        self.timeout = timeout
        self.delay = delay
        self.cache = cache
        self.rate_limiter = rate_limiter
        self.scraper_api_key = scraper_api_key
        self._last_request_time = 0
        self._results: List[SearchResult] = []
        self._raw_html: str = ""
    
    def __enter__(self):
        """Context manager entry - untuk penggunaan dengan 'with' statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup jika diperlukan"""
        self._results = []
        self._raw_html = ""
        return False
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate HTTP headers - sama seperti PHP"""
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration"""
        if self.proxy:
            return {
                "http": self.proxy,
                "https": self.proxy
            }
        return None
    
    def _apply_delay(self):
        """Apply delay between requests"""
        if self.delay > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed + random.uniform(0.1, 0.5))
        self._last_request_time = time.time()
    
    def _generate_cache_key(self, query: str, **params) -> str:
        """Generate unique cache key"""
        key_data = f"{self.ENGINE_NAME}:{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _build_url_with_scraper_api(self, url: str) -> str:
        """Build URL using ScraperAPI"""
        if self.scraper_api_key:
            from urllib.parse import quote
            return f"http://api.scraperapi.com?api_key={self.scraper_api_key}&url={quote(url)}"
        return url
    
    def _fetch(self, url: str) -> str:
        """Fetch URL content"""
        if self.rate_limiter:
            self.rate_limiter.wait()
        
        self._apply_delay()
        
        try:
            if self.scraper_api_key:
                url = self._build_url_with_scraper_api(url)
                proxies = None
            else:
                proxies = self._get_proxies()
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                proxies=proxies,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 429:
                if self.rate_limiter:
                    self.rate_limiter.backoff()
                raise BlockedException("Rate limited by search engine")
            
            if response.status_code == 403:
                raise BlockedException("Blocked by search engine")
            
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.Timeout:
            raise NetworkException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NetworkException(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Request failed: {str(e)}")
    
    @abstractmethod
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build search URL - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse HTML and extract results - must be implemented by subclasses"""
        pass
    
    def search(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True,
        use_cache: bool = True
    ) -> List[SearchResult]:
        """
        Melakukan pencarian
        
        Args:
            query: Kata kunci pencarian
            page: Halaman hasil (default: 1)
            num_results: Jumlah hasil per halaman (default: 10)
            language: Kode bahasa (contoh: 'id', 'en')
            country: Kode negara (contoh: 'ID', 'US')
            safe_search: Aktifkan SafeSearch (default: True)
            use_cache: Gunakan cache (default: True)
            
        Returns:
            List[SearchResult]: Daftar hasil pencarian
        """
        cache_key = self._generate_cache_key(
            query,
            page=page,
            num_results=num_results,
            language=language,
            country=country,
            safe_search=safe_search
        )
        
        if use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return [SearchResult(**r) for r in cached]
        
        url = self._build_search_url(
            query=query,
            page=page,
            num_results=num_results,
            language=language,
            country=country,
            safe_search=safe_search
        )
        
        self._raw_html = self._fetch(url)
        
        blocked_message = detect_blocked_page(self._raw_html)
        if blocked_message:
            raise BlockedException(blocked_message)
        
        self._results = self._parse_results(self._raw_html)
        
        for i, result in enumerate(self._results):
            result.position = (page - 1) * num_results + i + 1
            result.engine = self.ENGINE_NAME
        
        if self.cache:
            self.cache.set(cache_key, [r.to_dict() for r in self._results])
        
        return self._results
    
    def get_results(self) -> List[SearchResult]:
        """Get hasil pencarian terakhir"""
        return self._results
    
    def get_raw_html(self) -> str:
        """Get HTML mentah dari pencarian terakhir"""
        return self._raw_html
    
    def filter_by_keyword(self, keyword: str) -> List[SearchResult]:
        """Filter hasil berdasarkan kata kunci di title atau description"""
        keyword_lower = keyword.lower()
        return [
            r for r in self._results 
            if keyword_lower in r.title.lower() or keyword_lower in r.description.lower()
        ]
    
    def filter_by_domain(self, domain: str) -> List[SearchResult]:
        """Filter hasil berdasarkan domain"""
        domain_lower = domain.lower()
        return [
            r for r in self._results 
            if domain_lower in r.url.lower()
        ]
    
    def limit_results(self, count: int) -> List[SearchResult]:
        """Batasi jumlah hasil"""
        return self._results[:count]
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Konversi semua hasil ke list of dict"""
        return [r.to_dict() for r in self._results]
    
    def to_json(self, indent: int = 2) -> str:
        """Konversi semua hasil ke JSON string"""
        return json.dumps(self.to_dict_list(), indent=indent, ensure_ascii=False)
