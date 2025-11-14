"""
Adapter-specific helper functions.

Provides utility functions specifically for working with language adapters.
"""

import sys


def get_emoji_safe_display(adapter):
    """
    Get a display string for an adapter that's safe on all platforms.
    
    Args:
        adapter: LanguageAdapter instance
        
    Returns:
        str: Display string with emoji on UTF-8 systems, without on others
    """
    try:
        # Try to encode the emoji
        test = f"{adapter.emoji} {adapter.display_name}"
        test.encode(sys.stdout.encoding or 'utf-8')
        return test
    except (UnicodeEncodeError, AttributeError):
        # Fallback without emoji
        return adapter.display_name


def format_language_list(adapters):
    """
    Format a list of adapters for display.
    
    Args:
        adapters: List of LanguageAdapter instances or LanguageRegistry
        
    Returns:
        str: Formatted string with language names
    """
    if hasattr(adapters, 'get_supported_languages'):
        # It's a registry
        languages = adapters.get_supported_languages()
    elif isinstance(adapters, (list, tuple)):
        languages = [a.name if hasattr(a, 'name') else str(a) for a in adapters]
    else:
        return str(adapters)
    
    return ', '.join(languages)
