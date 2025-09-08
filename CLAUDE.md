# CLAUDE.md - AI Assistant Instructions

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

**Crawl4AI + Playwright MCP Integration POC**

This is a proof-of-concept that demonstrates how to integrate Crawl4AI with Playwright MCP (Model Context Protocol) tools for advanced web scraping and automation. The project combines:
- **Playwright MCP** for browser automation, navigation, and user interactions
- **Crawl4AI** for intelligent content extraction, data structuring, and AI-powered parsing

## Key Features Developed

1. **Unified Orchestration** - Seamless coordination between MCP browser control and Crawl4AI extraction
2. **Authentication Flows** - Handle login sequences with form filling and session management
3. **Dynamic Content Extraction** - Process JavaScript-rendered pages and dynamic content
4. **AI-Powered Extraction** - Use LLM strategies for intelligent data extraction
5. **Web Demo Interface** - Interactive demo with real-time extraction and monitoring
6. **Process Monitoring** - Real-time visualization of crawling operations

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install package in development mode
pip install -e .
```

### 2. Run the Web Demo
```bash
# Start the interactive web demo
python web_demo.py

# Or use the startup script
./start_web_demo.sh

# Access at: http://localhost:5000
```

### 3. Run Process Monitor
```bash
# Start the process monitor for real-time visualization
python process_monitor.py

# Access at: http://localhost:5001
```

## Architecture Components

### Core Modules

#### 1. **CrawlEngine** (`src/crawl_engine.py`)
Main engine for Crawl4AI operations:
- Content extraction with CSS selectors
- AI-based extraction strategies
- Structured data parsing
- HTML processing from MCP

#### 2. **MCPBridge** (`src/mcp_bridge.py`)
Real MCP integration for production:
- Connects to actual Playwright MCP tools
- Manages browser state
- Handles navigation and interactions

#### 3. **CrawlOrchestrator** (`src/orchestrator.py`)
Coordinates MCP and Crawl4AI:
- Authentication workflows
- Multi-page crawling
- Dynamic content handling
- Session management

#### 4. **ThreadSafeCrawler** (`src/thread_safe_crawler.py`)
Thread-safe wrapper for concurrent operations:
- Async queue management
- Error handling
- Resource cleanup

### Web Interfaces

#### 1. **Web Demo** (`web_demo.py`)
Interactive demonstration interface:
- URL input with extraction
- Authentication testing
- Real-time results display
- Multiple extraction strategies

#### 2. **Process Monitor** (`process_monitor.py`)
Real-time monitoring dashboard:
- Live crawling progress
- Performance metrics
- Error tracking
- Visual status indicators

## MCP Tool Integration Pattern

When using Playwright MCP tools in Claude, follow this pattern:

```python
# 1. Navigate to page
await mcp__playwright__browser_navigate(url="https://example.com")

# 2. Wait for content to load
await mcp__playwright__browser_wait_for(text="Content loaded")

# 3. Interact if needed (forms, buttons, etc.)
await mcp__playwright__browser_type(
    element="username field",
    ref="input#username",
    text="user@example.com"
)
await mcp__playwright__browser_click(
    element="submit button",
    ref="button[type='submit']"
)

# 4. Extract HTML for processing
html = await mcp__playwright__browser_evaluate(
    function="() => document.documentElement.outerHTML"
)

# 5. Process with Crawl4AI
from src.crawl_engine import CrawlEngine
engine = CrawlEngine()
await engine.initialize()
result = await engine.extract_from_html(html, extraction_config)
```

## Common Workflows

### Authentication Flow
```python
orchestrator = CrawlOrchestrator()
await orchestrator.initialize()

# Perform login
await orchestrator.handle_authentication(
    login_url="https://example.com/login",
    username="user@example.com",
    password="password",
    username_selector="input#username",
    password_selector="input#password",
    submit_selector="button[type='submit']"
)

# Extract from protected page
result = await orchestrator.extract_from_page(
    "https://example.com/dashboard",
    extraction_strategy="ai"
)
```

### Dynamic Content Extraction
```python
# Navigate and wait for dynamic content
await orchestrator.mcp.navigate("https://example.com")
await orchestrator.mcp.wait_for_element(".dynamic-content")
await orchestrator.mcp.scroll_to_bottom()

# Extract after content loads
result = await orchestrator.extract_current_page(
    strategy="css",
    selectors={
        "items": ".item-card",
        "title": "h2.title",
        "price": ".price"
    }
)
```

### Multi-Page Crawling
```python
# Crawl multiple pages with pagination
results = []
for page in range(1, 5):
    url = f"https://example.com/products?page={page}"
    result = await orchestrator.extract_from_page(url)
    results.extend(result['data'])
```

## Testing

### Run Examples
```bash
# Simple extraction
python examples/simple_extraction.py

# Authenticated crawling
python examples/authenticated_crawl.py

# Real MCP integration
python examples/real_mcp_example.py
```

### Manual Testing
```python
# Test basic extraction
from src.crawl_engine import CrawlEngine
import asyncio

async def test():
    engine = CrawlEngine()
    await engine.initialize()
    result = await engine.extract_from_url("https://example.com")
    print(result)
    await engine.cleanup()

asyncio.run(test())
```

## Data Processing Utilities

The `utils/data_processors.py` module provides helpers for:
- Text cleaning and normalization
- Entity extraction (emails, phones, URLs, prices, dates)
- Table data structuring
- JSON/CSV formatting
- Data validation and deduplication

## Development Commands

### Linting and Format
```bash
# Format code with black
black src/ examples/

# Check with flake8
flake8 src/ examples/

# Type checking
mypy src/
```

### Build and Deploy
```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install locally
pip install -e .

# Run tests
pytest tests/
```

## Environment Variables

Create a `.env` file for configuration:
```env
# Server settings
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

# Crawl4AI settings
MAX_WORKERS=5
EXTRACTION_TIMEOUT=30

# MCP settings (if using real MCP)
MCP_SERVER_URL=http://localhost:3000
```

## Important Notes

1. **Async Operations**: All crawling operations are async - always use `await` and `asyncio.run()`
2. **Resource Management**: Always call `cleanup()` methods to free resources
3. **Error Handling**: The system includes comprehensive error handling - check result status
4. **MCP vs Simulated**: Use `MCPBridge` for real MCP, `MCPWrapper` for testing
5. **Thread Safety**: Use `ThreadSafeCrawler` for concurrent operations

## Troubleshooting

### Common Issues

1. **Playwright not installed**
   ```bash
   playwright install chromium
   ```

2. **Import errors**
   ```bash
   pip install -e .  # Install package in development mode
   ```

3. **Async context errors**
   - Ensure all async functions are properly awaited
   - Use `asyncio.run()` for top-level execution

4. **Browser timeout**
   - Increase timeout in configuration
   - Check network connectivity
   - Verify selectors are correct

## Project Status

✅ **Completed Features:**
- Core crawling engine with Crawl4AI
- MCP integration bridge
- Authentication handling
- Dynamic content extraction
- Web demo interface
- Process monitoring dashboard
- Thread-safe operations
- Multiple extraction strategies
- Error handling and recovery

🚀 **Ready for Testing:**
- All core functionality is implemented
- Examples are working and documented
- Web interfaces are operational
- Can be used with real Playwright MCP tools

## Support

For issues or questions about:
- **Crawl4AI**: Check [Crawl4AI documentation](https://github.com/unclecode/crawl4ai)
- **Playwright MCP**: Refer to MCP documentation
- **This Integration**: Review examples and this documentation