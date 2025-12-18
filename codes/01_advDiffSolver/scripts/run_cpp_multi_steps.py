"""
Run C++ implementation with multiple time steps (64x64 grid).
"""

import os
import subprocess
import shutil
import platform
import tempfile
from pathlib import Path


def main():
    base_dir = Path(__file__).parent.parent
    cpp_file = base_dir / "src" / "program.cpp"
    
    # Use temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    results_dir = temp_dir
    
    # Binary name
    binary_name = "program_cpp.exe" if platform.system() == "Windows" else "program_cpp"
    binary_path = base_dir / binary_name
    
    # Compile
    if shutil.which("g++"):
        compiler = ["g++", str(cpp_file), "-O2", "-o", str(binary_path)]
    elif shutil.which("clang++"):
        compiler = ["clang++", str(cpp_file), "-O2", "-o", str(binary_path)]
    else:
        print("No compiler found!")
        return
    
    subprocess.run(compiler, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Run with different time steps
    grid_size = 64
    for nsteps in [16, 32, 64]:
        print(f"Running with {nsteps} steps...")
        
        # Create input (C++ reads input.txt directly)
        config = f"{grid_size} {grid_size} gauss diagonal 0.001 0.1 {nsteps}\n"
        input_file = base_dir / "input.txt"
        input_file.write_text(config)
        
        # Execute
        os.chdir(base_dir)
        exec_cmd = [str(binary_path)] if platform.system() == "Windows" else [f"./{binary_name}"]
        subprocess.run(exec_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Move results
        shutil.move(base_dir / "uInit.txt", results_dir / f"uInit_cpp_{nsteps}steps.txt")
        shutil.move(base_dir / "uEnd.txt", results_dir / f"uEnd_cpp_{nsteps}steps.txt")
    
    # Remove binary
    binary_path.unlink()
    print("Done!")
    
    # Return temp directory path for other scripts
    return str(results_dir)


if __name__ == "__main__":
    main()
