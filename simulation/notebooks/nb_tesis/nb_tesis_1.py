from poincare import Simulator, System, Variable, Parameter, assign, initial
import numpy as np
import matplotlib.pyplot as plt 

class Pollnau(System):
    N0: Variable = initial(default=0)
    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    P: Parameter = assign(default=1)
    sigma0: Parameter = assign(default=1)
    sigma1: Parameter = assign(default=1)
    k1: Parameter = assign(default=1)
    k2: Parameter = assign(default=1)
    W1: Parameter = assign(default=1)

    n0 = N0.derive() << 0
    n1 = N1.derive() << sigma0 * N0 * P - k1 * N1 -2 * W1 * N1**2 - sigma1 * P * N1
    n2 = N2.derive() << - k2 * N2 + W1 * N1**2 + sigma1 * P * N1

def p_vs_i(pots, sim, **kwargs):
    n1, n2 = np.zeros_like(pots), np.zeros_like(pots)
    for i, pot in enumerate(pots):
        kwargs["model_params"][Pollnau.P] = pot
        res = sim.solve(save_at=kwargs["save_at"],
                        values=kwargs["model_params"])
        n1[i] = res["N1"].iloc[-1]
        n2[i] = res["N2"].iloc[-1]
    return n1, n2