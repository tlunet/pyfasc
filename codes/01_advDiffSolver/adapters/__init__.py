"""
Language Adapters Package

This package provides adapters for different programming languages,
enabling easy extension with new languages through the Strategy Pattern.
"""

from .base_adapter import LanguageAdapter
from .registry import LanguageRegistry
from .utils import safe_print, configure_windows_console, get_emoji_safe_display

__all__ = [
    'LanguageAdapter', 
    'LanguageRegistry',
    'safe_print',
    'configure_windows_console',
    'get_emoji_safe_display'
]
