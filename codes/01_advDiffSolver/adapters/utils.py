"""
Utility functions for the adapters package.

Provides helper functions for common tasks like safe printing on Windows.
"""

import sys
import re


def safe_print(text, file=None):
    """
    Print text safely, handling encoding issues on Windows.
    
    This function is particularly useful when printing text with emojis
    or other Unicode characters on Windows systems where the console
    might use cp1252 encoding instead of UTF-8.
    
    Args:
        text: Text to print (can contain emojis and Unicode)
        file: Output stream (defaults to sys.stdout)
    
    Example:
        >>> safe_print("🐍 Python program loaded")
        # Will print with emoji on UTF-8 systems
        # Will print " Python program loaded" on cp1252 systems
    """
    if file is None:
        file = sys.stdout
    
    try:
        print(text, file=file)
    except (UnicodeEncodeError, UnicodeError):
        # Remove emojis and problematic Unicode characters
        # Emoji range: U+1F300 to U+1F9FF (plus some other ranges)
        text_no_emoji = re.sub(
            r'[\U0001F300-\U0001F9FF'  # Emoticons
            r'\U0001F600-\U0001F64F'   # Emoticons 2
            r'\U0001F680-\U0001F6FF'   # Transport & Map Symbols
            r'\U0001F1E0-\U0001F1FF'   # Flags
            r'\U00002700-\U000027BF'   # Dingbats
            r'\U0000FE00-\U0000FE0F'   # Variation Selectors
            r'\U00002600-\U000026FF'   # Miscellaneous Symbols
            r']+', 
            '', 
            text
        )
        print(text_no_emoji.strip(), file=file)


def configure_windows_console():
    """
    Configure Windows console for UTF-8 encoding.
    
    This should be called at the start of the program to enable
    proper Unicode/emoji support on Windows.
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if sys.platform != 'win32':
        return True  # Not Windows, no configuration needed
    
    try:
        import io
        # Reconfigure stdout and stderr to use UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        return True
    except Exception as e:
        # If reconfiguration fails, safe_print will handle it
        return False


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
