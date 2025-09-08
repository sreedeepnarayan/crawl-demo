#!/bin/bash

echo "========================================="
echo "Crawl4AI + MCP Integration Setup"
echo "========================================="

# Check Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "✓ Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -n "Creating virtual environment... "
    $PYTHON_CMD -m venv venv
    echo "✓"
else
    echo "Virtual environment already exists ✓"
fi

# Activate virtual environment
echo -n "Activating virtual environment... "
source venv/bin/activate
echo "✓"

# Upgrade pip
echo -n "Upgrading pip... "
pip install --upgrade pip --quiet
echo "✓"

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Install Playwright browsers
echo -n "Installing Playwright browser... "
playwright install chromium --with-deps
echo "✓"

# Install package in development mode
echo -n "Installing package in development mode... "
pip install -e . --quiet
echo "✓"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "To get started:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the web demo:"
echo "   python web_demo.py"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:5000"
echo ""
echo "For more information, see README.md"
echo "========================================="