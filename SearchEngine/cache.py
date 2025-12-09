"""
Caching system untuk Multi Search Engine Library
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import json
import os
import time
import hashlib


class CacheInterface(ABC):
    """Interface untuk cache"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value dari cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value ke cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Hapus key dari cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Hapus semua cache"""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """Cek apakah key ada di cache"""
        pass


class FileCache(CacheInterface):
    """File-based cache implementation"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 3600):
        """
        Inisialisasi FileCache
        
        Args:
            cache_dir: Direktori untuk menyimpan file cache
            default_ttl: Time-to-live default dalam detik (default: 1 jam)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Pastikan direktori cache ada"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """Get path file cache untuk key tertentu"""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value dari cache"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if data.get("expires_at") and data["expires_at"] < time.time():
                self.delete(key)
                return None
            
            return data.get("value")
            
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value ke cache"""
        cache_path = self._get_cache_path(key)
        ttl = ttl if ttl is not None else self.default_ttl
        
        data = {
            "key": key,
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl if ttl > 0 else None
        }
        
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def delete(self, key: str) -> bool:
        """Hapus key dari cache"""
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except IOError:
                return False
        return False
    
    def clear(self) -> bool:
        """Hapus semua cache"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except IOError:
            return False
    
    def has(self, key: str) -> bool:
        """Cek apakah key ada di cache"""
        return self.get(key) is not None
    
    def cleanup_expired(self) -> int:
        """Hapus cache yang sudah expired, return jumlah yang dihapus"""
        deleted = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.cache_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if data.get("expires_at") and data["expires_at"] < time.time():
                        os.remove(filepath)
                        deleted += 1
        except (IOError, json.JSONDecodeError):
            pass
        
        return deleted


class MemoryCache(CacheInterface):
    """In-memory cache implementation"""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Inisialisasi MemoryCache
        
        Args:
            default_ttl: Time-to-live default dalam detik
            max_size: Maksimum jumlah item di cache
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value dari cache"""
        if key not in self._cache:
            return None
        
        data = self._cache[key]
        if data.get("expires_at") and data["expires_at"] < time.time():
            self.delete(key)
            return None
        
        return data.get("value")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value ke cache"""
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl if ttl > 0 else None
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Hapus key dari cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Hapus semua cache"""
        self._cache.clear()
        return True
    
    def has(self, key: str) -> bool:
        """Cek apakah key ada di cache"""
        return self.get(key) is not None
    
    def _evict_oldest(self):
        """Hapus item cache paling lama"""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].get("created_at", 0)
        )
        del self._cache[oldest_key]
