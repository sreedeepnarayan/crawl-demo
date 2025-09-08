"""
Data processing utilities for extracted content
"""
import re
import json
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import pandas as pd


class DataProcessor:
    """Process and clean extracted data"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Trim
        return text.strip()
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from text
        
        Args:
            text: Text to search
            
        Returns:
            List of email addresses
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_phones(text: str) -> List[str]:
        """
        Extract phone numbers from text
        
        Args:
            text: Text to search
            
        Returns:
            List of phone numbers
        """
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # US with parentheses
            r'\b\+\d{1,3}\s?\d{1,14}\b'  # International
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text
        
        Args:
            text: Text to search
            
        Returns:
            List of URLs
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_prices(text: str) -> List[Dict[str, Any]]:
        """
        Extract prices from text
        
        Args:
            text: Text to search
            
        Returns:
            List of price dictionaries
        """
        price_patterns = [
            (r'\$[\d,]+\.?\d*', 'USD'),
            (r'€[\d,]+\.?\d*', 'EUR'),
            (r'£[\d,]+\.?\d*', 'GBP'),
            (r'¥[\d,]+\.?\d*', 'JPY')
        ]
        
        prices = []
        for pattern, currency in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean and convert to float
                value_str = re.sub(r'[^\d.]', '', match)
                try:
                    value = float(value_str)
                    prices.append({
                        'raw': match,
                        'value': value,
                        'currency': currency
                    })
                except ValueError:
                    continue
        
        return prices
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        Extract dates from text
        
        Args:
            text: Text to search
            
        Returns:
            List of date strings
        """
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))
    
    @staticmethod
    def structure_table_data(html: str, table_selector: str = 'table') -> List[Dict[str, Any]]:
        """
        Extract and structure table data from HTML
        
        Args:
            html: HTML content
            table_selector: CSS selector for tables
            
        Returns:
            List of dictionaries representing table rows
        """
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.select(table_selector)
        
        all_data = []
        
        for table in tables:
            # Get headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            else:
                # Try first row as headers
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            
            # Get data rows
            tbody = table.find('tbody') or table
            rows = tbody.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == len(headers) and headers:
                    row_data = {}
                    for header, cell in zip(headers, cells):
                        row_data[header] = cell.get_text(strip=True)
                    all_data.append(row_data)
                elif cells:
                    # No headers, use indices
                    row_data = {f'col_{i}': cell.get_text(strip=True) 
                               for i, cell in enumerate(cells)}
                    all_data.append(row_data)
        
        return all_data
    
    @staticmethod
    def deduplicate_items(items: List[Dict[str, Any]], key_field: str) -> List[Dict[str, Any]]:
        """
        Remove duplicate items based on a key field
        
        Args:
            items: List of dictionaries
            key_field: Field to use for deduplication
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []
        
        for item in items:
            key_value = item.get(key_field)
            if key_value and key_value not in seen:
                seen.add(key_value)
                unique.append(item)
        
        return unique
    
    @staticmethod
    def flatten_nested_dict(nested: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten a nested dictionary
        
        Args:
            nested: Nested dictionary
            parent_key: Parent key prefix
            sep: Separator for keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        
        for k, v in nested.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(
                    DataProcessor.flatten_nested_dict(v, new_key, sep=sep).items()
                )
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(
                            DataProcessor.flatten_nested_dict(
                                item, f"{new_key}{sep}{i}", sep=sep
                            ).items()
                        )
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    @staticmethod
    def summarize_content(content: str, max_length: int = 200) -> str:
        """
        Create a summary of content
        
        Args:
            content: Content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized content
        """
        if not content:
            return ""
        
        # Clean the content first
        clean = DataProcessor.clean_text(content)
        
        if len(clean) <= max_length:
            return clean
        
        # Find a good breaking point
        truncated = clean[:max_length]
        last_period = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_period > max_length * 0.8:
            return truncated[:last_period + 1]
        elif last_space > 0:
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."


class DataValidator:
    """Validate extracted data"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Check if phone number is valid"""
        # Remove common characters
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check if it's a reasonable phone number length
        return 7 <= len(cleaned) <= 15
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data dictionary
            required: List of required field names
            
        Returns:
            Validation result
        """
        missing = []
        empty = []
        
        for field in required:
            if field not in data:
                missing.append(field)
            elif not data[field] or data[field] == "":
                empty.append(field)
        
        return {
            'valid': len(missing) == 0 and len(empty) == 0,
            'missing_fields': missing,
            'empty_fields': empty
        }