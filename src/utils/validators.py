"""
Validation utilities for Prophere
Common form and data validation helpers
"""
import re
from typing import List, Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or len(email) > 120:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 6) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        min_length: Minimum required length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    return True, None


def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> tuple[bool, Optional[str]]:
    """
    Validate user name
    
    Args:
        name: Name to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name is required"
    
    name = name.strip()
    
    if len(name) < min_length:
        return False, f"Name must be at least {min_length} characters long"
    
    if len(name) > max_length:
        return False, f"Name must not exceed {max_length} characters"
    
    return True, None


def validate_keywords(keywords: str, min_count: int = 2) -> tuple[bool, Optional[str]]:
    """
    Validate comma-separated keywords
    
    Args:
        keywords: Comma-separated keywords string
        min_count: Minimum number of keywords required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not keywords:
        return False, f"At least {min_count} keywords are required"
    
    # Split and clean keywords
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    
    if len(keyword_list) < min_count:
        return False, f"At least {min_count} keywords are required (found {len(keyword_list)})"
    
    return True, None


def validate_word_count(text: str, max_words: int = 300) -> tuple[bool, Optional[str]]:
    """
    Validate word count in text
    
    Args:
        text: Text to validate
        max_words: Maximum allowed word count
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return True, None
    
    word_count = len(text.split())
    
    if word_count > max_words:
        return False, f"Text exceeds maximum of {max_words} words (found {word_count})"
    
    return True, None


def validate_file_extension(filename: str, allowed_extensions: set) -> tuple[bool, Optional[str]]:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions (without dots)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename or '.' not in filename:
        return False, "Invalid filename"
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File type '.{ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None


def sanitize_keywords(keywords: str) -> List[str]:
    """
    Clean and sanitize keywords
    
    Args:
        keywords: Comma-separated keywords
        
    Returns:
        List of cleaned keyword strings
    """
    if not keywords:
        return []
    
    # Split, strip whitespace, remove duplicates (case-insensitive), filter empty
    keyword_list = keywords.split(',')
    cleaned = []
    seen = set()
    
    for keyword in keyword_list:
        keyword = keyword.strip()
        keyword_lower = keyword.lower()
        
        if keyword and keyword_lower not in seen:
            cleaned.append(keyword)
            seen.add(keyword_lower)
    
    return cleaned
