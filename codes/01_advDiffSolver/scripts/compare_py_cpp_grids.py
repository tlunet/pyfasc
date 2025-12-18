"""
Compare Python and C++ results for different grid sizes.
"""

import numpy as np
from pathlib import Path


def main(results_dir=None):
    if results_dir:
        results_dir = Path(results_dir)
    else:
        results_dir = Path(__file__).parent.parent / "results"
    
    all_match = True
    
    # Compare results for each grid size
    for grid_size in [256, 128, 64]:
        print(f"\n{grid_size}x{grid_size} grid:")
        
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
        print(f"  Match: {grid_match}")
        
        all_match = all_match and grid_match
    
    print(f"\nAll grid sizes match: {all_match}")


if __name__ == "__main__":
    main()
