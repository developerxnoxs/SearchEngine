"""
Helper functions untuk kemudahan penggunaan Multi Search Engine Library
"""

from typing import Optional, List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import SearchResult
from .engines.google import GoogleSearch
from .engines.bing import BingSearch
from .engines.duckduckgo import DuckDuckGoSearch
from .engines.yahoo import YahooSearch
from .engines.mojeek import MojeekSearch
from .engines.brave import BraveSearch
from .cache import CacheInterface


ENGINES = {
    "google": GoogleSearch,
    "bing": BingSearch,
    "duckduckgo": DuckDuckGoSearch,
    "yahoo": YahooSearch,
    "mojeek": MojeekSearch,
    "brave": BraveSearch,
}

DEFAULT_ENGINE = "duckduckgo"


def quick_search(
    query: str,
    engine: str = DEFAULT_ENGINE,
    num_results: int = 10,
    language: Optional[str] = None,
    country: Optional[str] = None,
    cache: Optional[CacheInterface] = None,
    scraper_api_key: Optional[str] = None
) -> List[SearchResult]:
    """
    Fungsi shortcut untuk pencarian cepat dalam 1 baris.
    
    Args:
        query: Kata kunci pencarian
        engine: Nama mesin pencari ('google', 'bing', 'duckduckgo', 'yahoo', 'mojeek', 'brave')
        num_results: Jumlah hasil yang diinginkan (default: 10)
        language: Kode bahasa (contoh: 'id', 'en')
        country: Kode negara (contoh: 'ID', 'US')
        cache: Instance cache (opsional)
        scraper_api_key: API key untuk ScraperAPI (diperlukan untuk Google)
        
    Returns:
        List[SearchResult]: Daftar hasil pencarian
        
    Contoh:
        >>> results = quick_search("Python tutorial")
        >>> results = quick_search("machine learning", engine="brave", num_results=5)
        >>> results = quick_search("AI news", engine="google", scraper_api_key="YOUR_KEY")
    """
    engine_lower = engine.lower()
    
    if engine_lower not in ENGINES:
        available = ", ".join(ENGINES.keys())
        raise ValueError(f"Engine '{engine}' tidak dikenal. Pilihan: {available}")
    
    engine_class = ENGINES[engine_lower]
    
    search_engine = engine_class(
        cache=cache,
        scraper_api_key=scraper_api_key,
        delay=1.0
    )
    
    return search_engine.search(
        query=query,
        num_results=num_results,
        language=language,
        country=country
    )


class SearchAllResult:
    """Hasil dari search_all_engines dengan info error per engine"""
    
    def __init__(self):
        self.results: Dict[str, List[SearchResult]] = {}
        self.errors: Dict[str, Exception] = {}
    
    def has_errors(self) -> bool:
        """Cek apakah ada error"""
        return len(self.errors) > 0
    
    def successful_engines(self) -> List[str]:
        """Daftar engine yang berhasil"""
        return list(self.results.keys())
    
    def failed_engines(self) -> List[str]:
        """Daftar engine yang gagal"""
        return list(self.errors.keys())
    
    def __iter__(self):
        """Iterasi hasil seperti dictionary"""
        return iter(self.results.items())
    
    def items(self):
        """Kompatibel dengan dict.items()"""
        return self.results.items()


def search_all_engines(
    query: str,
    engines: Optional[List[str]] = None,
    num_results: int = 5,
    language: Optional[str] = None,
    country: Optional[str] = None,
    cache: Optional[CacheInterface] = None,
    scraper_api_key: Optional[str] = None,
    parallel: bool = True,
    raise_on_error: bool = False
) -> SearchAllResult:
    """
    Pencarian di multiple engines sekaligus.
    
    Args:
        query: Kata kunci pencarian
        engines: List nama engine (default: semua engine kecuali Google)
        num_results: Jumlah hasil per engine (default: 5)
        language: Kode bahasa
        country: Kode negara
        cache: Instance cache
        scraper_api_key: API key ScraperAPI (untuk Google/Bing)
        parallel: Jalankan pencarian paralel (default: True)
        raise_on_error: Raise exception jika ada error (default: False)
        
    Returns:
        SearchAllResult: Object dengan .results (Dict hasil) dan .errors (Dict error)
        
    Contoh:
        >>> result = search_all_engines("Python")
        >>> for engine, items in result.items():
        ...     print(f"{engine}: {len(items)} hasil")
        
        >>> # Cek error
        >>> if result.has_errors():
        ...     for engine, error in result.errors.items():
        ...         print(f"{engine} gagal: {error}")
        
        >>> results = search_all_engines("AI", engines=["duckduckgo", "brave"])
    """
    if engines is None:
        engines = ["duckduckgo", "yahoo", "mojeek", "brave"]
    
    search_result = SearchAllResult()
    
    def search_single(engine_name: str) -> tuple:
        try:
            engine_results = quick_search(
                query=query,
                engine=engine_name,
                num_results=num_results,
                language=language,
                country=country,
                cache=cache,
                scraper_api_key=scraper_api_key
            )
            return (engine_name, engine_results, None)
        except Exception as e:
            return (engine_name, [], e)
    
    if parallel and len(engines) > 1:
        with ThreadPoolExecutor(max_workers=len(engines)) as executor:
            futures = {executor.submit(search_single, eng): eng for eng in engines}
            for future in as_completed(futures):
                engine_name, engine_results, error = future.result()
                if error:
                    search_result.errors[engine_name] = error
                    if raise_on_error:
                        raise error
                else:
                    search_result.results[engine_name] = engine_results
    else:
        for engine_name in engines:
            _, engine_results, error = search_single(engine_name)
            if error:
                search_result.errors[engine_name] = error
                if raise_on_error:
                    raise error
            else:
                search_result.results[engine_name] = engine_results
    
    return search_result


def get_available_engines() -> List[str]:
    """
    Mendapatkan daftar engine yang tersedia.
    
    Returns:
        List[str]: Daftar nama engine
        
    Contoh:
        >>> engines = get_available_engines()
        >>> print(engines)
        ['google', 'bing', 'duckduckgo', 'yahoo', 'mojeek', 'brave']
    """
    return list(ENGINES.keys())


def visit_url(
    url: str,
    timeout: int = 30,
    user_agent: Optional[str] = None
):
    """
    Kunjungi URL dan ambil konten halaman.
    
    Args:
        url: URL yang akan dikunjungi
        timeout: Timeout dalam detik (default: 30)
        user_agent: Custom user agent (opsional)
        
    Returns:
        PageContent: Object berisi konten halaman
        
    Contoh:
        >>> page = visit_url("https://python.org")
        >>> print(page.title)
        >>> print(page.text[:500])
        
        >>> # Dengan timeout custom
        >>> page = visit_url("https://example.com", timeout=10)
    """
    from .base import PageContent
    import requests
    from bs4 import BeautifulSoup
    
    default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    headers = {
        "User-Agent": user_agent or default_ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        text = ' '.join(soup.get_text(separator=' ').split())
        
        return PageContent(
            url=url,
            title=title,
            text=text,
            html=response.text,
            status_code=response.status_code,
            success=True
        )
    except requests.exceptions.Timeout:
        return PageContent(
            url=url, title="", text="", html="",
            status_code=0, success=False, error=f"Timeout setelah {timeout}s"
        )
    except requests.exceptions.RequestException as e:
        return PageContent(
            url=url, title="", text="", html="",
            status_code=0, success=False, error=str(e)
        )
