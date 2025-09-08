#!/bin/bash

# Start Web Demo for Crawl4AI + Playwright MCP
echo "🌐 Starting Crawl4AI + Playwright MCP Web Demo"
echo "============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   playwright install chromium"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip install flask flask-cors
fi

echo "🚀 Starting Flask web server..."
echo "📍 Web demo will be available at: http://localhost:8080"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Start the web demo
python web_demo.py