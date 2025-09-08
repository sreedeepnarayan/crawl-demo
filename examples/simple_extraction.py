"""
Example 1: Simple extraction - Navigate with MCP, extract with Crawl4AI
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import CrawlOrchestrator
import json


async def main():
    """
    Demonstrate simple navigation and extraction
    """
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    print("=" * 60)
    print("Example 1: Simple Navigation and Extraction")
    print("=" * 60)
    
    # Example 1: Basic content extraction
    print("\n📍 Test 1: Extract content from a news website")
    result = await orchestrator.navigate_and_extract(
        url="https://news.ycombinator.com"
    )
    
    if result["extraction"]["success"]:
        print(f"✅ Successfully extracted content from {result['url']}")
        print(f"   - Title: {result['extraction']['title']}")
        print(f"   - Links found: {len(result['extraction']['links'])}")
        print(f"   - Images found: {len(result['extraction']['images'])}")
    
    # Example 2: Structured data extraction with schema
    print("\n📍 Test 2: Extract structured data using CSS selectors")
    
    schema = {
        "name": "HackerNews Stories",
        "baseSelector": ".athing",
        "fields": [
            {
                "name": "title",
                "selector": ".titleline > a",
                "type": "text"
            },
            {
                "name": "link",
                "selector": ".titleline > a",
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "points",
                "selector": ".score",
                "type": "text"
            }
        ]
    }
    
    result2 = await orchestrator.navigate_and_extract(
        url="https://news.ycombinator.com",
        extraction_schema=schema
    )
    
    if result2["extraction"]["success"]:
        print(f"✅ Successfully extracted structured data")
        data = result2["extraction"]["structured_data"]
        print(f"   - Items extracted: {len(data) if isinstance(data, list) else 0}")
        
        # Show first few items
        if isinstance(data, list) and len(data) > 0:
            print("\n   Sample extracted items:")
            for item in data[:3]:
                print(f"   • {item.get('title', 'N/A')}")
    
    # Example 3: Dynamic content handling
    print("\n📍 Test 3: Handle dynamic content with scroll and wait")
    
    result3 = await orchestrator.dynamic_content_extract(
        url="https://example.com",
        wait_selector=".content",
        scroll_times=2
    )
    
    print(f"✅ Dynamic content extraction completed")
    print(f"   - Scrolled {result3['scroll_times']} times")
    print(f"   - Content length: {len(result3['extraction'].get('content', ''))}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    
    all_results = orchestrator.get_all_results()
    print(f"Total extractions performed: {len(all_results)}")
    
    mcp_history = orchestrator.get_mcp_history()
    print(f"Total MCP actions performed: {len(mcp_history)}")
    
    print("\nMCP Action breakdown:")
    action_types = {}
    for action in mcp_history:
        action_type = action.get("action", "unknown")
        action_types[action_type] = action_types.get(action_type, 0) + 1
    
    for action_type, count in action_types.items():
        print(f"  - {action_type}: {count}")
    
    await orchestrator.close()
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())