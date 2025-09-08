#!/bin/bash

# Crawl4AI + Playwright MCP Demo Runner
# This script activates the virtual environment and runs the demo

echo "🚀 Starting Crawl4AI + Playwright MCP Demo"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   playwright install chromium"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if we should run tests or interactive demo
if [ "$1" = "test" ]; then
    echo "🧪 Running automated tests..."
    python test_manual.py
elif [ "$1" = "interactive" ]; then
    echo "🎮 Running interactive demo..."
    echo "y" | python test_manual.py
elif [ "$1" = "real-mcp" ]; then
    echo "📋 Running real MCP example..."
    python examples/real_mcp_example.py
else
    echo "Available options:"
    echo "  ./run_demo.sh test        - Run automated tests"
    echo "  ./run_demo.sh interactive - Run interactive demo"
    echo "  ./run_demo.sh real-mcp    - Show real MCP integration patterns"
    echo ""
    echo "Or run manually:"
    echo "  source venv/bin/activate"
    echo "  python test_manual.py"
fi