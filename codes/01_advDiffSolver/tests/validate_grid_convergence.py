import sys
import os
import numpy as np
import importlib.util

def load_program_module(python_file="program.py"):
    """Dynamically load the Python program module"""
    # Add parent directory to path to import from src
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    full_path = os.path.join(src_path, python_file)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Python file not found: {full_path}")
    
    # Load module dynamically
    spec = importlib.util.spec_from_file_location("user_program", full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

def run_simulation(nX, nY, program_module):
    input_content = f"{nX} {nY}\ngauss\ndiagonal 0.0\n0.1 400\n"  # Kürzere Zeit für Stabilität
    with open("temp_input.txt", "w") as f:
        f.write(input_content)

    # Access Problem class from the loaded module
    Problem = program_module.Problem
    nHalo = program_module.nHalo
    sIn = program_module.sIn
    
    p = Problem("temp_input.txt")
    p.simulate()
    u = p.u[sIn, sIn]
    return np.mean(u)

def validate_python_grid_convergence(python_file="program.py"):
    """Main validation function for Python implementation"""
    print("Starting Python Grid Convergence Validation...")
    
    # Load the program module
    try:
        program_module = load_program_module(python_file)
    except Exception as e:
        print(f"Failed to load Python program: {e}")
        return False
    
    grid_sizes = [32, 64, 128, 256, 512]
    solutions = [run_simulation(n, n, program_module) for n in grid_sizes]

    # Robustere Konvergenzprüfung
    print(f"Grid sizes: {grid_sizes}")
    print(f"Solutions: {solutions}")

    # Prüfe auf numerische Stabilität
    all_finite = all(np.isfinite(sol) for sol in solutions)
    reasonable_range = all(0 < sol < 1 for sol in solutions)

    if not (all_finite and reasonable_range):
        print("Grid convergence test failed: Numerical instability detected.")
        return False

    # Für sehr genaue Lösungen: Prüfe relative Unterschiede
    ref_solution = solutions[-1]
    rel_errors = [abs(sol - ref_solution) / abs(ref_solution) if abs(ref_solution) > 1e-15 else abs(sol - ref_solution) for sol in solutions[:-1]]

    print(f"Relative errors: {rel_errors}")

    # Prüfe, ob die Fehler klein genug sind (weniger als 1% Unterschied zwischen den Gittern)
    max_rel_error = max(rel_errors) if rel_errors else 0
    converges = max_rel_error < 0.01

    if converges:
        print("Grid Convergence Validation PASSED: Algorithm shows correct convergence behavior.")
        return True
    else:
        print("Grid Convergence Validation FAILED: Algorithm does not show expected convergence behavior.")
        return False

if __name__ == "__main__":
    # Check for command line argument for python file
    python_file = "program.py"
    if len(sys.argv) > 1:
        python_file = sys.argv[1]
    
    success = validate_python_grid_convergence(python_file)
    sys.exit(0 if success else 1)
