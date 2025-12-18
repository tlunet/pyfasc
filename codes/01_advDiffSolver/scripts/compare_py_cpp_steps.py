"""
Compare Python and C++ results for different time steps.
"""

import numpy as np
from pathlib import Path


def main(results_dir=None):
    if results_dir:
        results_dir = Path(results_dir)
    else:
        results_dir = Path(__file__).parent.parent / "results"
    
    all_match = True
    
    # Compare results for each time step configuration
    for nsteps in [16, 32, 64]:
        print(f"\n{nsteps} steps:")
        
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
        print(f"  Match: {step_match}")
        
        all_match = all_match and step_match
    
    print(f"\nAll steps match: {all_match}")


if __name__ == "__main__":
    main()
