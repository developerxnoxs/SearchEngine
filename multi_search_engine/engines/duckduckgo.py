"""
DuckDuckGo Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
import re

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class DuckDuckGoSearch(SearchEngine):
    """
    DuckDuckGo Search Engine
    
    Berfungsi dengan baik tanpa proxy. Direkomendasikan untuk penggunaan langsung.
    """
    
    ENGINE_NAME = "duckduckgo"
    BASE_URL = "https://html.duckduckgo.com/html/"
    
    AD_PATTERNS = [
        'duckduckgo.com/y.js',
        'ad_domain=',
        'ad_provider=',
        'ad_type=',
    ]
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build DuckDuckGo search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "q": query,
            "s": start,
        }
        
        if country:
            params["kl"] = country.lower()
        
        if language:
            params["lang"] = language
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _extract_real_url(self, ddg_redirect: str) -> str:
        """Extract real URL dari DuckDuckGo redirect - sama seperti PHP"""
        match = re.search(r'uddg=([^&]+)', ddg_redirect)
        if match:
            decoded = unquote(match.group(1))
            if re.match(r'^https?://', decoded):
                return decoded
        
        if ddg_redirect.startswith('//'):
            return 'https:' + ddg_redirect
        
        return ddg_redirect
    
    def _is_ad_url(self, url: str) -> bool:
        """Check apakah URL adalah iklan - sama seperti PHP"""
        for pattern in self.AD_PATTERNS:
            if pattern in url:
                return True
        return False
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse DuckDuckGo search results - sama seperti PHP
        
        PHP menggunakan XPath: //a[contains(@class,"result__a")]
        Dan mencari snippet dengan: ../following-sibling::div[contains(@class,"result__snippet")]
        """
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            links = soup.select('a.result__a')
            
            for a in links:
                href = a.get('href', '')
                url = self._extract_real_url(href)
                
                if self._is_ad_url(url) or self._is_ad_url(href):
                    continue
                
                title = a.get_text(strip=True)
                
                description = ""
                result_container = a.find_parent('div', class_=lambda x: x and 'result' in x)
                if result_container:
                    desc_elem = result_container.find('a', class_=lambda x: x and 'result__snippet' in str(x))
                    if not desc_elem:
                        desc_elem = result_container.find('div', class_=lambda x: x and 'result__snippet' in str(x))
                    if not desc_elem:
                        desc_elem = result_container.find(class_=lambda x: x and 'snippet' in str(x))
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                
                if not url or not re.match(r'^https?://', url):
                    continue
                
                if title and url:
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        description=description
                    ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse DuckDuckGo results: {str(e)}")
        
        return results
