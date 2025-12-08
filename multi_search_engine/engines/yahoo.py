"""
Yahoo Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
import re

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class YahooSearch(SearchEngine):
    """
    Yahoo Search Engine
    
    Berfungsi dengan baik tanpa proxy.
    """
    
    ENGINE_NAME = "yahoo"
    BASE_URL = "https://search.yahoo.com/search"
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build Yahoo search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "p": query,
            "b": start + 1,
        }
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _extract_real_url(self, yahoo_redirect: str) -> str:
        """Extract real URL dari Yahoo redirect - sama seperti PHP"""
        match = re.search(r'RU=(.*?)/RK=', yahoo_redirect)
        if match:
            return unquote(match.group(1))
        return yahoo_redirect
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse Yahoo search results - sama seperti PHP"""
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            nodes = soup.select('div[class*="algo"]')
            
            for node in nodes:
                link_node = node.select_one('a')
                title_node = node.select_one('h3')
                desc_node = node.select_one('p')
                
                if link_node and title_node:
                    href = link_node.get('href', '')
                    url = self._extract_real_url(href)
                    title = title_node.get_text(strip=True)
                    description = desc_node.get_text(strip=True) if desc_node else ''
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            description=description
                        ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse Yahoo results: {str(e)}")
        
        return results
