"""
Demo script untuk Multi Search Engine Library
"""

import time
from multi_search_engine import (
    DuckDuckGoSearch,
    MojeekSearch,
    BraveSearch,
    FileCache,
    RateLimiter
)


def demo_basic_search():
    """Demo pencarian dasar"""
    print("=" * 60)
    print("Multi Search Engine Library - Python Version")
    print("=" * 60)
    print()
    
    print("Demo 1: DuckDuckGo Search (tanpa proxy)")
    print("-" * 40)
    
    ddg = DuckDuckGoSearch(delay=1.0)
    
    try:
        results = ddg.search("Python programming", num_results=5)
        print(f"Ditemukan {len(results)} hasil:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Desc: {result.description[:100]}..." if len(result.description) > 100 else f"   Desc: {result.description}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def demo_with_cache():
    """Demo dengan caching"""
    print("Demo 2: Pencarian dengan Cache")
    print("-" * 40)
    
    cache = FileCache(cache_dir=".search_cache", default_ttl=3600)
    
    ddg = DuckDuckGoSearch(cache=cache, delay=2.0)
    
    try:
        print("Pencarian pertama (dari web)...")
        results = ddg.search("machine learning", num_results=3)
        print(f"Ditemukan {len(results)} hasil")
        
        print("\nPencarian kedua (dari cache)...")
        results = ddg.search("machine learning", num_results=3)
        print(f"Ditemukan {len(results)} hasil (dari cache)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def demo_filter():
    """Demo filter hasil"""
    print("Demo 3: Filter Hasil Pencarian")
    print("-" * 40)
    
    mojeek = MojeekSearch(delay=1.0)
    
    try:
        results = mojeek.search("web development tutorial", num_results=10)
        print(f"Total hasil: {len(results)}")
        
        filtered = mojeek.filter_by_keyword("javascript")
        print(f"Hasil dengan 'javascript': {len(filtered)}")
        
        limited = mojeek.limit_results(3)
        print(f"Dibatasi 3 hasil: {len(limited)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def demo_export():
    """Demo export ke JSON"""
    print("Demo 4: Export ke JSON")
    print("-" * 40)
    
    brave = BraveSearch(delay=1.0)
    
    try:
        results = brave.search("artificial intelligence", num_results=3)
        
        json_output = brave.to_json(indent=2)
        print("JSON Output:")
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def main():
    """Main function"""
    print()
    print("Library ini menyediakan interface untuk berbagai search engines:")
    print("- GoogleSearch (memerlukan ScraperAPI)")
    print("- BingSearch (memerlukan ScraperAPI/proxy)")
    print("- DuckDuckGoSearch (tanpa proxy)")
    print("- YahooSearch (tanpa proxy)")
    print("- MojeekSearch (tanpa proxy)")
    print("- BraveSearch (tanpa proxy)")
    print()
    
    demo_basic_search()
    time.sleep(2)
    demo_with_cache()
    time.sleep(2)
    demo_filter()
    time.sleep(2)
    demo_export()
    
    print("=" * 60)
    print("Demo selesai!")
    print("=" * 60)


if __name__ == "__main__":
    main()
