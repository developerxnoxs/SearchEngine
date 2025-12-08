# Multi Search Engine

[![PyPI version](https://badge.fury.io/py/multi-search-engine.svg)](https://badge.fury.io/py/multi-search-engine)
[![Python Versions](https://img.shields.io/pypi/pyversions/multi-search-engine.svg)](https://pypi.org/project/multi-search-engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/yourusername/multi-search-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/multi-search-engine/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/multi-search-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/multi-search-engine)
[![Downloads](https://pepy.tech/badge/multi-search-engine)](https://pepy.tech/project/multi-search-engine)

Library Python yang powerful untuk melakukan pencarian di berbagai mesin pencari dengan interface yang seragam. Mendukung Google, Bing, DuckDuckGo, Yahoo, Mojeek, dan Brave dengan fitur caching, rate limiting, dan dukungan proxy.

## Fitur

- **6 Mesin Pencari**: Google, Bing, DuckDuckGo, Yahoo, Mojeek, Brave
- **Interface Seragam**: API yang sama untuk semua mesin pencari
- **Caching**: Cache berbasis file dan memory
- **Rate Limiting**: Rate limiter bawaan dengan exponential backoff
- **Dukungan Proxy**: Bekerja dengan proxy kustom dan ScraperAPI
- **Filter Hasil**: Filter berdasarkan kata kunci, domain, atau batasi jumlah
- **Opsi Export**: Export ke JSON atau format dictionary
- **Type Hints**: Anotasi tipe lengkap untuk dukungan IDE yang lebih baik
- **Penanganan Error**: Exception handling yang komprehensif

## Instalasi

```bash
pip install multi-search-engine
```

## Memulai Cepat

```python
from multi_search_engine import DuckDuckGoSearch

# Buat instance search engine
ddg = DuckDuckGoSearch()

# Lakukan pencarian
results = ddg.search("Python programming", num_results=10)

# Proses hasil
for result in results:
    print(f"Judul: {result.title}")
    print(f"URL: {result.url}")
    print(f"Deskripsi: {result.description}")
    print()
```

## Mesin Pencari yang Didukung

| Engine | Class | Tanpa Proxy | Dengan ScraperAPI | Rekomendasi |
|--------|-------|-------------|-------------------|-------------|
| DuckDuckGo | `DuckDuckGoSearch` | Stabil | Stabil | Langsung (tanpa proxy) |
| Yahoo | `YahooSearch` | Stabil | Stabil | Langsung (tanpa proxy) |
| Mojeek | `MojeekSearch` | Stabil | Stabil | Langsung (tanpa proxy) |
| Brave | `BraveSearch` | Stabil | Stabil | Langsung (tanpa proxy) |
| Bing | `BingSearch` | Mungkin perlu captcha | OK | Gunakan ScraperAPI |
| Google | `GoogleSearch` | Diblokir | OK | ScraperAPI diperlukan |

> **Catatan:** Google dan Bing aktif memblokir permintaan otomatis. Gunakan ScraperAPI untuk hasil yang andal.

## Contoh Penggunaan

### Pencarian Dasar

```python
from multi_search_engine import DuckDuckGoSearch, BingSearch, GoogleSearch

# DuckDuckGo (tanpa proxy)
ddg = DuckDuckGoSearch()
results = ddg.search("Python programming", num_results=10)

# Dengan parameter pencarian
results = ddg.search(
    query="machine learning",
    page=1,
    num_results=10,
    language="id",
    country="ID",
    safe_search=True
)
```

### Menggunakan ScraperAPI (untuk Google/Bing)

```python
from multi_search_engine import GoogleSearch

google = GoogleSearch(scraper_api_key="API_KEY_ANDA")
results = google.search("Python programming")

for result in results:
    print(f"{result.title}: {result.url}")
```

### Caching Hasil

```python
from multi_search_engine import DuckDuckGoSearch, FileCache, MemoryCache

# Cache berbasis file (persisten)
file_cache = FileCache(cache_dir=".search_cache", default_ttl=3600)
ddg = DuckDuckGoSearch(cache=file_cache)

# Cache memory (hanya sesi)
mem_cache = MemoryCache(default_ttl=600)
ddg = DuckDuckGoSearch(cache=mem_cache)

# Hasil otomatis di-cache
results = ddg.search("Tutorial Python")
```

### Rate Limiting

```python
from multi_search_engine import BingSearch, RateLimiter

limiter = RateLimiter(
    requests_per_minute=10,
    min_delay=1.0,
    max_delay=60.0
)

bing = BingSearch(rate_limiter=limiter)
results = bing.search("web development")
```

### Menggunakan Proxy Kustom

```python
from multi_search_engine import YahooSearch

yahoo = YahooSearch(proxy="http://proxy.example.com:8080")
results = yahoo.search("berita teknologi")
```

### Filter Hasil

```python
from multi_search_engine import BraveSearch

brave = BraveSearch()
results = brave.search("tutorial programming", num_results=20)

# Filter berdasarkan kata kunci
python_results = brave.filter_by_keyword("python")

# Filter berdasarkan domain
github_results = brave.filter_by_domain("github.com")

# Batasi hasil
top_5 = brave.limit_results(5)
```

### Export Hasil

```python
from multi_search_engine import DuckDuckGoSearch

ddg = DuckDuckGoSearch()
results = ddg.search("data science")

# Export ke list of dictionaries
data = ddg.to_dict_list()

# Export ke JSON string
json_str = ddg.to_json(indent=2)

# Simpan ke file
with open("results.json", "w") as f:
    f.write(ddg.to_json())
```

### Penanganan Error

```python
from multi_search_engine import (
    DuckDuckGoSearch,
    NetworkException,
    ParseException,
    BlockedException
)

ddg = DuckDuckGoSearch()

try:
    results = ddg.search("query")
except NetworkException as e:
    print(f"Error jaringan: {e}")
except ParseException as e:
    print(f"Gagal parsing hasil: {e}")
except BlockedException as e:
    print(f"Diblokir oleh mesin pencari: {e}")
```

## Referensi API

### Parameter SearchEngine

| Parameter | Tipe | Default | Deskripsi |
|-----------|------|---------|-----------|
| `user_agent` | str | Random | String user agent kustom |
| `proxy` | str | None | URL Proxy |
| `timeout` | int | 30 | Timeout request dalam detik |
| `delay` | float | 1.0 | Delay antar request |
| `cache` | CacheInterface | None | Instance cache |
| `rate_limiter` | RateLimiter | None | Instance rate limiter |
| `scraper_api_key` | str | None | API key ScraperAPI |

### Parameter Method Search

| Parameter | Tipe | Default | Deskripsi |
|-----------|------|---------|-----------|
| `query` | str | Wajib | Query pencarian |
| `page` | int | 1 | Nomor halaman |
| `num_results` | int | 10 | Hasil per halaman |
| `language` | str | None | Kode bahasa (contoh: 'id', 'en') |
| `country` | str | None | Kode negara (contoh: 'ID', 'US') |
| `safe_search` | bool | True | Aktifkan safe search |
| `use_cache` | bool | True | Gunakan hasil cache |

### Properti SearchResult

| Properti | Tipe | Deskripsi |
|----------|------|-----------|
| `title` | str | Judul hasil |
| `url` | str | URL hasil |
| `description` | str | Deskripsi/snippet hasil |
| `position` | int | Posisi dalam hasil pencarian |
| `engine` | str | Nama mesin pencari |
| `extra` | dict | Metadata tambahan |

## Struktur Proyek

```
multi-search-engine/
├── multi_search_engine/
│   ├── __init__.py
│   ├── base.py              # Base class dan SearchResult
│   ├── cache.py             # FileCache dan MemoryCache
│   ├── rate_limiter.py      # RateLimiter
│   ├── exceptions.py        # Custom exceptions
│   └── engines/
│       ├── __init__.py
│       ├── google.py
│       ├── bing.py
│       ├── duckduckgo.py
│       ├── yahoo.py
│       ├── mojeek.py
│       └── brave.py
├── tests/
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Kontribusi

Kontribusi sangat diterima! Silakan baca [Panduan Kontribusi](CONTRIBUTING.md) untuk detail tentang cara mengirim pull request, melaporkan masalah, dan berkontribusi pada proyek.

## Keamanan

Untuk masalah keamanan, silakan baca [Kebijakan Keamanan](SECURITY.md).

## Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## Changelog

Lihat [CHANGELOG.md](CHANGELOG.md) untuk daftar perubahan.

## Ucapan Terima Kasih

- Terima kasih kepada semua kontributor
- Terinspirasi dari kebutuhan akan interface pencarian yang seragam
- Dibangun dengan Python dan cinta
