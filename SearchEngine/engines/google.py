"""
Google Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
import re

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class GoogleSearch(SearchEngine):
    """
    Google Search Engine
    
    PENTING: Google memerlukan ScraperAPI untuk bypass proteksi bot.
    Tanpa ScraperAPI, kemungkinan besar akan di-block.
    """
    
    ENGINE_NAME = "google"
    BASE_URL = "https://www.google.com/search"
    
    def _get_headers(self):
        """Override headers untuk Google - tambahkan consent cookie"""
        headers = super()._get_headers()
        headers["Cookie"] = "CONSENT=PENDING+987; SOCS=CAESHAgBEhIaAB"
        return headers
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build Google search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "q": query,
            "num": num_results + 2,
            "start": start,
            "safe": "active",
        }
        
        if language:
            params["hl"] = language
        
        if country:
            params["gl"] = country
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse Google search results - sama seperti PHP"""
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            blocks = soup.select('div.MjjYud')
            
            if not blocks:
                blocks = soup.select('div.ezO2md')
            
            for block in blocks:
                link_container = block.select_one('div.yuRUbf a[href]')
                if not link_container:
                    link_container = block.select_one('a[href]')
                
                title_elem = block.select_one('h3.LC20lb')
                if not title_elem:
                    title_elem = block.select_one('a span.CVA68e')
                
                desc_elem = block.select_one('div.VwiC3b')
                if not desc_elem:
                    desc_elem = block.select_one('span.FrIlee')
                
                if not link_container or not title_elem:
                    continue
                
                href = link_container.get('href', '')
                
                if href.startswith('/url?'):
                    parts = href.replace('/url?q=', '').split('&')
                    link = unquote(parts[0]) if parts else href
                elif href.startswith('http'):
                    link = href
                else:
                    continue
                
                if not re.match(r'^https?://', link):
                    continue
                
                if 'google.com' in link:
                    continue
                
                title = title_elem.get_text(strip=True)
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                if title and link:
                    results.append(SearchResult(
                        title=title,
                        url=link,
                        description=description
                    ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse Google results: {str(e)}")
        
        return results
