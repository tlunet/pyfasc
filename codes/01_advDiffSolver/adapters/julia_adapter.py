"""
Julia Language Adapter

Handles execution of Julia programs.
"""

import os
import shutil
from typing import List, Tuple
from .base_adapter import LanguageAdapter
from .config_parser import parse_compiler_config


class JuliaAdapter(LanguageAdapter):
    """Adapter for Julia programs."""
    
    def __init__(self, config_file: str = None):
        super().__init__()
        self.name = "julia"
        self.extensions = [".jl"]
        self.requires_compilation = False
        self.display_name = "Julia"
        self.emoji = "🔬"
        self._custom_flags = self._load_flags(config_file)
    
    def _load_flags(self, config_file: str) -> List[str]:
        """Load Julia flags from config file"""
        if not config_file or not os.path.exists(config_file):
            return []
        
        config = parse_compiler_config(config_file)
        flags_str = config.get("julia", "")
        return flags_str.split() if flags_str else []
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Julia doesn't require compilation, but check if Julia is installed.
        
        Args:
            source_file: Path to the Julia source file
            
        Returns:
            Tuple of (success, source_file, error_message)
        """
        if not shutil.which("julia"):
            return False, "", "Julia interpreter not found. Please install Julia."
        
        return True, source_file, ""
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute a Julia program.
        
        Args:
            prepared_file: Path to the Julia source file
            
        Returns:
            List containing ['julia', flags..., source_file]
        """
        return ["julia"] + self._custom_flags + [prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """
        Julia doesn't create temporary files during execution.
        
        Args:
            prepared_file: Path to the Julia source file
        """
        pass  # No cleanup needed for Julia
