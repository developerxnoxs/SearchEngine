# xnoxs-dork

SQL Injection Vulnerability Scanner menggunakan library `xnoxs-engine`.

## ⚠️ DISCLAIMER

**Tools ini hanya untuk tujuan riset keamanan dan edukasi.**

- Hanya gunakan pada website yang Anda miliki
- Atau website yang Anda memiliki izin tertulis untuk diuji
- Penggunaan tanpa izin adalah ilegal dan melanggar hukum

## Instalasi

### Di Termux / Linux / Windows

```bash
pip install xnoxs-engine requests
```

### Clone dan jalankan

```bash
git clone <repo-url>
cd xnoxs-dork
python xnoxs_dork.py
```

## Fitur

- Pencarian URL dengan Google Dorks via DuckDuckGo, Brave, Mojeek
- Deteksi error SQL dari berbagai database:
  - MySQL
  - PostgreSQL  
  - MSSQL
  - Oracle
  - SQLite
- Test single URL atau scan domain
- Delay otomatis untuk menghindari rate limiting

## Penggunaan

### Sebagai CLI

```bash
python xnoxs_dork.py
```

Pilih opsi:
1. Scan dengan custom dork
2. Scan specific domain
3. Test single URL

### Sebagai Library

```python
from xnoxs_dork import SQLiScanner

scanner = SQLiScanner(delay=2.0)

# Test single URL
results = scanner.test_url("http://example.com/page.php?id=1")

# Scan dengan dork
results = scanner.scan_dork("inurl:id=", num_results=10)

# Scan domain
results = scanner.scan_domain("example.com")

# Lihat hasil vulnerable
vulnerable = scanner.get_vulnerable_urls()
for v in vulnerable:
    print(f"URL: {v.url}")
    print(f"Parameter: {v.parameter}")
    print(f"DB Type: {v.error_type}")
```

## Cara Kerja

1. **Pencarian**: Menggunakan `xnoxs-engine` untuk mencari URL dengan parameter
2. **Injeksi**: Menambahkan payload `'` di akhir parameter
3. **Deteksi**: Menganalisis response untuk error SQL patterns
4. **Report**: Melaporkan URL yang vulnerable

## SQL Error Patterns

Tools ini mendeteksi error patterns dari:

| Database | Contoh Error |
|----------|--------------|
| MySQL | `SQL syntax.*MySQL`, `Warning.*mysql_` |
| PostgreSQL | `PostgreSQL.*ERROR`, `Warning.*pg_` |
| MSSQL | `SQL Server.*Driver`, `OLE DB.* SQL Server` |
| Oracle | `ORA-[0-9]{4}`, `Oracle error` |
| SQLite | `SQLite.*Exception`, `Warning.*sqlite_` |

## License

MIT License - Untuk tujuan riset dan edukasi saja.
