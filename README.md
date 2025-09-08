# Crawl4AI + Playwright MCP Integration

## Overview

This repository contains a proof-of-concept integration between Crawl4AI and Playwright MCP (Model Context Protocol) tools. It demonstrates advanced web scraping capabilities by combining browser automation with intelligent content extraction.

## What This Does

- **Automated Web Scraping**: Extract structured data from any website
- **Authentication Handling**: Navigate through login flows automatically
- **Dynamic Content**: Handle JavaScript-rendered pages and AJAX content
- **AI-Powered Extraction**: Use LLMs to intelligently parse and structure data
- **Real-time Monitoring**: Visualize crawling operations as they happen

## Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone [repository-url]
cd crawl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 2. Run the Demo
```bash
# Start the web interface
python web_demo.py

# Open browser to http://localhost:5000
```

### 3. Test It Out
1. Enter any URL in the web interface
2. Click "Extract" to see structured data
3. Try the authentication demo with test credentials

## For Claude AI Testing

When using this with Claude AI (claude.ai/code), Claude will automatically:
1. Read the `CLAUDE.md` file for detailed instructions
2. Understand the MCP integration patterns
3. Be able to modify and extend the functionality

### Key Files for Claude
- `CLAUDE.md` - Comprehensive AI instructions
- `src/orchestrator.py` - Main orchestration logic
- `examples/` - Working examples to reference

## Features Included

✅ **Core Functionality**
- Crawl4AI engine integration
- Playwright MCP bridge
- Authentication workflows
- Dynamic content extraction

✅ **User Interfaces**
- Web demo at http://localhost:5000
- Process monitor at http://localhost:5001
- Real-time extraction results

✅ **Developer Tools**
- Thread-safe operations
- Comprehensive error handling
- Multiple extraction strategies
- Data processing utilities

## Example Usage

### Simple Extraction
```python
from src.orchestrator import CrawlOrchestrator
import asyncio

async def extract_data():
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.extract_from_page(
        "https://example.com",
        strategy="auto"
    )
    
    print(result['data'])
    await orchestrator.cleanup()

asyncio.run(extract_data())
```

### With Authentication
```python
# Handle login and extract protected content
await orchestrator.handle_authentication(
    login_url="https://example.com/login",
    username="demo@example.com",
    password="demo123"
)

result = await orchestrator.extract_from_page(
    "https://example.com/dashboard"
)
```

## Architecture
```
Playwright MCP → Navigation & Interaction
     ↓
Current Page State
     ↓
Crawl4AI → Content Extraction & Parsing
     ↓
Structured Data Output
```

## Project Structure
```
crawl/
├── src/               # Core source code
│   ├── crawl_engine.py      # Crawl4AI integration
│   ├── mcp_bridge.py        # MCP connection
│   └── orchestrator.py      # Main coordinator
├── examples/          # Working examples
├── templates/         # Web UI templates
├── web_demo.py       # Interactive demo
├── process_monitor.py # Real-time monitor
└── CLAUDE.md         # AI instructions
```

## Testing with MCP Tools

This project is designed to work with Playwright MCP tools in Claude. The integration allows Claude to:
- Navigate websites using MCP browser tools
- Extract content using Crawl4AI
- Handle complex workflows automatically

## Command Line Usage

### Web Demo (Recommended)
```bash
# Start web demo
./start_web_demo.sh

# Or manually:
python web_demo.py

# Then open: http://localhost:5000
```

### Run Examples
```bash
# Simple extraction
python examples/simple_extraction.py

# With authentication
python examples/authenticated_crawl.py

# Real MCP integration
python examples/real_mcp_example.py
```

### Interactive Testing
```bash
./run_demo.sh test        # Automated tests
./run_demo.sh interactive # Interactive demo
./run_demo.sh real-mcp    # MCP integration patterns
```

## Troubleshooting

### Common Issues

**Browser not installed:**
```bash
playwright install chromium
```

**Import errors:**
```bash
pip install -e .
```

**Port already in use:**
Change the port in web_demo.py or use:
```bash
python web_demo.py --port 5001
```

## Next Steps

1. **Test the Demo**: Run `python web_demo.py` and try extracting from different websites
2. **Review Examples**: Check `examples/` folder for implementation patterns
3. **Use with Claude**: Open in claude.ai/code for AI-assisted development
4. **Extend Features**: Add new extraction strategies or workflows

## Support

- **Documentation**: See `CLAUDE.md` for detailed technical documentation
- **Examples**: Working code in `examples/` directory
- **Architecture**: Review `src/` for implementation details

---

**Status**: ✅ Ready for Testing - All core features implemented and working