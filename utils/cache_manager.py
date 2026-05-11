#!/usr/bin/env python3
"""
CACHE MANAGER
Efficient caching layer for trading system data and calculations
"""

import json
import hashlib
import time
from typing import Any, Dict, Optional, Union, Callable
from pathlib import Path
import logging
from functools import wraps
from datetime import datetime, timedelta
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheEntry:
    """Cache entry with expiration and metadata"""
    
    def __init__(self, value: Any, ttl_seconds: int = 3600):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.created_at > self.ttl_seconds
    
    def access(self) -> Any:
        """Access the cached value and update metadata"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary for serialization"""
        return {
            'value': self.value,
            'created_at': self.created_at,
            'ttl_seconds': self.ttl_seconds,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create cache entry from dictionary"""
        entry = cls(data['value'], data['ttl_seconds'])
        entry.created_at = data['created_at']
        entry.access_count = data['access_count']
        entry.last_accessed = data['last_accessed']
        return entry

class MemoryCache:
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                logger.debug(f"Cache entry expired: {key}")
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return entry.access()
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set value in cache"""
        with self.lock:
            # Remove expired entries
            self._cleanup_expired()
            
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = CacheEntry(value, ttl_seconds)
            logger.debug(f"Cached data: {key} (TTL: {ttl_seconds}s)")
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Deleted cache entry: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size"""
        with self.lock:
            return len(self.cache)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.cache:
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]
            logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            
            access_counts = [entry.access_count for entry in self.cache.values()]
            avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'utilization': total_entries / self.max_size,
                'avg_access_count': avg_access_count,
                'memory_usage_kb': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in KB"""
        total_size = 0
        for key, entry in self.cache.items():
            total_size += len(key.encode('utf-8'))
            total_size += len(str(entry.value).encode('utf-8'))
        return total_size / 1024

class FileCache:
    """File-based cache for persistence"""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path.home() / '.trading_system' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Hash key to create valid filename
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache"""
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            if not cache_path.exists():
                return None
            
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                entry = CacheEntry.from_dict(data)
                if entry.is_expired():
                    cache_path.unlink()
                    logger.debug(f"File cache entry expired: {key}")
                    return None
                
                return entry.access()
                
            except Exception as e:
                logger.error(f"Error reading file cache {key}: {e}")
                cache_path.unlink(missing_ok=True)
                return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set value in file cache"""
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            try:
                entry = CacheEntry(value, ttl_seconds)
                with open(cache_path, 'w') as f:
                    json.dump(entry.to_dict(), f)
                
                logger.debug(f"File cached data: {key} (TTL: {ttl_seconds}s)")
                
            except Exception as e:
                logger.error(f"Error writing file cache {key}: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete key from file cache"""
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Deleted file cache entry: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all file cache entries"""
        with self.lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("File cache cleared")
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        with self.lock:
            expired_count = 0
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    entry = CacheEntry.from_dict(data)
                    if entry.is_expired():
                        cache_file.unlink()
                        expired_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error cleaning cache file {cache_file}: {e}")
                    cache_file.unlink(missing_ok=True)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            return expired_count

class CacheManager:
    """Unified cache manager with memory and file caching"""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 file_cache_dir: Path = None,
                 enable_file_cache: bool = True):
        self.memory_cache = MemoryCache(memory_cache_size)
        self.file_cache = FileCache(file_cache_dir) if enable_file_cache else None
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, use_file_cache: bool = True) -> Optional[Any]:
        """Get value from cache (memory first, then file)"""
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            self.stats['hits'] += 1
            return value
        
        # Try file cache if enabled
        if use_file_cache and self.file_cache:
            value = self.file_cache.get(key)
            if value is not None:
                # Store in memory cache for faster access
                self.memory_cache.set(key, value)
                self.stats['hits'] += 1
                return value
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600, 
             persist_to_file: bool = True) -> None:
        """Set value in cache"""
        self.memory_cache.set(key, value, ttl_seconds)
        
        if persist_to_file and self.file_cache:
            self.file_cache.set(key, value, ttl_seconds)
        
        self.stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from all caches"""
        memory_deleted = self.memory_cache.delete(key)
        file_deleted = self.file_cache.delete(key) if self.file_cache else False
        
        if memory_deleted or file_deleted:
            self.stats['deletes'] += 1
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all caches"""
        self.memory_cache.clear()
        if self.file_cache:
            self.file_cache.clear()
        
        self.stats = {'hits': 0, 'misses': 0, 'sets': 0, 'deletes': 0}
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        total_requests = self.stats['hits'] + self.stats['misses']
        return self.stats['hits'] / total_requests if total_requests > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'cache_stats': self.stats.copy(),
            'hit_rate': self.get_hit_rate(),
            'memory_cache': self.memory_cache.get_stats()
        }
        
        if self.file_cache:
            file_cache_files = len(list(self.file_cache.cache_dir.glob("*.cache")))
            stats['file_cache'] = {
                'cached_files': file_cache_files,
                'cache_dir': str(self.file_cache.cache_dir)
            }
        
        return stats
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        memory_cleanup = 0  # Memory cache auto-cleans on access
        file_cleanup = self.file_cache.cleanup_expired() if self.file_cache else 0
        return memory_cleanup + file_cleanup

# Decorator for easy caching
def cache_result(ttl_seconds: int = 3600, key_prefix: str = "", 
                persist_to_file: bool = True):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}_{hashlib.md5(str(args + tuple(sorted(kwargs.items()))).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl_seconds, persist_to_file)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator

# Global cache manager instance
cache_manager = CacheManager()

# Convenience functions
def get_cached(key: str, default: Any = None) -> Any:
    """Get cached value with default"""
    result = cache_manager.get(key)
    return result if result is not None else default

def set_cached(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Set cached value"""
    cache_manager.set(key, value, ttl_seconds)

def delete_cached(key: str) -> bool:
    """Delete cached value"""
    return cache_manager.delete(key)

if __name__ == "__main__":
    # Test cache functionality
    print("Cache Manager Test")
    print("=" * 50)
    
    # Test memory cache
    cache_manager.set("test_key", "test_value", ttl_seconds=60)
    print(f"Set test_key = test_value")
    
    retrieved = cache_manager.get("test_key")
    print(f"Retrieved: {retrieved}")
    
    # Test cache stats
    stats = cache_manager.get_stats()
    print(f"Cache stats: {stats}")
    
    # Test cleanup
    expired_count = cache_manager.cleanup_expired()
    print(f"Cleaned up {expired_count} expired entries")
