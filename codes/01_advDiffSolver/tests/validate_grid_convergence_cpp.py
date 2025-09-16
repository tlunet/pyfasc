"""
Grid Convergence Validation for C++ Implementation
Compiles and runs the C++ program with different grid sizes to validate convergence behavior.
"""

import sys
import os
import subprocess
import numpy as np
import tempfile
import platform
import shutil

def compile_cpp_program(cpp_file="program.cpp"):
    """Compile the C++ program"""
    try:
        # Determine executable name based on platform
        exe_name = "program_cpp_exec.exe" if platform.system() == "Windows" else "program_cpp_exec"
        
        # Check for available C++ compilers
        if shutil.which("g++"):
            compiler = "g++"
        elif shutil.which("clang++"):
            compiler = "clang++"
        elif platform.system() == "Windows" and shutil.which("cl"):
            compiler = "cl"
        else:
            print("No C++ compiler found (g++, clang++, or MSVC)")
            return False
        
        # Compile with optimization flags for better performance
        if compiler in ["g++", "clang++"]:
            result = subprocess.run([
                compiler, "-O2", "-std=c++17", 
                cpp_file, "-o", exe_name
            ], capture_output=True, text=True, timeout=60)
        else:  # MSVC
            result = subprocess.run([
                compiler, "/O2", "/std:c++17", 
                cpp_file, "/Fe:" + exe_name
            ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"Compilation failed: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("Compilation timed out")
        return False
    except Exception as e:
        print(f"Compilation error: {e}")
        return False

def run_cpp_simulation(nX, nY):
    """Run C++ simulation with given grid size"""
    input_content = f"{nX} {nY}\ngauss\ndiagonal 0.0\n0.1 50\n"  # Kürzere Zeit für Stabilität
    
    # Determine executable name based on platform
    exe_name = "program_cpp_exec.exe" if platform.system() == "Windows" else "./program_cpp_exec"
    
    # Create temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
    
    try:
        # Copy to input.txt (C++ program expects this filename)
        with open("input.txt", "w") as f:
            f.write(input_content)
        
        # Run the C++ executable
        result = subprocess.run(
            [exe_name], 
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode != 0:
            print(f"C++ simulation failed for grid {nX}x{nY}: {result.stderr}")
            return None
        
        # Read the output solution
        if os.path.exists("uEnd.txt"):
            try:
                # Read the solution file - C++ writes a grid format
                with open("uEnd.txt", "r") as f:
                    lines = f.readlines()
                
                # Parse the solution data - each line contains row values separated by spaces
                data = []
                for line in lines:
                    line = line.strip()
                    if line:  # Skip empty lines
                        values = [float(x) for x in line.split()]
                        data.extend(values)
                
                if data:
                    # Return mean value like in Python version
                    return np.mean(data)
                else:
                    print(f"No numerical data found in uEnd.txt for grid {nX}x{nY}")
                    return None
                    
            except Exception as e:
                print(f"Error reading solution file for grid {nX}x{nY}: {e}")
                return None
        else:
            print(f"Output file uEnd.txt not found for grid {nX}x{nY}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"C++ simulation timed out for grid {nX}x{nY}")
        return None
    except Exception as e:
        print(f"Error running C++ simulation for grid {nX}x{nY}: {e}")
        return None

def validate_cpp_grid_convergence(cpp_file="program.cpp"):
    """Main validation function for C++ implementation"""
    print("Starting C++ Grid Convergence Validation...")
    
    # Compile the C++ program
    if not compile_cpp_program(cpp_file):
        print("C++ Grid Convergence Validation FAILED: Compilation error.")
        return False
    
    print("C++ program compiled successfully.")
    
    # Test different grid sizes
    grid_sizes = [32, 64, 128, 256]
    solutions = []
    
    for grid_size in grid_sizes:
        print(f"Running simulation with grid size {grid_size}x{grid_size}...")
        solution = run_cpp_simulation(grid_size, grid_size)
        
        if solution is None:
            print(f"C++ Grid Convergence Validation FAILED: Simulation failed for grid {grid_size}x{grid_size}.")
            return False
        
        solutions.append(solution)
        print(f"Grid {grid_size}x{grid_size}: solution = {solution}")
    
    # Analyze convergence
    print(f"Grid sizes: {grid_sizes}")
    print(f"Solutions: {solutions}")
    
    # Check for numerical stability
    all_finite = all(np.isfinite(sol) for sol in solutions)
    reasonable_range = all(0 <= sol <= 1 for sol in solutions)
    
    if not (all_finite and reasonable_range):
        print("C++ Grid Convergence Validation FAILED: Numerical instability detected.")
        print(f"All finite: {all_finite}, Reasonable range: {reasonable_range}")
        return False
    
    # Check relative convergence
    ref_solution = solutions[-1]  # Use finest grid as reference
    rel_errors = []
    
    for i, sol in enumerate(solutions[:-1]):
        if abs(ref_solution) > 1e-15:
            rel_error = abs(sol - ref_solution) / abs(ref_solution)
        else:
            rel_error = abs(sol - ref_solution)
        rel_errors.append(rel_error)
    
    print(f"Relative errors: {rel_errors}")
    
    # Check convergence criteria
    max_rel_error = max(rel_errors) if rel_errors else 0
    converges = max_rel_error < 0.01  # Less than 1% difference
    
    if converges:
        print("C++ Grid Convergence Validation PASSED: Algorithm shows correct convergence behavior.")
        return True
    else:
        print(f"C++ Grid Convergence Validation FAILED: Maximum relative error {max_rel_error:.4f} exceeds threshold 0.01")
        return False

if __name__ == "__main__":
    try:
        # Check for command line argument for cpp file
        cpp_file = "program.cpp"
        if len(sys.argv) > 1:
            cpp_file = sys.argv[1]
        
        success = validate_cpp_grid_convergence(cpp_file)
        
        # Cleanup executable
        if os.path.exists("program_cpp_exec"):
            os.unlink("program_cpp_exec")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"C++ Grid Convergence Validation FAILED: Unexpected error: {e}")
        
        # Cleanup executable
        if os.path.exists("program_cpp_exec"):
            os.unlink("program_cpp_exec")
        
        sys.exit(1)
