"""
Async Operations for Performance Module
Provides asynchronous processing capabilities for improved performance
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import time

logger = logging.getLogger(__name__)

class AsyncOperationManager:
    """Manages async operations for improved performance"""
    
    def __init__(self, max_workers: int = 4, max_connections: int = 10):
        self.max_workers = max_workers
        self.max_connections = max_connections
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        
        logger.info(f"✅ AsyncOperationManager initialized: {max_workers} workers, {max_connections} connections")
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_connections)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_data_async(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Fetch data from URL asynchronously"""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise aiohttp.ClientError(f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            logger.error(f"Async fetch error for {url}: {e}")
            raise
    
    async def fetch_multiple(self, urls: List[str], headers: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Fetch multiple URLs concurrently"""
        try:
            tasks = [self.fetch_data_async(url, headers) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            successful = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {urls[i]}: {result}")
                else:
                    successful.append(result)
            
            return successful
            
        except Exception as e:
            logger.error(f"Multiple fetch error: {e}")
            raise
    
    def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run a function in a thread pool"""
        try:
            future = self.executor.submit(func, *args, **kwargs)
            return future.result()
        except Exception as e:
            logger.error(f"Thread execution error: {e}")
            raise
    
    async def parallel_process(self, items: List[Any], 
                              process_func: Callable[[Any], Any],
                              max_concurrent: int = 5) -> List[Any]:
        """Process items in parallel with concurrency limit"""
        try:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_limit(item):
                async with semaphore:
                    return process_func(item)
            
            tasks = [process_with_limit(item) for item in items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            successful = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to process item {i}: {result}")
                else:
                    successful.append(result)
            
            return successful
            
        except Exception as e:
            logger.error(f"Parallel processing error: {e}")
            raise
    
    async def batch_operations(self, operations: List[Callable], 
                              batch_size: int = 10) -> List[Any]:
        """Execute operations in batches"""
        try:
            results = []
            
            for i in range(0, len(operations), batch_size):
                batch = operations[i:i + batch_size]
                batch_results = await asyncio.gather(*[op() for op in batch], 
                                                      return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Batch operation {i+j} failed: {result}")
                    else:
                        results.append(result)
                
                # Small delay between batches
                if i + batch_size < len(operations):
                    await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch operations error: {e}")
            raise
    
    def async_retry(self, max_retries: int = 3, delay: float = 1.0):
        """Decorator for async retry logic"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        await asyncio.sleep(delay * (attempt + 1))
                return None
            return wrapper
        return decorator
    
    async def timeout_operation(self, coro, timeout: float = 30.0):
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout}s")
            raise

# Performance monitoring decorator
def async_performance_monitor(func):
    """Decorator to monitor async function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️  {func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# Convenience functions for common async patterns
async def parallel_data_fetch(urls: List[str], max_concurrent: int = 5) -> List[Dict]:
    """Fetch multiple data sources in parallel"""
    async with AsyncOperationManager(max_connections=max_concurrent) as manager:
        return await manager.fetch_multiple(urls)

async def batch_process_items(items: List[Any], 
                              processor: Callable[[Any], Any],
                              batch_size: int = 10) -> List[Any]:
    """Process items in optimized batches"""
    async with AsyncOperationManager() as manager:
        return await manager.parallel_process(items, processor, batch_size)

# Run async function from sync code
def run_async(coro):
    """Run async coroutine from synchronous code"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

__all__ = [
    'AsyncOperationManager', 
    'async_performance_monitor',
    'parallel_data_fetch',
    'batch_process_items',
    'run_async'
]
