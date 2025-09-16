"""
Example: How to Add Rust Language Support

This file demonstrates how easy it is to add support for a new programming language
using the adapter architecture. Copy this pattern to add support for any language!

Steps to add a new language:
1. Create a new adapter class (like RustAdapter below)
2. Implement the required methods: prepare(), get_execution_command(), cleanup()
3. Register the adapter with the registry
4. That's it! No changes to app.py or diagnosetool.py needed!

Usage:
    python tests/diagnosetool.py --rust my_program.rs --cpp other_program.cpp --config config.txt
"""

import os
import platform
import shutil
import subprocess
from typing import List, Tuple
from adapters.base_adapter import LanguageAdapter
from adapters.registry import register_custom_adapter


class RustAdapter(LanguageAdapter):
    """
    Adapter for Rust programs.
    
    Rust programs need to be compiled with rustc before execution.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "rust"
        self.extensions = [".rs"]
        self.requires_compilation = True
        self.display_name = "Rust"
        self.emoji = "🦀"
        self._compiled_binary = None
    
    def _get_binary_name(self, source_file: str) -> str:
        """Get the output binary name based on the platform."""
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        if platform.system() == "Windows":
            return f"temp_{base_name}_rust.exe"
        else:
            return f"temp_{base_name}_rust"
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Compile the Rust source file using rustc.
        
        Args:
            source_file: Path to the Rust source file
            
        Returns:
            Tuple of (success, binary_path, error_message)
        """
        try:
            # Check if rustc is installed
            if not shutil.which("rustc"):
                return False, "", "Rust compiler (rustc) not found. Please install Rust from https://rustup.rs/"
            
            binary = self._get_binary_name(source_file)
            
            # Compile with optimization
            compile_cmd = ["rustc", source_file, "-O", "-o", binary]
            
            print(f"Compiling Rust with: {' '.join(compile_cmd)}")
            
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, "", f"Rust compilation failed: {result.stderr}"
            
            # Perform warm-up run
            print("Performing warm-up run for Rust binary...")
            self._compiled_binary = binary
            self.warmup(binary)
            
            return True, binary, ""
            
        except Exception as e:
            return False, "", str(e)
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute a compiled Rust program.
        
        Args:
            prepared_file: Path to the compiled binary
            
        Returns:
            List containing the binary path
        """
        # On Unix-like systems, need ./ prefix for local executables
        if platform.system() != "Windows" and not prepared_file.startswith("./"):
            return [f"./{prepared_file}"]
        return [prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """
        Remove the compiled binary.
        
        Args:
            prepared_file: Path to the compiled binary
        """
        try:
            if os.path.exists(prepared_file):
                os.remove(prepared_file)
                print(f"Cleaned up: {prepared_file}")
        except Exception as e:
            print(f"Warning: Could not clean up {prepared_file}: {e}")


# ===================================
# Example: JavaScript/Node.js Support
# ===================================

class JavaScriptAdapter(LanguageAdapter):
    """
    Adapter for JavaScript programs (Node.js).
    
    JavaScript programs are interpreted and don't need compilation.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "javascript"
        self.extensions = [".js"]
        self.requires_compilation = False
        self.display_name = "JavaScript"
        self.emoji = "📜"
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        JavaScript doesn't require compilation, but check if Node.js is installed.
        
        Args:
            source_file: Path to the JavaScript source file
            
        Returns:
            Tuple of (success, source_file, error_message)
        """
        if not shutil.which("node"):
            return False, "", "Node.js not found. Please install Node.js from https://nodejs.org/"
        
        return True, source_file, ""
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute a JavaScript program.
        
        Args:
            prepared_file: Path to the JavaScript source file
            
        Returns:
            List containing ['node', source_file]
        """
        return ["node", prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """JavaScript doesn't create temporary files during execution."""
        pass  # No cleanup needed for JavaScript


# ===================================
# Example: Go Language Support
# ===================================

class GoAdapter(LanguageAdapter):
    """
    Adapter for Go programs.
    
    Go programs need to be compiled with 'go build' before execution.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "go"
        self.extensions = [".go"]
        self.requires_compilation = True
        self.display_name = "Go"
        self.emoji = "🐹"
        self._compiled_binary = None
    
    def _get_binary_name(self, source_file: str) -> str:
        """Get the output binary name based on the platform."""
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        if platform.system() == "Windows":
            return f"temp_{base_name}_go.exe"
        else:
            return f"temp_{base_name}_go"
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Compile the Go source file.
        
        Args:
            source_file: Path to the Go source file
            
        Returns:
            Tuple of (success, binary_path, error_message)
        """
        try:
            # Check if go is installed
            if not shutil.which("go"):
                return False, "", "Go compiler not found. Please install Go from https://golang.org/"
            
            binary = self._get_binary_name(source_file)
            
            # Compile
            compile_cmd = ["go", "build", "-o", binary, source_file]
            
            print(f"Compiling Go with: {' '.join(compile_cmd)}")
            
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, "", f"Go compilation failed: {result.stderr}"
            
            # Perform warm-up run
            print("Performing warm-up run for Go binary...")
            self._compiled_binary = binary
            self.warmup(binary)
            
            return True, binary, ""
            
        except Exception as e:
            return False, "", str(e)
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """Get the command to execute a compiled Go program."""
        # On Unix-like systems, need ./ prefix for local executables
        if platform.system() != "Windows" and not prepared_file.startswith("./"):
            return [f"./{prepared_file}"]
        return [prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """Remove the compiled binary."""
        try:
            if os.path.exists(prepared_file):
                os.remove(prepared_file)
                print(f"Cleaned up: {prepared_file}")
        except Exception as e:
            print(f"Warning: Could not clean up {prepared_file}: {e}")


# ===================================
# Register Custom Adapters
# ===================================

if __name__ == "__main__":
    """
    To use these custom adapters, simply run this file before using the benchmark tool,
    or import and register them in your own script.
    """
    print("Registering custom language adapters...")
    
    # Register Rust support
    register_custom_adapter(RustAdapter())
    
    # Register JavaScript support
    register_custom_adapter(JavaScriptAdapter())
    
    # Register Go support
    register_custom_adapter(GoAdapter())
    
    print("\nCustom adapters registered successfully!")
    print("\nYou can now use these languages with the benchmark tool:")
    print("  python tests/diagnosetool.py --rust my_program.rs --cpp other.cpp --config input.txt")
    print("  python tests/diagnosetool.py --javascript my_program.js --py other.py --config input.txt")
    print("  python tests/diagnosetool.py --go my_program.go --cpp other.cpp --config input.txt")
