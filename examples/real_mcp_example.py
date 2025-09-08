"""
Real-world example showing how to use actual Playwright MCP tools with Crawl4AI
This example shows the actual MCP tool calls that Claude would make
"""
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json


async def example_with_real_mcp():
    """
    This function demonstrates how the actual integration would work
    with real Playwright MCP tools available in Claude
    """
    
    print("=" * 60)
    print("Real MCP + Crawl4AI Integration Example")
    print("=" * 60)
    print("\nThis example shows the actual workflow when using Claude's MCP tools\n")
    
    # Step 1: Use MCP to navigate and interact with the page
    print("📍 Step 1: Using Playwright MCP for navigation and interaction")
    print("In Claude, you would use these MCP tools:")
    print("  - mcp__playwright__browser_navigate(url='https://example.com')")
    print("  - mcp__playwright__browser_snapshot() to see the page")
    print("  - mcp__playwright__browser_click(element='Login', ref='button#login')")
    print("  - mcp__playwright__browser_type(element='Username', ref='input#username', text='user@example.com')")
    
    # Step 2: Get page content from MCP
    print("\n📍 Step 2: Extract page HTML using MCP")
    print("In Claude, you would use:")
    print("  - mcp__playwright__browser_evaluate(function='() => document.documentElement.outerHTML')")
    
    # Simulated HTML content that would come from MCP
    mcp_html_content = """
    <html>
    <body>
        <div class="products">
            <div class="product">
                <h2>Product 1</h2>
                <span class="price">$19.99</span>
                <p class="description">Amazing product description</p>
            </div>
            <div class="product">
                <h2>Product 2</h2>
                <span class="price">$29.99</span>
                <p class="description">Another great product</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Step 3: Use Crawl4AI to process the extracted HTML
    print("\n📍 Step 3: Process extracted content with Crawl4AI")
    
    crawler = AsyncWebCrawler()
    await crawler.start()
    
    # Define extraction schema
    schema = {
        "name": "Products",
        "baseSelector": ".product",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "price", "selector": ".price", "type": "text"},
            {"name": "description", "selector": ".description", "type": "text"}
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema=schema)
    
    # Process the HTML content
    result = await crawler.arun(
        url="http://localhost",  # Dummy URL since we're providing HTML
        html=mcp_html_content,
        extraction_strategy=extraction_strategy
    )
    
    if result.success and result.extracted_content:
        products = json.loads(result.extracted_content)
        print(f"✅ Successfully extracted {len(products)} products:")
        for product in products:
            print(f"  • {product['title']}: {product['price']}")
            print(f"    {product['description']}")
    
    await crawler.stop()
    
    # Step 4: Show the complete workflow
    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW SUMMARY")
    print("=" * 60)
    print("""
    1. MCP Tools handle:
       - Browser automation
       - Page navigation
       - User interactions (click, type, scroll)
       - Waiting for elements
       - JavaScript execution
       - Authentication flows
    
    2. Crawl4AI handles:
       - Content extraction
       - Data structuring
       - Pattern matching
       - Text processing
       - Batch processing
    
    3. Benefits of this approach:
       ✅ MCP provides reliable browser control
       ✅ Crawl4AI provides powerful extraction
       ✅ Clear separation of concerns
       ✅ Can handle complex workflows
       ✅ Scalable and maintainable
    """)


async def show_mcp_tool_examples():
    """
    Show examples of actual MCP tool calls
    """
    print("\n" + "=" * 60)
    print("MCP TOOL REFERENCE")
    print("=" * 60)
    
    mcp_examples = {
        "Navigation": [
            "mcp__playwright__browser_navigate(url='https://example.com')",
            "mcp__playwright__browser_navigate_back()",
            "mcp__playwright__browser_navigate_forward()"
        ],
        "Interaction": [
            "mcp__playwright__browser_click(element='Button', ref='button.submit')",
            "mcp__playwright__browser_type(element='Search', ref='input#search', text='query')",
            "mcp__playwright__browser_select_option(element='Dropdown', ref='select#options', values=['option1'])"
        ],
        "Waiting": [
            "mcp__playwright__browser_wait_for(text='Loading complete')",
            "mcp__playwright__browser_wait_for(time=5)"
        ],
        "Content Access": [
            "mcp__playwright__browser_snapshot()",
            "mcp__playwright__browser_take_screenshot(filename='page.png')",
            "mcp__playwright__browser_evaluate(function='() => document.title')"
        ],
        "Advanced": [
            "mcp__playwright__browser_handle_dialog(accept=true)",
            "mcp__playwright__browser_file_upload(paths=['/path/to/file'])",
            "mcp__playwright__browser_console_messages()"
        ]
    }
    
    for category, tools in mcp_examples.items():
        print(f"\n{category}:")
        for tool in tools:
            print(f"  • {tool}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION PATTERN")
    print("=" * 60)
    print("""
    # Pattern 1: Simple extraction after navigation
    1. mcp__playwright__browser_navigate(url=target_url)
    2. mcp__playwright__browser_wait_for(text='Content loaded')
    3. html = mcp__playwright__browser_evaluate(function='() => document.documentElement.outerHTML')
    4. Use Crawl4AI to extract from html
    
    # Pattern 2: Login then extract
    1. mcp__playwright__browser_navigate(url=login_url)
    2. mcp__playwright__browser_type(element='Username', ref='#username', text=username)
    3. mcp__playwright__browser_type(element='Password', ref='#password', text=password)
    4. mcp__playwright__browser_click(element='Login', ref='button[type=submit]')
    5. mcp__playwright__browser_wait_for(text='Dashboard')
    6. mcp__playwright__browser_navigate(url=data_url)
    7. Use Crawl4AI to extract data
    
    # Pattern 3: Dynamic content with scrolling
    1. mcp__playwright__browser_navigate(url=target_url)
    2. Loop:
       - mcp__playwright__browser_evaluate(function='() => window.scrollTo(0, document.body.scrollHeight)')
       - mcp__playwright__browser_wait_for(time=1)
    3. html = mcp__playwright__browser_evaluate(function='() => document.documentElement.outerHTML')
    4. Use Crawl4AI with the complete HTML
    """)


async def main():
    """Run all examples"""
    await example_with_real_mcp()
    await show_mcp_tool_examples()
    print("\n✅ Examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())