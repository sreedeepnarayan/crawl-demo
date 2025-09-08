"""
Crawl4AI extraction engine for content parsing and structured data extraction
"""
import asyncio
from typing import Dict, List, Optional, Any
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
    NoExtractionStrategy
)
import json


class CrawlEngine:
    """Handles content extraction using Crawl4AI"""
    
    def __init__(self):
        self.crawler = None
        
    async def initialize(self):
        """Initialize the async web crawler"""
        self.crawler = AsyncWebCrawler()
        await self.crawler.start()
        
    async def extract_content(self, url: str, wait_for: str = None) -> Dict[str, Any]:
        """
        Extract basic content from a URL
        
        Args:
            url: Target URL
            wait_for: CSS selector to wait for before extraction
            
        Returns:
            Dictionary with extracted content
        """
        if not self.crawler:
            await self.initialize()
            
        result = await self.crawler.arun(
            url=url,
            wait_for=wait_for
        )
        
        return {
            "url": url,
            "title": result.metadata.get("title", "") if hasattr(result, 'metadata') else "",
            "content": result.markdown if hasattr(result, 'markdown') else "",
            "links": result.links if hasattr(result, 'links') else {},
            "images": result.media.get("images", []) if hasattr(result, 'media') and result.media else [],
            "success": result.success if hasattr(result, 'success') else False,
            "error": result.error_message if hasattr(result, 'error_message') and not result.success else None
        }
    
    async def extract_structured_data(self, url: str, schema: Dict) -> Dict[str, Any]:
        """
        Extract structured data using CSS selectors
        
        Args:
            url: Target URL
            schema: Extraction schema with CSS selectors
            
        Returns:
            Dictionary with structured data
        """
        if not self.crawler:
            await self.initialize()
            
        extraction_strategy = JsonCssExtractionStrategy(
            schema=schema,
            verbose=True
        )
        
        result = await self.crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy
        )
        
        extracted_data = []
        if result.extracted_content:
            extracted_data = json.loads(result.extracted_content)
            
        return {
            "url": url,
            "structured_data": extracted_data,
            "raw_content": result.markdown,
            "success": result.success,
            "error": result.error_message if not result.success else None
        }
    
    async def extract_with_ai(self, url: str, instruction: str, wait_for: str = None) -> Dict[str, Any]:
        """
        Extract content using AI-based extraction
        
        Args:
            url: Target URL
            instruction: Natural language instruction for extraction
            wait_for: CSS selector to wait for
            
        Returns:
            Dictionary with AI-extracted content
        """
        if not self.crawler:
            await self.initialize()
            
        extraction_strategy = LLMExtractionStrategy(
            instruction=instruction,
            verbose=True
        )
        
        result = await self.crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy,
            wait_for=wait_for
        )
        
        return {
            "url": url,
            "ai_extracted": result.extracted_content,
            "raw_content": result.markdown,
            "success": result.success,
            "error": result.error_message if not result.success else None
        }
    
    async def extract_from_html(self, html_content: str, base_url: str = None) -> Dict[str, Any]:
        """
        Extract content from raw HTML (useful when HTML comes from MCP)
        
        Args:
            html_content: Raw HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with extracted content
        """
        # For now, use BeautifulSoup to extract basic content from HTML
        # This avoids the complex HTML parameter issue in Crawl4AI
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            content = soup.get_text(separator=' ', strip=True)
            
            # Extract links
            links = {"internal": [], "external": []}
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links["external"].append({"url": href, "text": link.get_text(strip=True)})
                else:
                    links["internal"].append({"url": href, "text": link.get_text(strip=True)})
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                images.append({"src": img['src'], "alt": img.get('alt', '')})
            
            return {
                "content": content,
                "links": links,
                "images": images,
                "success": True
            }
        except Exception as e:
            return {
                "content": "",
                "links": {"internal": [], "external": []},
                "images": [],
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the crawler"""
        if self.crawler:
            # Use context manager method or check if stop exists
            if hasattr(self.crawler, 'stop'):
                await self.crawler.stop()
            elif hasattr(self.crawler, 'close'):
                await self.crawler.close()
            self.crawler = None