# Quick Start Guide

## 1-Minute Setup

### Option A: Automatic Setup (Recommended)
```bash
./setup.sh
```

### Option B: Manual Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pip install -e .
```

## Run the Demo

### Start Web Interface
```bash
python web_demo.py
```
Open: http://localhost:5000

### Start Process Monitor
```bash
python process_monitor.py
```
Open: http://localhost:5001

## Test Examples

### Simple Test
```bash
python examples/simple_extraction.py
```

### With Authentication
```bash
python examples/authenticated_crawl.py
```

## Key Features to Try

1. **Basic Extraction**: Enter any URL and click "Extract"
2. **Authentication**: Use the auth demo with test credentials
3. **AI Extraction**: Try the AI-powered extraction mode
4. **Process Monitor**: Watch real-time crawling operations

## For Claude AI

When using with Claude (claude.ai/code):
- Claude reads `CLAUDE.md` automatically
- Can modify and extend all features
- Understands MCP integration patterns

## Need Help?

- Technical details: See `CLAUDE.md`
- Full documentation: See `README.md`
- Examples: Check `examples/` folder