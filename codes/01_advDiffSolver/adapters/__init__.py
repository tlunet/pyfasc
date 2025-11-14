"""
Language Adapters Package

This package provides adapters for different programming languages,
enabling easy extension with new languages through the Strategy Pattern.
"""

from .base_adapter import LanguageAdapter
from .registry import LanguageRegistry
from .adapter_helpers import get_emoji_safe_display

__all__ = [
    'LanguageAdapter', 
    'LanguageRegistry',
    'get_emoji_safe_display'
]
