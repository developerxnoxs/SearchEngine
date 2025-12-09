"""
Mojeek Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class MojeekSearch(SearchEngine):
    """
    Mojeek Search Engine
    
    Berfungsi dengan baik tanpa proxy. 
    Mojeek adalah mesin pencari independen yang tidak menggunakan hasil dari Google atau Bing.
    """
    
    ENGINE_NAME = "mojeek"
    BASE_URL = "https://www.mojeek.com/search"
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build Mojeek search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "q": query,
            "s": start,
        }
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse Mojeek search results - sama seperti PHP"""
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            blocks = soup.select('div[class*="result"]')
            
            for block in blocks:
                a = block.select_one('a')
                desc = block.select_one('p')
                
                if not a:
                    continue
                
                url = a.get('href', '')
                title = a.get_text(strip=True)
                description = desc.get_text(strip=True) if desc else ''
                
                if title and url and url.startswith('http'):
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        description=description
                    ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse Mojeek results: {str(e)}")
        
        return results
