"""
Python Language Adapter

Handles execution of Python programs.
"""

import sys
from typing import List, Tuple
from .base_adapter import LanguageAdapter


class PythonAdapter(LanguageAdapter):
    """Adapter for Python programs."""
    
    def __init__(self):
        super().__init__()
        self.name = "python"
        self.extensions = [".py"]
        self.requires_compilation = False
        self.display_name = "Python"
        self.emoji = "🐍"
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Python doesn't require compilation, just return the source file.
        
        Args:
            source_file: Path to the Python source file
            
        Returns:
            Tuple of (True, source_file, "")
        """
        return True, source_file, ""
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute a Python program.
        
        Args:
            prepared_file: Path to the Python source file
            
        Returns:
            List containing [python_interpreter, source_file]
        """
        return [sys.executable, prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """
        Python doesn't create temporary files during execution.
        
        Args:
            prepared_file: Path to the Python source file
        """
        pass  # No cleanup needed for Python
