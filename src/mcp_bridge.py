"""
MCPBridge - REAL Playwright Integration
This version uses actual browser automation, not simulation
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser

@dataclass
class MCPResult:
    """Result from MCP operation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[float] = None

@dataclass
class MCPBridge:
    """
    REAL Bridge to Playwright browser automation
    This uses actual browser control, not simulation
    """
    browser_active: bool = False
    current_page_url: Optional[str] = None
    session_cookies: Dict[str, Any] = field(default_factory=dict)
    action_history: list = field(default_factory=list)
    
    # Real browser instances
    _playwright = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _context = None
    
    async def initialize(self):
        """Initialize the real browser"""
        try:
            if not self._playwright:
                self._playwright = await async_playwright().start()
                print("✅ Playwright initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Playwright: {e}")
            return False
    
    async def launch_browser(self, headless: bool = True):
        """Launch real browser instance"""
        try:
            if not self._playwright:
                await self.initialize()
            
            if self._browser:
                await self._browser.close()
            
            # Launch real browser
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Create context with permissions
            self._context = await self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Create page
            self._page = await self._context.new_page()
            self.browser_active = True
            
            print(f"🌐 Real browser launched (headless={headless})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    async def navigate(self, url: str) -> MCPResult:
        """Navigate to URL using real browser"""
        try:
            if not self._page:
                await self.launch_browser()
            
            # Real navigation with longer timeout
            response = await self._page.goto(url, wait_until='domcontentloaded', timeout=60000)
            self.current_page_url = url
            
            # Log action
            self.action_history.append({
                'action': 'navigate',
                'url': url,
                'timestamp': time.time(),
                'status': 'success'
            })
            
            return MCPResult(
                success=True,
                data={
                    "url": url,
                    "status": response.status if response else 200,
                    "ok": response.ok if response else True
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Navigation failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def type_text(self, selector: str, text: str, element_desc: str) -> MCPResult:
        """Type text into element using real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Wait for element and type
            await self._page.wait_for_selector(selector, timeout=10000)
            await self._page.fill(selector, text)
            
            # Log action
            self.action_history.append({
                'action': 'type',
                'selector': selector,
                'text': text[:20] + '...' if len(text) > 20 else text,
                'element': element_desc,
                'timestamp': time.time()
            })
            
            return MCPResult(
                success=True,
                data={"selector": selector, "element": element_desc},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Type failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def click_element(self, selector: str, element_desc: str) -> MCPResult:
        """Click element using real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Wait and click
            await self._page.wait_for_selector(selector, timeout=10000)
            await self._page.click(selector)
            
            # Log action
            self.action_history.append({
                'action': 'click',
                'selector': selector,
                'element': element_desc,
                'timestamp': time.time()
            })
            
            return MCPResult(
                success=True,
                data={"selector": selector, "element": element_desc},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Click failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def wait_for_element(self, selector: str, timeout: int = 30) -> MCPResult:
        """Wait for element to appear using real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Real wait
            element = await self._page.wait_for_selector(selector, timeout=timeout * 1000)
            
            return MCPResult(
                success=True,
                data={"selector": selector, "found": element is not None},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Wait failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def wait_for_navigation(self, timeout: int = 30) -> MCPResult:
        """Wait for navigation to complete"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Wait for navigation
            await self._page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            
            # Update current URL
            self.current_page_url = self._page.url
            
            return MCPResult(
                success=True,
                data={"url": self.current_page_url},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Navigation wait failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def get_page_content(self) -> MCPResult:
        """Get full page HTML using real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Get real HTML content
            html = await self._page.content()
            
            return MCPResult(
                success=True,
                data={"html": html, "url": self._page.url},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Content extraction failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def take_screenshot(self, path: str = None) -> MCPResult:
        """Take screenshot using real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            if not path:
                path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # Take real screenshot
            await self._page.screenshot(path=path, full_page=True)
            
            return MCPResult(
                success=True,
                data={"path": path},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Screenshot failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def evaluate_javascript(self, script: str) -> MCPResult:
        """Execute JavaScript in real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Execute real JavaScript
            result = await self._page.evaluate(script)
            
            return MCPResult(
                success=True,
                data={"result": result},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"JavaScript evaluation failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def check_element_exists(self, selector: str) -> MCPResult:
        """Check if element exists in real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Check element
            element = await self._page.query_selector(selector)
            
            return MCPResult(
                success=True,
                data={"exists": element is not None, "selector": selector},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Element check failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def get_current_url(self) -> MCPResult:
        """Get current page URL from real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            url = self._page.url
            self.current_page_url = url
            
            return MCPResult(
                success=True,
                data={"url": url},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"URL retrieval failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def close_browser(self) -> MCPResult:
        """Close real browser"""
        try:
            if self._page:
                await self._page.close()
                self._page = None
            
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            self.browser_active = False
            self.current_page_url = None
            
            return MCPResult(
                success=True,
                data={"status": "closed"},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Browser close failed: {str(e)}",
                timestamp=time.time()
            )
    
    async def get_snapshot(self) -> MCPResult:
        """Get accessibility snapshot from real browser"""
        try:
            if not self._page:
                return MCPResult(success=False, error="Browser not initialized")
            
            # Get accessibility tree
            snapshot = await self._page.accessibility.snapshot()
            
            return MCPResult(
                success=True,
                data={"snapshot": snapshot},
                timestamp=time.time()
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Snapshot failed: {str(e)}",
                timestamp=time.time()
            )
    
    def is_browser_active(self) -> bool:
        """Check if browser is active"""
        return self.browser_active and self._page is not None
    
    async def _call_mcp_function(self, function_name: str, params: Dict[str, Any]) -> MCPResult:
        """
        Bridge function to map MCP-style calls to real Playwright
        """
        try:
            if function_name == "browser_navigate":
                return await self.navigate(params.get("url"))
            
            elif function_name == "browser_type":
                return await self.type_text(
                    params.get("ref", params.get("selector")),
                    params.get("text"),
                    params.get("element", "")
                )
            
            elif function_name == "browser_click":
                return await self.click_element(
                    params.get("ref", params.get("selector")),
                    params.get("element", "")
                )
            
            elif function_name == "browser_wait_for":
                if "text" in params:
                    # Wait for text selector
                    return await self.wait_for_element(
                        f'text={params["text"]}',
                        params.get("time", 30)
                    )
                else:
                    # Wait for navigation
                    return await self.wait_for_navigation(params.get("time", 30))
            
            elif function_name == "browser_evaluate":
                return await self.evaluate_javascript(params.get("function"))
            
            elif function_name == "browser_snapshot":
                return await self.get_snapshot()
            
            elif function_name == "browser_close":
                return await self.close_browser()
            
            elif function_name == "browser_screenshot":
                return await self.take_screenshot(params.get("path"))
            
            else:
                return MCPResult(
                    success=False,
                    error=f"Unknown MCP function: {function_name}"
                )
                
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"MCP function call failed: {str(e)}"
            )

# Global instance
_mcp_bridge = None

def get_mcp_bridge():
    """Get or create the MCP bridge instance"""
    global _mcp_bridge
    if _mcp_bridge is None:
        _mcp_bridge = MCPBridge()
    return _mcp_bridge