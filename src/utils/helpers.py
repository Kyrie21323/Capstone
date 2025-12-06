"""
Common helper functions for Prophere
Reusable utility functions across the application
"""
from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime], format_string: str = '%B %d, %Y at %I:%M %p') -> str:
    """
    Format datetime object to string
    
    Args:
        dt: Datetime object to format
        format_string: strftime format string
        
    Returns:
        Formatted datetime string or empty string if None
    """
    if not dt:
        return ''
    
    return dt.strftime(format_string)


def format_date(dt: Optional[datetime], format_string: str = '%B %d, %Y') -> str:
    """
    Format datetime object to date string
    
    Args:
        dt: Datetime object to format
        format_string: strftime format string
        
    Returns:
        Formatted date string or empty string if None
    """
    if not dt:
        return ''
    
    return dt.strftime(format_string)


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_file_size_str(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable string
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Return singular or plural form based on count
    
    Args:
        count: Count value
        singular: Singular form
        plural: Plural form (defaults to singular + 's')
        
    Returns:
        Appropriate form with count
    """
    if plural is None:
        plural = singular + 's'
    
    word = singular if count == 1 else plural
    return f"{count} {word}"


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing/replacing problematic characters
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for filesystem
    """
    import re
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove or replace other problematic characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    return filename.strip()


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text
    
    Args:
        text: Text to slugify
        
    Returns:
        URL-friendly slug
    """
    import re
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    return slug.strip('-')


def parse_keywords(keywords_str: str) -> list:
    """
    Parse comma-separated keywords into list
    
    Args:
        keywords_str: Comma-separated keywords
        
    Returns:
        List of cleaned keywords
    """
    if not keywords_str:
        return []
    
    return [k.strip() for k in keywords_str.split(',') if k.strip()]


def keywords_to_string(keywords_list: list) -> str:
    """
    Convert list of keywords to comma-separated string
    
    Args:
        keywords_list: List of keywords
        
    Returns:
        Comma-separated string
    """
    if not keywords_list:
        return ''
    
    return ', '.join(str(k).strip() for k in keywords_list if k)
