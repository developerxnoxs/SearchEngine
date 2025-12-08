"""
Rate Limiter untuk Multi Search Engine Library
"""

import time
from threading import Lock
from typing import Optional


class RateLimiter:
    """
    Rate limiter dengan auto-backoff untuk menghindari blocking
    """
    
    def __init__(
        self,
        requests_per_minute: int = 10,
        min_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        """
        Inisialisasi RateLimiter
        
        Args:
            requests_per_minute: Maksimum request per menit
            min_delay: Delay minimum antar request (detik)
            max_delay: Delay maksimum saat backoff (detik)
            backoff_factor: Faktor pengali untuk backoff
        """
        self.requests_per_minute = requests_per_minute
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        
        self._current_delay = min_delay
        self._last_request_time = 0
        self._request_count = 0
        self._window_start = time.time()
        self._lock = Lock()
    
    def wait(self):
        """Tunggu sebelum melakukan request berikutnya"""
        with self._lock:
            current_time = time.time()
            
            if current_time - self._window_start >= 60:
                self._window_start = current_time
                self._request_count = 0
                self._current_delay = self.min_delay
            
            if self._request_count >= self.requests_per_minute:
                wait_time = 60 - (current_time - self._window_start)
                if wait_time > 0:
                    time.sleep(wait_time)
                self._window_start = time.time()
                self._request_count = 0
            
            elapsed = current_time - self._last_request_time
            if elapsed < self._current_delay:
                time.sleep(self._current_delay - elapsed)
            
            self._last_request_time = time.time()
            self._request_count += 1
    
    def backoff(self):
        """Meningkatkan delay setelah terkena rate limit"""
        with self._lock:
            self._current_delay = min(
                self._current_delay * self.backoff_factor,
                self.max_delay
            )
    
    def reset(self):
        """Reset rate limiter ke kondisi awal"""
        with self._lock:
            self._current_delay = self.min_delay
            self._request_count = 0
            self._window_start = time.time()
            self._last_request_time = 0
    
    @property
    def current_delay(self) -> float:
        """Get delay saat ini"""
        return self._current_delay
    
    @property
    def remaining_requests(self) -> int:
        """Get sisa request yang tersedia dalam window saat ini"""
        with self._lock:
            current_time = time.time()
            if current_time - self._window_start >= 60:
                return self.requests_per_minute
            return max(0, self.requests_per_minute - self._request_count)
