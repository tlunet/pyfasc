"""
Combined validation test: C++ and Python implementations for different grid sizes and time steps.
Returns True if all tests pass, False otherwise.
"""

import sys
import shutil
import importlib.util
from pathlib import Path
import numpy as np


def import_module_from_path(name, path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare_grids(results_dir):
    """Compare Python and C++ results for different grid sizes."""
    
    all_match = True
    
    for grid_size in [256, 128, 64]:
        print(f"\n{grid_size}x{grid_size} grid:")
        
        try:
            # Load results
            py_init = np.loadtxt(results_dir / f"uInit_py_{grid_size}x{grid_size}.txt")
            py_end = np.loadtxt(results_dir / f"uEnd_py_{grid_size}x{grid_size}.txt")
            cpp_init = np.loadtxt(results_dir / f"uInit_cpp_{grid_size}x{grid_size}.txt")
            cpp_end = np.loadtxt(results_dir / f"uEnd_cpp_{grid_size}x{grid_size}.txt")
            
            # Calculate differences
            init_diff = np.abs(py_init - cpp_init)
            end_diff = np.abs(py_end - cpp_end)
            
            print(f"  Initial - Max diff: {init_diff.max():.2e}, Mean diff: {init_diff.mean():.2e}")
            print(f"  Final   - Max diff: {end_diff.max():.2e}, Mean diff: {end_diff.mean():.2e}")
            
            # Check with reasonable tolerance
            init_match = np.allclose(py_init, cpp_init, rtol=1e-6, atol=1e-6)
            end_match = np.allclose(py_end, cpp_end, rtol=1e-6, atol=1e-6)
            
            grid_match = init_match and end_match
            print(f"  Match: {'✓ PASS' if grid_match else '✗ FAIL'}")
            
            all_match = all_match and grid_match
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Match: ✗ FAIL")
            all_match = False
    
    print(f"\nGrid validation result: {'✓ PASS' if all_match else '✗ FAIL'}")
    return all_match


def compare_steps(results_dir):
    """Compare Python and C++ results for different time steps."""
    
    all_match = True
    
    for nsteps in [16, 32, 64]:
        print(f"\n{nsteps} steps:")
        
        try:
            # Load results
            py_init = np.loadtxt(results_dir / f"uInit_py_{nsteps}steps.txt")
            py_end = np.loadtxt(results_dir / f"uEnd_py_{nsteps}steps.txt")
            cpp_init = np.loadtxt(results_dir / f"uInit_cpp_{nsteps}steps.txt")
            cpp_end = np.loadtxt(results_dir / f"uEnd_cpp_{nsteps}steps.txt")
            
            # Calculate differences
            init_diff = np.abs(py_init - cpp_init)
            end_diff = np.abs(py_end - cpp_end)
            
            print(f"  Initial - Max diff: {init_diff.max():.2e}, Mean diff: {init_diff.mean():.2e}")
            print(f"  Final   - Max diff: {end_diff.max():.2e}, Mean diff: {end_diff.mean():.2e}")
            
            # Check with reasonable tolerance
            init_match = np.allclose(py_init, cpp_init, rtol=1e-6, atol=1e-6)
            end_match = np.allclose(py_end, cpp_end, rtol=1e-6, atol=1e-6)
            
            step_match = init_match and end_match
            print(f"  Match: {'✓ PASS' if step_match else '✗ FAIL'}")
            
            all_match = all_match and step_match
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Match: ✗ FAIL")
            all_match = False
    
    print(f"\nTime steps validation result: {'✓ PASS' if all_match else '✗ FAIL'}")
    return all_match


def main():
    """Run combined validation test."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    
    # Import modules
    run_cpp_grids = import_module_from_path("run_cpp_multi_grids", scripts_dir / "run_cpp_multi_grids.py")
    run_py_grids = import_module_from_path("run_py_multi_grids", scripts_dir / "run_py_multi_grids.py")
    run_cpp_steps = import_module_from_path("run_cpp_multi_steps", scripts_dir / "run_cpp_multi_steps.py")
    run_py_steps = import_module_from_path("run_py_multi_steps", scripts_dir / "run_py_multi_steps.py")
    
    print("="*60)
    print("COMBINED VALIDATION TEST")
    print("="*60)
    
    all_tests_passed = True
    
    try:
        # ===== GRID SIZE TESTS =====
        print("\n" + "="*60)
        print("GRID SIZE VALIDATION")
        print("="*60)
    
        print("\n[1/6] Running C++ implementation (grid sizes)...")
        temp_dir_grids = run_cpp_grids.main()
        temp_dir_grids = Path(temp_dir_grids)
        
        print("\n[2/6] Running Python implementation (grid sizes)...")
        run_py_grids.main(temp_dir_grids)
        
        print("\n[3/6] Comparing grid size results...")
        grids_passed = compare_grids(temp_dir_grids)
        all_tests_passed = all_tests_passed and grids_passed
        
        # Cleanup grid tests
        print("\nCleaning up grid test files...")
        shutil.rmtree(temp_dir_grids)
        
        # ===== TIME STEPS TESTS =====
        print("\n" + "="*60)
        print("TIME STEPS VALIDATION")
        print("="*60)

        print("\n[4/6] Running C++ implementation (time steps)...")
        temp_dir_steps = run_cpp_steps.main()
        temp_dir_steps = Path(temp_dir_steps)
        
        print("\n[5/6] Running Python implementation (time steps)...")
        run_py_steps.main(temp_dir_steps)
        
        print("\n[6/6] Comparing time step results...")
        steps_passed = compare_steps(temp_dir_steps)
        all_tests_passed = all_tests_passed and steps_passed
        
        # Cleanup step tests
        print("\nCleaning up time step test files...")
        shutil.rmtree(temp_dir_steps)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        all_tests_passed = False
    
    # Final result
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"All tests passed: {all_tests_passed}")
    print("="*60)
    
    return all_tests_passed


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
