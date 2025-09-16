# 2D Advection Diffusion solver

## Project Structure

```
01_advDiffSolver/
├── src/                    # Source code files
│   ├── *.py               # Python implementations (any .py file supported)
│   ├── *.cpp              # C++ implementations (any .cpp file supported)
│   └── *.jl               # Julia implementations
├── tests/                  # Test and validation scripts
│   ├── validate.py
│   ├── validate_grid_convergence.py
│   ├── validate_grid_convergence_cpp.py
│   └── diagnosetool.py    # Performance diagnosis tool
├── config/                 # Configuration/input files
│   ├── input.txt          # Single input configuration
│   ├── inputs.txt         # Multiple input configurations
│   ├── test_inputs.txt
│   └── test_multi_grid.txt
├── results/                # Generated results (plots, animations, metrics)
│   ├── algorithm_animation.gif
│   ├── solution.png
│   └── all_metrics.json
├── outputs/                # Temporary output files (uEnd.txt, uInit.txt)
├── docs/                   # Documentation files
├── img/                    # Static images for README
├── gif_frames/            # Temporary frames for GIF generation
├── app.py                 # Streamlit web interface (main entry point)
└── README.md
```

## Implementation Files

The system now supports **any filename** for Python (`.py`) and C++ (`.cpp`) files:

- [src/program.cpp](./src/program.cpp) : semi-optimized implementation in C++
- [src/program.py](./src/program.py) : Numpy-based implementation in Python, produce also an image with the initial and final 2D fields.
- [src/program.jl](./src/program.jl) : Julia implementation

You can now use any filename you prefer (e.g., `my_solver.py`, `advection_diffusion.cpp`, etc.).

## How to run

### Using the Streamlit Web Interface

The application is designed to be used through the Streamlit web interface:

```bash
streamlit run app.py
```

This provides a complete interface for:
- Writing and editing Python/C++ code
- Configuring benchmark parameters
- Running performance comparisons
- Visualizing results
- Exporting data

### Manual Execution (for development)

📜 _Requires an `input.txt` file to provide the simulation arguments, for instance :_

```
512 512
cross2 circular2 0
0.125 125
```

- two integers for $N_x$ and $N_y$ (here `512`, `512`)
- one string for the initialization type (here `cross2`)
- one string for the flow type (here `circular2`)
- one float for the diffusion coefficient, or viscosity (here `0`)
- one float for the final time of simulation (here `0.125`)
- one integer for the number of time-steps (here `125`)

## Base configurations for benchmarking

### Simple Gaussian diagonal advection, half time

Input file :

```
32 32
gauss diagonal 0.0
0.25 8
```

Initial and final field (produced by [src/program.py](./src/program.py)) :

<div style="display: flex; justify-content: center;">
    <img src="./img/B1_solution.png" alt="B1_solution" style="width: 600px;" />
</div>

---

Note that if we increase the computation time (and the number of time steps accordingly), we get for

```
32 32
gauss diagonal 0.0
0.5 16
```

<div style="display: flex; justify-content: center;">
    <img src="./img/B1_solution_2.png" alt="B1_solution_2" style="width: 600px;" />
</div><br>

and for

```
32 32
gauss diagonal 0.0
1 32
```

<div style="display: flex; justify-content: center;">
    <img src="./img/B1_solution_3.png" alt="B1_solution_3" style="width: 600px;" />
</div>