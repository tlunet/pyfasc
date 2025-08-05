# 2D Advection Diffusion solver

- [program.cpp](./program.cpp) : semi-optimized implementation in C++
- [program.py](./program.py) : Numpy-based implementation in Python, produce also an image with the initial and final 2D fields.

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
- one integer for the number of time-steps (here `125`)

## Base configurations for benchmarking

### Simple Gaussian diagonal advection, half time

Input file :

```
32 32
gauss diagonal 0.0
0.25 8
```

Initial and final field (produced by [program.py](./program.py)) :

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