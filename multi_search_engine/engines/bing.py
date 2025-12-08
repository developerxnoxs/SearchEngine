"""
Bing Search Engine Implementation
Mengikuti logika dari PHP: https://github.com/developerxnoxs/multi-search-engine
"""

from typing import Optional, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from ..base import SearchEngine, SearchResult
from ..exceptions import ParseException


class BingSearch(SearchEngine):
    """
    Bing Search Engine
    
    Berfungsi dengan baik tanpa proxy.
    """
    
    ENGINE_NAME = "bing"
    BASE_URL = "https://www.bing.com/search"
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        """Build Bing search URL - sama seperti PHP"""
        start = (page - 1) * num_results
        params = {
            "q": query,
            "first": start + 1,
            "count": num_results + 2,
        }
        
        if language:
            params["setlang"] = language
        
        if country:
            params["cc"] = country
        
        return f"{self.BASE_URL}?{urlencode(params)}"
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        """Parse Bing search results - sama seperti PHP
        
        PHP menggunakan XPath: //li[@class="b_algo"]
        Lalu .//h2/a untuk link dan .//div[@class="b_caption"]/p untuk deskripsi
        
        Tapi deskripsi bersifat opsional - jika tidak ada, tetap terima hasilnya
        """
        results = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            blocks = soup.select('li.b_algo')
            
            for block in blocks:
                a = block.select_one('h2 a')
                
                if not a:
                    continue
                
                url = a.get('href', '')
                title = a.get_text(strip=True)
                
                description = ""
                desc = block.select_one('div.b_caption p')
                if desc:
                    description = desc.get_text(strip=True)
                else:
                    caption = block.select_one('div.b_caption')
                    if caption:
                        description = caption.get_text(strip=True)
                    else:
                        p_elem = block.select_one('p')
                        if p_elem:
                            description = p_elem.get_text(strip=True)
                
                if title and url:
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        description=description
                    ))
            
        except Exception as e:
            raise ParseException(f"Failed to parse Bing results: {str(e)}")
        
        return results
