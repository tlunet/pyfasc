"""
Run Python implementation with 256x256, 128x128 and 64x64 grids.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path


def main(temp_dir=None):
    base_dir = Path(__file__).parent.parent
    py_file = base_dir / "src" / "program.py"
    
    # Use provided temp directory or create new one
    if temp_dir:
        results_dir = Path(temp_dir)
    else:
        results_dir = Path(tempfile.mkdtemp())
    
    # Run with different grid sizes
    for grid_size in [256, 128, 64]:
        print(f"Running {grid_size}x{grid_size}...")
        
        # Create input
        config = f"{grid_size} {grid_size} gauss diagonal 0.001 0.1 32\n"
        input_file = base_dir / "input.txt"
        input_file.write_text(config)
        
        # Execute
        os.chdir(base_dir)
        subprocess.run(["python", str(py_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Move results
        shutil.move(base_dir / "uInit.txt", results_dir / f"uInit_py_{grid_size}x{grid_size}.txt")
        shutil.move(base_dir / "uEnd.txt", results_dir / f"uEnd_py_{grid_size}x{grid_size}.txt")
    
    print("Done!")
    
    # Return temp directory path
    return str(results_dir)


if __name__ == "__main__":
    main()
