"""
Thread-safe crawler wrapper for Flask integration
"""
import asyncio
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import functools
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy


class ThreadSafeCrawler:
    """Thread-safe wrapper for async crawler operations"""
    
    def __init__(self):
        self.crawler = None
        self.loop = None
        self.thread = None
        self._initialized = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def initialize(self):
        """Initialize the crawler in a dedicated thread"""
        if self._initialized:
            return
            
        def run_async_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._async_initialize())
            self.loop.run_forever()
            
        self.thread = threading.Thread(target=run_async_loop, daemon=True)
        self.thread.start()
        
        # Wait for initialization
        import time
        max_wait = 10
        waited = 0
        while not self._initialized and waited < max_wait:
            time.sleep(0.1)
            waited += 0.1
            
        if not self._initialized:
            raise RuntimeError("Failed to initialize crawler within timeout")
    
    async def _async_initialize(self):
        """Async initialization in the dedicated event loop"""
        try:
            self.crawler = AsyncWebCrawler()
            await self.crawler.start()
            self._initialized = True
            print("✅ Thread-safe crawler initialized")
        except Exception as e:
            print(f"❌ Failed to initialize crawler: {e}")
            raise
    
    def _run_in_loop(self, coro):
        """Run coroutine in the dedicated event loop"""
        if not self._initialized:
            self.initialize()
            
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=30)  # 30 second timeout
    
    def extract_content(self, url: str, wait_for: str = None) -> Dict[str, Any]:
        """Extract basic content from URL (synchronous interface)"""
        try:
            coro = self._async_extract_content(url, wait_for)
            return self._run_in_loop(coro)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": "",
                "title": "",
                "links": [],
                "images": []
            }
    
    async def _async_extract_content(self, url: str, wait_for: str = None) -> Dict[str, Any]:
        """Internal async content extraction"""
        try:
            result = await self.crawler.arun(
                url=url,
                wait_for=wait_for,
                timeout=15  # 15 second per-request timeout
            )
            
            return {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "") if hasattr(result, 'metadata') else "",
                "content": result.markdown if hasattr(result, 'markdown') else "",
                "links": result.links if hasattr(result, 'links') else {},
                "images": result.media.get("images", []) if hasattr(result, 'media') and result.media else [],
                "status": "completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": "",
                "title": "",
                "links": [],
                "images": [],
                "status": "failed"
            }
    
    def extract_with_ai(self, url: str, instruction: str) -> Dict[str, Any]:
        """Extract content using AI instruction (synchronous interface)"""
        try:
            coro = self._async_extract_with_ai(url, instruction)
            return self._run_in_loop(coro)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": "",
                "ai_extraction": ""
            }
    
    async def _async_extract_with_ai(self, url: str, instruction: str) -> Dict[str, Any]:
        """Internal async AI extraction"""
        try:
            strategy = LLMExtractionStrategy(
                provider="ollama/llama2",
                api_token="your-api-key",
                instruction=instruction
            )
            
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=strategy,
                timeout=20
            )
            
            return {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "") if hasattr(result, 'metadata') else "",
                "content": result.markdown if hasattr(result, 'markdown') else "",
                "ai_extraction": result.extracted_content if hasattr(result, 'extracted_content') else "",
                "status": "completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": "",
                "ai_extraction": "",
                "status": "failed"
            }
    
    def extract_structured_data(self, url: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data using CSS selectors (synchronous interface)"""
        try:
            coro = self._async_extract_structured_data(url, schema)
            return self._run_in_loop(coro)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "structured_data": []
            }
    
    async def _async_extract_structured_data(self, url: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Internal async structured data extraction"""
        try:
            strategy = JsonCssExtractionStrategy(schema)
            
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=strategy,
                timeout=15
            )
            
            return {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "") if hasattr(result, 'metadata') else "",
                "content": result.markdown if hasattr(result, 'markdown') else "",
                "structured_data": result.extracted_content if hasattr(result, 'extracted_content') else [],
                "status": "completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "structured_data": [],
                "status": "failed"
            }
    
    def extract_from_html(self, html_content: str, url: str = "dummy") -> Dict[str, Any]:
        """Extract content from HTML string (synchronous interface)"""
        try:
            coro = self._async_extract_from_html(html_content, url)
            return self._run_in_loop(coro)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "title": ""
            }
    
    async def _async_extract_from_html(self, html_content: str, url: str = "dummy") -> Dict[str, Any]:
        """Internal async HTML extraction"""
        try:
            result = await self.crawler.arun(
                url=url,
                html=html_content,
                timeout=10
            )
            
            return {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "") if hasattr(result, 'metadata') else "",
                "content": result.markdown if hasattr(result, 'markdown') else "",
                "status": "completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "title": "",
                "status": "failed"
            }
    
    def close(self):
        """Clean up resources"""
        if self.loop and not self.loop.is_closed():
            try:
                # Schedule cleanup in the event loop
                cleanup_coro = self._async_cleanup()
                asyncio.run_coroutine_threadsafe(cleanup_coro, self.loop)
                
                # Stop the event loop
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                print(f"Warning during cleanup: {e}")
        
        self.executor.shutdown(wait=False)
        self._initialized = False
    
    async def _async_cleanup(self):
        """Internal async cleanup"""
        if self.crawler:
            try:
                await self.crawler.close()
            except Exception as e:
                print(f"Warning during crawler cleanup: {e}")


# Global instance for Flask app
_global_crawler = None

def get_thread_safe_crawler() -> ThreadSafeCrawler:
    """Get or create global thread-safe crawler instance"""
    global _global_crawler
    if _global_crawler is None:
        _global_crawler = ThreadSafeCrawler()
        _global_crawler.initialize()
    return _global_crawler