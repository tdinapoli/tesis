from poincare import Variable, System, Parameter, assign, Simulator, Independent, initial
from poincare.types import Initial
from poincare._utils import class_and_instance_method
from typing_extensions import dataclass_transform
import poincare.compile

import pint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Bujjamer(System):

    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    N0: Parameter = assign(default=0)
    rhoP: Parameter = assign(default=0)
    sigma0: Parameter = assign(default=0)
    sigma1: Parameter = assign(default=0)
    ketu: Parameter = assign(default=0)
    k1: Parameter = assign(default=0)
    k2: Parameter = assign(default=0)

    N1_eq = N1.derive() << rhoP * sigma0 * N0 - 2 * ketu * N1**2 - k1 * N1
    N2_eq = N2.derive() << rhoP * sigma1 * N1 + ketu * N1**2 - k2 * N2


sim = Simulator(Bujjamer)
times = np.linspace(0, 10, 10000)
values = {
    Bujjamer.N1:1,
    Bujjamer.N2:1,
    Bujjamer.N0:1,
    Bujjamer.rhoP:1,
    Bujjamer.sigma0:1,
    Bujjamer.sigma1:5E-1,
    Bujjamer.ketu:2,
    Bujjamer.k1:2,
    Bujjamer.k2:2
}

rvals = np.geomspace(1e-3, 1e4, num=100)
n1, n2 = np.zeros_like(rvals), np.zeros_like(rvals)
for i, r in enumerate(rvals):
    values[Bujjamer.rhoP] = r
    result = sim.solve(save_at=times, values=values)
    result.plot()
    plt.show()
    n1[i] = result["n1"].iloc[-1]
    n2[i] = result["n2"].iloc[-1]
plt.loglog(rvals, n1, label="N1")
plt.loglog(rvals, n2, label="N2")
plt.legend()
plt.show()

values = {
    Bujjamer.N1:1,
    Bujjamer.N2:1,
    Bujjamer.N0:1,
    Bujjamer.rhoP:1,
    Bujjamer.sigma0:1,
    Bujjamer.sigma1:1e-4,
    Bujjamer.ketu:1,
    Bujjamer.k1:2,
    Bujjamer.k2:2
}

rvals = np.geomspace(1e-3, 1e4, num=100)
n1, n2 = np.zeros_like(rvals), np.zeros_like(rvals)
for i, r in enumerate(rvals):
    values[Bujjamer.rhoP] = r
    result = sim.solve(save_at=times, values=values)
    n1[i] = result["N1"].iloc[-1]
    n2[i] = result["N2"].iloc[-1]
plt.loglog(rvals, n1, label="N1")
plt.loglog(rvals, n2, label="N2")
plt.legend()
plt.show()

