#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick convergence test for the numpy code
"""
import os, sys
sys.path.append(os.path.dirname(os.getcwd()))
from src.program import Problem, sIn, np

nX0 = 32
nGrids = 3
tEnd = 0.1

for nu in [0, 0.001]:   # try two diffusion coefficients

    nXRef = nX0*2**nGrids
    with open("input.txt", 'w') as f:
        f.write(f"{nXRef} {nXRef} gauss diagonal {nu} {tEnd} {nXRef}\n")
    p = Problem("input.txt")
    p.simulate()
    uRef = p.u[sIn, sIn]

    errors = {}
    for i in range(nGrids):
        nX = nX0*2**i
        with open("input.txt", 'w') as f:
            f.write(f"{nX} {nX} gauss diagonal {nu} {tEnd} {nX}\n")
        p = Problem("input.txt")
        p.simulate()
        uNum = p.u[sIn, sIn]

        r = nXRef//nX
        diff = uRef[::r, ::r] - uNum
        errors[nX] = np.sqrt(np.mean(diff**2))

    conv = {}
    for i in range(nGrids-1):
        nX1 = nX0*2**i
        nX2 = 2*nX1
        conv[nX2] = np.log2(errors[nX1]/errors[nX2])

    print("Convergence order :")
    for nX, order in conv.items():
        err1, err2 = errors[nX//2], errors[nX]
        print(f" -- grid {nX} : {order} ({err1:1.2e} -> {err2:1.2e})")
        assert abs(order-4) < 0.3, f"numerical order ({order}) to different from theoretical order (4)"
