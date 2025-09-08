"""
Orchestrator that coordinates Playwright MCP and Crawl4AI operations
"""
from typing import Dict, Any, List, Optional
from .mcp_wrapper import MCPSession
from .crawl_engine import CrawlEngine
import asyncio


class CrawlOrchestrator:
    """
    Coordinates operations between Playwright MCP and Crawl4AI
    """
    
    def __init__(self):
        self.mcp_session = MCPSession()
        self.crawl_engine = CrawlEngine()
        self.results = []
    
    async def initialize(self):
        """Initialize both engines"""
        await self.crawl_engine.initialize()
        print("✅ Orchestrator initialized")
    
    async def navigate_and_extract(self, url: str, extraction_schema: Dict = None) -> Dict[str, Any]:
        """
        Navigate to a URL with MCP, then extract content with Crawl4AI
        
        Args:
            url: Target URL
            extraction_schema: Optional schema for structured extraction
            
        Returns:
            Combined results from navigation and extraction
        """
        # Step 1: Navigate with MCP
        nav_result = await self.mcp_session.execute_action("navigate", url=url)
        
        # Step 2: Wait for page load
        await asyncio.sleep(1)
        
        # Step 3: Extract content with Crawl4AI
        if extraction_schema:
            extract_result = await self.crawl_engine.extract_structured_data(url, extraction_schema)
        else:
            extract_result = await self.crawl_engine.extract_content(url)
        
        result = {
            "navigation": nav_result,
            "extraction": extract_result,
            "url": url
        }
        
        self.results.append(result)
        return result
    
    async def login_and_extract(self, login_url: str, target_url: str,
                                username: str, password: str,
                                extraction_instruction: str = None) -> Dict[str, Any]:
        """
        Login using MCP, navigate to target, extract with Crawl4AI
        
        Args:
            login_url: URL of login page
            target_url: URL to extract after login
            username: Login username
            password: Login password
            extraction_instruction: Optional AI extraction instruction
            
        Returns:
            Combined results
        """
        # Step 1: Navigate to login page
        await self.mcp_session.execute_action("navigate", url=login_url)
        
        # Step 2: Perform authentication
        auth_result = await self.mcp_session.execute_action(
            "authenticate",
            username=username,
            password=password
        )
        
        # Step 3: Navigate to target page
        await self.mcp_session.execute_action("navigate", url=target_url)
        
        # Step 4: Extract content
        if extraction_instruction:
            extract_result = await self.crawl_engine.extract_with_ai(
                target_url, 
                extraction_instruction
            )
        else:
            extract_result = await self.crawl_engine.extract_content(target_url)
        
        result = {
            "authentication": auth_result,
            "extraction": extract_result,
            "login_url": login_url,
            "target_url": target_url
        }
        
        self.results.append(result)
        return result
    
    async def interactive_crawl(self, start_url: str, actions: List[Dict], 
                               extraction_points: List[str]) -> List[Dict[str, Any]]:
        """
        Perform interactive crawling with MCP actions and Crawl4AI extraction
        
        Args:
            start_url: Starting URL
            actions: List of MCP actions to perform
            extraction_points: URLs or markers where to extract content
            
        Returns:
            List of extraction results
        """
        results = []
        
        # Navigate to start URL
        await self.mcp_session.execute_action("navigate", url=start_url)
        current_url = start_url
        
        for action in actions:
            # Execute MCP action
            action_result = await self.mcp_session.execute_action(
                action["type"],
                **action.get("params", {})
            )
            
            # Check if we should extract at this point
            if action.get("extract_after", False):
                # Get current page HTML via MCP
                html_result = await self.mcp_session.execute_action("get_html")
                html_content = html_result.get("html", "")
                
                # Extract with Crawl4AI
                extract_result = await self.crawl_engine.extract_from_html(
                    html_content,
                    current_url
                )
                
                results.append({
                    "action": action,
                    "action_result": action_result,
                    "extraction": extract_result
                })
            
            # Update current URL if navigation occurred
            if action["type"] == "navigate":
                current_url = action["params"].get("url", current_url)
        
        self.results.extend(results)
        return results
    
    async def parallel_extract(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs in parallel using Crawl4AI
        
        Args:
            urls: List of URLs to extract from
            
        Returns:
            List of extraction results
        """
        tasks = [self.crawl_engine.extract_content(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        self.results.extend(results)
        return results
    
    async def dynamic_content_extract(self, url: str, wait_selector: str,
                                     scroll_times: int = 3) -> Dict[str, Any]:
        """
        Handle dynamic content: navigate, scroll, wait, then extract
        
        Args:
            url: Target URL
            wait_selector: CSS selector to wait for
            scroll_times: Number of times to scroll
            
        Returns:
            Extraction results
        """
        # Navigate with MCP
        await self.mcp_session.execute_action("navigate", url=url)
        
        # Wait for element
        await self.mcp_session.execute_action("wait", selector=wait_selector)
        
        # Scroll to load more content
        for i in range(scroll_times):
            await self.mcp_session.execute_action(
                "evaluate",
                script="() => window.scrollTo(0, document.body.scrollHeight)"
            )
            await asyncio.sleep(1)
        
        # Extract with Crawl4AI
        extract_result = await self.crawl_engine.extract_content(url, wait_for=wait_selector)
        
        result = {
            "url": url,
            "dynamic_load": True,
            "scroll_times": scroll_times,
            "extraction": extract_result
        }
        
        self.results.append(result)
        return result
    
    async def form_submit_extract(self, url: str, form_data: Dict[str, str],
                                 submit_button: str = "button[type='submit']") -> Dict[str, Any]:
        """
        Fill form with MCP, submit, then extract results with Crawl4AI
        
        Args:
            url: Form URL
            form_data: Dictionary of field selectors and values
            submit_button: Submit button selector
            
        Returns:
            Extraction results after form submission
        """
        # Navigate to form
        await self.mcp_session.execute_action("navigate", url=url)
        
        # Fill form fields
        for selector, value in form_data.items():
            await self.mcp_session.execute_action(
                "type",
                selector=selector,
                text=value,
                element_description=f"Form field: {selector}"
            )
        
        # Submit form
        await self.mcp_session.execute_action(
            "click",
            selector=submit_button,
            element_description="Submit button"
        )
        
        # Wait for results
        await asyncio.sleep(2)
        
        # Get current URL (might have changed after submission)
        current_url = self.mcp_session.get_current_url() or url
        
        # Extract results
        extract_result = await self.crawl_engine.extract_content(current_url)
        
        result = {
            "form_url": url,
            "form_data": form_data,
            "extraction": extract_result
        }
        
        self.results.append(result)
        return result
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all collected results"""
        return self.results
    
    def get_mcp_history(self) -> List[Dict[str, Any]]:
        """Get MCP action history"""
        return self.mcp_session.get_history()
    
    async def close(self):
        """Clean up resources"""
        await self.crawl_engine.close()
        print("✅ Orchestrator closed")