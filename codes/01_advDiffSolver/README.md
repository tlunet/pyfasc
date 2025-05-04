# 2D Advection Diffusion solver

- [program.cpp](./program.cpp) : semi-optimized implementation in C++
- [program.py](./program.py) : Numpy-based implementation in Python

## How to run

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
- one integer for the number of time-steps (here `12`)
