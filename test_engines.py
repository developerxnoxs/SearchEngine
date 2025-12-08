"""
Test Script untuk Search Engines - Tanpa Proxy vs Dengan ScraperAPI
"""

import time
from multi_search_engine import (
    GoogleSearch,
    BingSearch,
    DuckDuckGoSearch,
    YahooSearch,
    MojeekSearch,
    BraveSearch
)
from multi_search_engine.exceptions import BlockedException, NetworkException, ParseException

SCRAPER_API_KEY = "1820c54a47ebf6d3557d9be57aa70c81"

TEST_QUERY = "Python programming"
NUM_RESULTS = 5

ENGINES = [
    ("Google", GoogleSearch),
    ("Bing", BingSearch),
    ("DuckDuckGo", DuckDuckGoSearch),
    ("Yahoo", YahooSearch),
    ("Mojeek", MojeekSearch),
    ("Brave", BraveSearch),
]


def print_separator(title):
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_results(results, max_display=3):
    """Print hasil pencarian"""
    if not results:
        print("   Tidak ada hasil ditemukan")
        return
    
    print(f"   Ditemukan {len(results)} hasil:")
    for i, result in enumerate(results[:max_display], 1):
        title = result.title[:60] + "..." if len(result.title) > 60 else result.title
        print(f"   {i}. {title}")
        print(f"      URL: {result.url[:70]}...")
    
    if len(results) > max_display:
        print(f"   ... dan {len(results) - max_display} hasil lainnya")


def test_engine_without_proxy(name, engine_class):
    """Test engine tanpa proxy"""
    print(f"\n   [{name}] Tanpa Proxy...")
    
    try:
        engine = engine_class(delay=1.0, timeout=30)
        start_time = time.time()
        results = engine.search(TEST_QUERY, num_results=NUM_RESULTS, use_cache=False)
        elapsed = time.time() - start_time
        
        print(f"   Status: SUCCESS ({elapsed:.2f}s)")
        print_results(results)
        return {"status": "success", "count": len(results), "time": elapsed}
        
    except BlockedException as e:
        print(f"   Status: BLOCKED - {e}")
        return {"status": "blocked", "error": str(e)}
        
    except NetworkException as e:
        print(f"   Status: NETWORK ERROR - {e}")
        return {"status": "network_error", "error": str(e)}
        
    except ParseException as e:
        print(f"   Status: PARSE ERROR - {e}")
        return {"status": "parse_error", "error": str(e)}
        
    except Exception as e:
        print(f"   Status: ERROR - {e}")
        return {"status": "error", "error": str(e)}


def test_engine_with_scraper_api(name, engine_class):
    """Test engine dengan ScraperAPI"""
    print(f"\n   [{name}] Dengan ScraperAPI...")
    
    try:
        engine = engine_class(
            delay=0.5,
            timeout=60,
            scraper_api_key=SCRAPER_API_KEY
        )
        start_time = time.time()
        results = engine.search(TEST_QUERY, num_results=NUM_RESULTS, use_cache=False)
        elapsed = time.time() - start_time
        
        print(f"   Status: SUCCESS ({elapsed:.2f}s)")
        print_results(results)
        return {"status": "success", "count": len(results), "time": elapsed}
        
    except BlockedException as e:
        print(f"   Status: BLOCKED - {e}")
        return {"status": "blocked", "error": str(e)}
        
    except NetworkException as e:
        print(f"   Status: NETWORK ERROR - {e}")
        return {"status": "network_error", "error": str(e)}
        
    except ParseException as e:
        print(f"   Status: PARSE ERROR - {e}")
        return {"status": "parse_error", "error": str(e)}
        
    except Exception as e:
        print(f"   Status: ERROR - {e}")
        return {"status": "error", "error": str(e)}


def main():
    print()
    print("*" * 70)
    print("*  SEARCH ENGINE TEST: Tanpa Proxy vs Dengan ScraperAPI")
    print("*" * 70)
    print(f"\nQuery: '{TEST_QUERY}'")
    print(f"Jumlah hasil: {NUM_RESULTS}")
    print(f"ScraperAPI Key: {SCRAPER_API_KEY[:20]}...")
    
    results_without_proxy = {}
    results_with_proxy = {}
    
    print_separator("TEST 1: TANPA PROXY")
    print("\nMenguji semua engine tanpa menggunakan proxy...")
    
    for name, engine_class in ENGINES:
        results_without_proxy[name] = test_engine_without_proxy(name, engine_class)
        time.sleep(1)
    
    print_separator("TEST 2: DENGAN SCRAPERAPI PROXY")
    print("\nMenguji semua engine dengan ScraperAPI proxy...")
    
    for name, engine_class in ENGINES:
        results_with_proxy[name] = test_engine_with_scraper_api(name, engine_class)
        time.sleep(1)
    
    print_separator("RINGKASAN HASIL")
    
    print("\n{:<15} {:<25} {:<25}".format("Engine", "Tanpa Proxy", "Dengan ScraperAPI"))
    print("-" * 65)
    
    for name, _ in ENGINES:
        no_proxy = results_without_proxy.get(name, {})
        with_proxy = results_with_proxy.get(name, {})
        
        no_proxy_status = no_proxy.get("status", "N/A")
        if no_proxy_status == "success":
            no_proxy_str = f"OK ({no_proxy.get('count', 0)} hasil, {no_proxy.get('time', 0):.1f}s)"
        else:
            no_proxy_str = no_proxy_status.upper()
        
        with_proxy_status = with_proxy.get("status", "N/A")
        if with_proxy_status == "success":
            with_proxy_str = f"OK ({with_proxy.get('count', 0)} hasil, {with_proxy.get('time', 0):.1f}s)"
        else:
            with_proxy_str = with_proxy_status.upper()
        
        print("{:<15} {:<25} {:<25}".format(name, no_proxy_str, with_proxy_str))
    
    print()
    print("*" * 70)
    print("*  TEST SELESAI")
    print("*" * 70)
    print()


if __name__ == "__main__":
    main()
