# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation

## [1.0.0] - 2024-12-08

### Added
- Support for 6 search engines: Google, Bing, DuckDuckGo, Yahoo, Mojeek, Brave
- ScraperAPI integration for bypassing bot protection
- File-based and memory-based caching
- Rate limiting with exponential backoff
- Result filtering by keyword and domain
- JSON export functionality
- Blocked page detection
- Comprehensive error handling

### Search Engines
- **GoogleSearch** - Requires ScraperAPI for reliable results
- **BingSearch** - Works with or without proxy
- **DuckDuckGoSearch** - Works without proxy (recommended)
- **YahooSearch** - Works without proxy
- **MojeekSearch** - Works without proxy
- **BraveSearch** - Works without proxy

### Features
- `SearchResult` dataclass with position, engine, and extra fields
- `FileCache` for persistent caching to disk
- `MemoryCache` for in-memory caching
- `RateLimiter` for controlling request rates
- Custom exceptions: `NetworkException`, `ParseException`, `BlockedException`
