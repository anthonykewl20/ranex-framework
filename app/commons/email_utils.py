"""Email utility functions for validation and formatting."""

import re


def validate_email(email: str) -> bool:
    """
    Validate email address using RFC 5322 regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_email(email: str) -> str:
    """
    Normalize email address to lowercase.
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email address
    """
    return email.lower().strip()
