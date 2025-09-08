from setuptools import setup, find_packages

setup(
    name="crawl4ai-mcp-poc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crawl4ai>=0.3.0",
        "playwright>=1.40.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "aiohttp>=3.9.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
)