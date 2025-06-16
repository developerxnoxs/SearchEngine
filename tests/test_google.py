from multi_search_engine.google import GoogleSearch

search = GoogleSearch().search("inurl:/admin/login.php", limit=5)

for url in search.urls():
    print(url)
