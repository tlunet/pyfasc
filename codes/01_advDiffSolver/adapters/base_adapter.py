"""
Base Language Adapter

Defines the abstract interface that all language adapters must implement.
This enables a consistent way to handle different programming languages.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import subprocess
import time


class LanguageAdapter(ABC):
    """
    Abstract base class for language adapters.
    
    Each language adapter must implement methods for:
    - Preparing the program (e.g., compilation)
    - Executing the program
    - Cleaning up temporary files
    """
    
    def __init__(self):
        """Initialize the adapter with language-specific properties."""
        self.name: str = ""
        self.extensions: List[str] = []
        self.requires_compilation: bool = False
        self.display_name: str = ""
        self.emoji: str = "📄"
        self.compilation_time: float = 0.0  # Track compilation time
    
    @abstractmethod
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Prepare the program for execution (e.g., compile if needed).
        
        Args:
            source_file: Path to the source code file
            
        Returns:
            Tuple of (success, executable_path, error_message)
        """
        pass
    
    @abstractmethod
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute the prepared program.
        
        Args:
            prepared_file: Path to the prepared/compiled program
            
        Returns:
            List of command arguments
        """
        pass
    
    def execute(self, prepared_file: str, config_content: str, 
                config_files: Optional[List[str]] = None) -> Dict:
        """
        Execute the program with the given configuration.
        
        Args:
            prepared_file: Path to the prepared/compiled program
            config_content: Content to write to config file
            config_files: List of config file names to write to
            
        Returns:
            Dictionary with runtime, total_time, stdout, stderr, and returncode
        """
        if config_files is None:
            config_files = ["config.txt", "input.txt"]
        
        # Write config content to files
        for config_filename in config_files:
            with open(config_filename, "w") as f:
                f.write(config_content)
        
        # Get execution command
        cmd = self.get_execution_command(prepared_file)
        
        # Measure execution time
        start = time.time()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        end = time.time()
        
        execution_time = end - start
        total_time = self.compilation_time + execution_time
        
        return {
            "runtime": execution_time,
            "total_time": total_time,
            "compilation_time": self.compilation_time
        }
    
    def warmup(self, prepared_file: str) -> bool:
        """
        Perform a warm-up run to load libraries and cache the executable.
        
        Args:
            prepared_file: Path to the prepared/compiled program
            
        Returns:
            True if warm-up successful, False otherwise
        """
        try:
            warmup_config = "warmup\n"
            for config_filename in ["config.txt", "input.txt"]:
                with open(config_filename, "w") as f:
                    f.write(warmup_config)
            
            cmd = self.get_execution_command(prepared_file)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate(timeout=10)
            print(f"  {self.display_name} warm-up complete")
            return True
        except Exception as e:
            print(f"  Warning: {self.display_name} warm-up failed (this is OK): {e}")
            return False
    
    @abstractmethod
    def cleanup(self, prepared_file: str) -> None:
        """
        Clean up temporary files created during preparation/execution.
        
        Args:
            prepared_file: Path to the prepared/compiled program
        """
        pass
    
    def detect_from_file(self, filename: str) -> bool:
        """
        Check if this adapter can handle the given file.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if this adapter can handle the file, False otherwise
        """
        return any(filename.lower().endswith(ext) for ext in self.extensions)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
