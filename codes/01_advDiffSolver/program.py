#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from time import time
import matplotlib.pyplot as plt

nHalo = 2
sIn = slice(nHalo, -nHalo)
def updateHalo(u):
    nH2 = 2*nHalo
    u[0:nHalo, sIn] = u[-nH2:-nHalo, sIn]
    u[-nHalo:, sIn] = u[nHalo:2*nHalo, sIn]
    u[sIn, 0:nHalo] = u[sIn, -nH2:-nHalo]
    u[sIn, -nHalo:] = u[sIn, nHalo:2*nHalo]


cAdv = np.array([ 1./12, -2./3,  0,    2./3, -1./12])
cDif = np.array([-1./12,  4./3, -5./2, 4./3, -1./12])

class Problem:

    def __init__(self, fileName):
        with open(fileName, "r") as f:
            inputs = f.read().split()

        self.nX, self.nY = [int(inputs.pop(0)) for _ in range(2)]
        self.initType, self.flowType = [inputs.pop(0) for _ in range(2)]
        self.viscosity, self.tEnd = [float(inputs.pop(0)) for _ in range(2)]
        self.nSteps = int(inputs.pop(0))

        self.setupSolution()
        self.setupCoeffs()

        # Additional variable
        self.t = 0
        self.tmp = np.empty((self.nX, self.nY))

    @property
    def grid(self):
        x = np.linspace(0, 1, self.nX, endpoint=False)[:, None]
        y = np.linspace(0, 1, self.nY, endpoint=False)[None, :]
        return x, y


    def setupSolution(self):
        self.u = u = np.zeros((self.nX+2*nHalo, self.nY+2*nHalo))
        initType, (x, y) = self.initType, self.grid

        if initType == "gauss":
            u[sIn, sIn] = np.exp(-200*((x-0.5)**2 + (y-0.5)**2))
        elif initType == "square":
            u[sIn, sIn] = (x > 0.2)*(x < 0.3)*(y > 0.2)*(y < 0.3)
        elif initType == "cross":
            u[sIn, sIn] = 0.5*(np.exp(-200*(x-0.5)**2) + np.exp(-200*(y-0.5)**2))
        elif initType == "cross2":
            u[sIn, sIn] = np.maximum(np.exp(-200*(x-0.5)**2), np.exp(-200*(y-0.5)**2))
        else:
            raise ValueError(f"unknown initType : {initType}")


    def setupCoeffs(self):
        self.coeffs = coeffs = np.zeros((2, 2*nHalo+1, self.nX, self.nY))

        flowType, viscosity = self.flowType, self.viscosity
        dX, dY, (x, y) = 1/self.nX, 1/self.nY, self.grid

        if flowType == "diagonal":
            vX, vY = 1, 1
        elif flowType == "circular":
            r = np.hypot(x-0.5, y-0.5)
            phi= np.arctan2(y-0.5, x-0.5)
            rho = np.exp(-10*r**2)
            vX = -r*2*np.pi*np.sin(phi)*rho
            vY =  r*2*np.pi*np.cos(phi)*rho
        elif flowType == "circular2":
            r = np.hypot(x-0.5, y-0.5)
            phi= np.arctan2(y-0.5, x-0.5)
            rho = np.exp(-5*r**2)
            vX = -r*2*np.pi*np.sin(phi)*np.sin(4*np.pi*r)*rho
            vY =  r*2*np.pi*np.cos(phi)*np.sin(4*np.pi*r)*rho
        else:
            vX = vY = 0
        coeffs[0] = -vX*cAdv[:, None, None]/dX + viscosity*cDif[:, None, None]/dX**2
        coeffs[1] = -vY*cAdv[:, None, None]/dY + viscosity*cDif[:, None, None]/dY**2


    def computeRHS(self, uEval, t, out):
        coeffs, tmp, nX, nY = self.coeffs, self.tmp, self.nX, self.nY

        updateHalo(uEval)

        out[:] = 0
        for s in range(2*nHalo+1):

            # Derivative in X
            np.copyto(tmp, uEval[s:nX+s, sIn])
            tmp *= coeffs[0, s]
            out += tmp

            # Derivative in Y
            np.copyto(tmp, uEval[sIn, s:nY+s])
            tmp *= coeffs[1, s]
            out += tmp


    def simulate(self):
        u0, nX, nY = self.u, self.nX, self.nY
        uEval = np.zeros_like(u0)

        u1 = np.empty((nX, nY))
        np.copyto(u1, u0[sIn, sIn])
        k = np.zeros_like(u1)

        dt = self.tEnd/self.nSteps
        tBeg = time()
        for i in range(self.nSteps):
            t = self.t

            self.computeRHS(u0, t, k)
            np.copyto(uEval[sIn, sIn], k)
            k *= dt/6; u1 += k

            uEval *= dt/2
            uEval += u0
            self.computeRHS(uEval, t+dt/2, k)
            np.copyto(uEval[sIn, sIn], k)
            k *= dt/3; u1 += k

            uEval *= dt/2
            uEval += u0
            self.computeRHS(uEval, t+dt/2, k)
            np.copyto(uEval[sIn, sIn], k)
            k *= dt/3; u1 += k

            uEval *= dt
            uEval += u0
            self.computeRHS(uEval, t+dt, k)
            k *= dt/6; u1 += k

            np.copyto(u0[sIn, sIn], u1)
            self.t = (i+1)*dt

        tWall = time()-tBeg
        print(f"tWall : {tWall}")
        print(f"tWall/DoF : {tWall/(self.nSteps*nX*nY)}")


# Simulation
p = Problem("input.txt")
u0 = p.u.copy()

p.simulate()
uEnd = np.abs(p.u)  # remove some negative artefacts for plots

# Plotting
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

grid = [x.ravel() for x in p.grid]

c0 = ax[0].contourf(*grid, u0[sIn, sIn])
ax[0].set_title('T=0')
ax[0].set_xlabel('X')
ax[0].set_ylabel('Y')
fig.colorbar(c0, ax=ax[0], orientation='vertical')

c1 = ax[1].contourf(*grid, uEnd[sIn, sIn])
ax[1].set_title(f'T={p.tEnd}')
ax[1].set_xlabel('X')
ax[1].set_ylabel('Y')
fig.colorbar(c1, ax=ax[1], orientation='vertical')

plt.tight_layout()
plt.savefig("solution.png")

# plt.show()
