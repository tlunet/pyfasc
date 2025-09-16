"""
Julia Language Adapter

Handles execution of Julia programs.
"""

import shutil
from typing import List, Tuple
from .base_adapter import LanguageAdapter


class JuliaAdapter(LanguageAdapter):
    """Adapter for Julia programs."""
    
    def __init__(self):
        super().__init__()
        self.name = "julia"
        self.extensions = [".jl"]
        self.requires_compilation = False
        self.display_name = "Julia"
        self.emoji = "🔬"
    
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
            List containing ['julia', source_file]
        """
        return ["julia", prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """
        Julia doesn't create temporary files during execution.
        
        Args:
            prepared_file: Path to the Julia source file
        """
        pass  # No cleanup needed for Julia
