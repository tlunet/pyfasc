"""
C++ Language Adapter

Handles compilation and execution of C++ programs with support for multiple compilers.
"""

import os
import platform
import shutil
import subprocess
import time
from typing import List, Tuple
from .base_adapter import LanguageAdapter


class CppAdapter(LanguageAdapter):
    """Adapter for C++ programs."""
    
    def __init__(self):
        super().__init__()
        self.name = "cpp"
        self.extensions = [".cpp", ".cc", ".cxx", ".c++"]
        self.requires_compilation = True
        self.display_name = "C++"
        self.emoji = "⚙️"
        self._compiled_binary = None
    
    def _find_compiler(self) -> Tuple[str, List[str]]:
        """
        Find an available C++ compiler on the system.
        
        Returns:
            Tuple of (compiler_name, base_command)
            
        Raises:
            RuntimeError: If no compiler is found
        """
        # Try g++
        if shutil.which("g++"):
            return "g++", ["g++"]
        
        # Try clang++
        if shutil.which("clang++"):
            return "clang++", ["clang++"]
        
        # Try MSVC on Windows
        if platform.system() == "Windows" and shutil.which("cl"):
            return "msvc", ["cl"]
        
        # No compiler found
        raise RuntimeError(
            "No C++ compiler found. Please install:\n"
            "  - MinGW (g++) from https://www.mingw-w64.org/\n"
            "  - Or Visual Studio with C++ support\n"
            "  - Or Clang for Windows"
        )
    
    def _get_binary_name(self, source_file: str) -> str:
        """
        Get the output binary name based on the platform.
        
        Args:
            source_file: Path to the source file
            
        Returns:
            Name of the binary to create
        """
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        if platform.system() == "Windows":
            return f"temp_{base_name}_exec.exe"
        else:
            return f"temp_{base_name}_exec"
    
    def prepare(self, source_file: str) -> Tuple[bool, str, str]:
        """
        Compile the C++ source file.
        
        Args:
            source_file: Path to the C++ source file
            
        Returns:
            Tuple of (success, binary_path, error_message)
        """
        try:
            compiler_name, compiler_cmd = self._find_compiler()
            binary = self._get_binary_name(source_file)
            
            # Build compilation command based on compiler
            if compiler_name == "msvc":
                # MSVC syntax
                compile_cmd = compiler_cmd + ["/O2", f"/Fe:{binary}", source_file]
            else:
                # GCC/Clang syntax
                compile_cmd = compiler_cmd + [source_file, "-O2", "-o", binary]
            
            print(f"Compiling with: {' '.join(compile_cmd)}")
            
            # Measure compilation time
            compile_start = time.time()
            
            # Compile
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True
            )
            
            compile_end = time.time()
            self.compilation_time = compile_end - compile_start
            
            print(f"Compilation took {self.compilation_time:.3f}s")
            
            if result.returncode != 0:
                return False, "", f"Compilation failed: {result.stderr}"
            
            # Perform warm-up run
            print("Performing warm-up run for C++ binary...")
            self._compiled_binary = binary
            self.warmup(binary)
            
            return True, binary, ""
            
        except Exception as e:
            return False, "", str(e)
    
    def get_execution_command(self, prepared_file: str) -> List[str]:
        """
        Get the command to execute a compiled C++ program.
        
        Args:
            prepared_file: Path to the compiled binary
            
        Returns:
            List containing the binary path (with ./ prefix on Unix)
        """
        # On Unix-like systems, need ./ prefix for local executables
        if platform.system() != "Windows" and not prepared_file.startswith("./"):
            return [f"./{prepared_file}"]
        return [prepared_file]
    
    def cleanup(self, prepared_file: str) -> None:
        """
        Remove the compiled binary and any temporary files.
        
        Args:
            prepared_file: Path to the compiled binary
        """
        try:
            if os.path.exists(prepared_file):
                os.remove(prepared_file)
                print(f"Cleaned up: {prepared_file}")
        except Exception as e:
            print(f"Warning: Could not clean up {prepared_file}: {e}")
