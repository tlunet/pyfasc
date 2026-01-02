"""
Language Registry

Manages the registration and discovery of language adapters.
This enables a plug-and-play architecture for adding new languages.
"""

import os
from typing import Dict, List, Optional, Type
from .base_adapter import LanguageAdapter
from .python_adapter import PythonAdapter
from .cpp_adapter import CppAdapter
from .julia_adapter import JuliaAdapter


class LanguageRegistry:
    """
    Central registry for managing language adapters.
    
    Provides methods to:
    - Auto-register all available adapters
    - Look up adapters by file extension or language name
    - Get lists of supported languages and extensions
    """
    
    def __init__(self, config_file: str = None):
        """Initialize the registry with built-in adapters."""
        self._adapters_by_name: Dict[str, LanguageAdapter] = {}
        self._adapters_by_extension: Dict[str, LanguageAdapter] = {}
        self._config_file = config_file
        self._register_builtin_adapters()
    
    def _register_builtin_adapters(self) -> None:
        """Register all built-in language adapters."""
        builtin_adapters = [
            PythonAdapter(),
            CppAdapter(config_file=self._config_file),
            JuliaAdapter(config_file=self._config_file),
        ]
        
        for adapter in builtin_adapters:
            self.register(adapter)
    
    def register(self, adapter: LanguageAdapter) -> None:
        """
        Register a language adapter.
        
        Args:
            adapter: The language adapter to register
        """
        # Register by language name
        self._adapters_by_name[adapter.name.lower()] = adapter
        
        # Register by file extensions
        for ext in adapter.extensions:
            # Normalize extension (ensure it starts with a dot)
            normalized_ext = ext if ext.startswith('.') else f'.{ext}'
            self._adapters_by_extension[normalized_ext.lower()] = adapter
        
        # Safe printing for Windows - use simple print, safe_print in utils handles it
        message = f"Registered adapter: {adapter.display_name} ({', '.join(adapter.extensions)})"
        try:
            print(message)
        except (UnicodeEncodeError, UnicodeError):
            # Fallback: print without emojis
            import re
            message_safe = re.sub(r'[\U0001F000-\U0001FFFF]+', '', message)
            print(message_safe.strip())
    
    def get_adapter_by_name(self, language_name: str) -> Optional[LanguageAdapter]:
        """
        Get an adapter by language name.
        
        Args:
            language_name: Name of the language (e.g., 'python', 'cpp', 'julia')
            
        Returns:
            The language adapter, or None if not found
        """
        return self._adapters_by_name.get(language_name.lower())
    
    def get_adapter_by_file(self, filename: str) -> Optional[LanguageAdapter]:
        """
        Get an adapter based on a file's extension.
        
        Args:
            filename: Name or path of the file
            
        Returns:
            The language adapter, or None if extension not recognized
        """
        _, ext = os.path.splitext(filename)
        return self._adapters_by_extension.get(ext.lower())
    
    def detect_language(self, filename: str) -> Optional[str]:
        """
        Detect the programming language from a filename.
        
        Args:
            filename: Name or path of the file
            
        Returns:
            Language name (e.g., 'python', 'cpp'), or None if not recognized
        """
        adapter = self.get_adapter_by_file(filename)
        return adapter.name if adapter else None
    
    def get_supported_languages(self) -> List[str]:
        """
        Get a list of all supported language names.
        
        Returns:
            List of language names
        """
        return list(self._adapters_by_name.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of all supported file extensions.
        
        Returns:
            List of file extensions (with dots)
        """
        return list(self._adapters_by_extension.keys())
    
    def get_language_info(self) -> List[Dict[str, str]]:
        """
        Get information about all registered languages.
        
        Returns:
            List of dictionaries with language information
        """
        info = []
        for adapter in self._adapters_by_name.values():
            info.append({
                'name': adapter.name,
                'display_name': adapter.display_name,
                'emoji': adapter.emoji,
                'extensions': ', '.join(adapter.extensions),
                'requires_compilation': str(adapter.requires_compilation)
            })
        return info
    
    def __repr__(self) -> str:
        languages = ', '.join(self.get_supported_languages())
        return f"<LanguageRegistry: {languages}>"


# Global registry instance
_global_registry: Optional[LanguageRegistry] = None


def get_registry(config_file: str = None) -> LanguageRegistry:
    """
    Get the global language registry instance.
    
    Returns:
        The global LanguageRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = LanguageRegistry(config_file=config_file)
    return _global_registry


def register_custom_adapter(adapter: LanguageAdapter) -> None:
    """
    Register a custom language adapter with the global registry.
    
    This function allows users to add support for new languages
    without modifying the core codebase.
    
    Args:
        adapter: The custom language adapter to register
        
    Example:
        >>> from adapters import register_custom_adapter
        >>> from adapters.base_adapter import LanguageAdapter
        >>> 
        >>> class RustAdapter(LanguageAdapter):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.name = "rust"
        >>>         self.extensions = [".rs"]
        >>>         # ... implement methods
        >>> 
        >>> register_custom_adapter(RustAdapter())
    """
    registry = get_registry()
    registry.register(adapter)
