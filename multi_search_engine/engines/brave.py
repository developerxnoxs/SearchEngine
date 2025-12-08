"""
Brave Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class BraveSearch(SearchEngine):
    """
    Brave Search Engine
    
    Berfungsi dengan baik tanpa proxy.
    Brave adalah mesin pencari yang fokus pada privasi.
    """
    
    ENGINE_NAME = "brave"
    BASE_URL = "https://search.brave.com/search"
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build Brave search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "q": query,
            "offset": start,
            "count": num_results,
        }
        
        if language:
            params["lang"] = language
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse Brave search results - sama seperti PHP"""
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            nodes = soup.select('div.snippet[data-type="web"]')
            
            for node in nodes:
                a_node = node.select_one('a[href][class*="svelte"]')
                
                title_node = node.select_one('div.title.search-snippet-title')
                if not title_node:
                    title_node = node.select_one('div[class*="title"]')
                
                desc_node = node.select_one('div.content.desktop-default-regular')
                if not desc_node:
                    desc_node = node.select_one('div[class*="generic-snippet"]')
                if not desc_node:
                    desc_node = node.select_one('div[class*="snippet-description"]')
                
                if not a_node:
                    continue
                
                url = a_node.get('href', '')
                
                if not url or url.startswith('#') or 'brave.com' in url:
                    continue
                
                title = title_node.get_text(strip=True) if title_node else ''
                description = desc_node.get_text(strip=True) if desc_node else ''
                
                if title and url:
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        description=description
                    ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse Brave results: {str(e)}")
        
        return results
