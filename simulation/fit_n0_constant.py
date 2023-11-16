from scipy.optimize import curve_fit, basinhopping, brute, differential_evolution, shgo, dual_annealing, direct
from example_hernan3 import Example, Bujjamer, model_params_etu
import numpy as np
import matplotlib.pyplot as plt
from poincare import Simulator
import example_hernan3

simulator = Simulator(Example)

def p_vs_i(x):
    sigma0, sigma1, ketu, k1, k2 = x
    pots = np.geomspace(1e-3, 1e4, num=100)
    model_params = {
        Example.N1:1.2e5,
        Example.N2:1.2e5,
        Example.N0:1.2e5,
        Example.sigma0:sigma0,
        Example.sigma1:sigma1,
        Example.ketu:ketu,
        Example.k1:k1,
        Example.k2:k2
        }
    n1, n2 = np.zeros_like(pots), np.zeros_like(pots)
    for i, pot in enumerate(pots):
        model_params[Example.laser] = pot
        times = np.linspace(0, 10.0, 250)
        result = simulator.solve(save_at=times, values=model_params)
        #nt = result["N1"].iloc[-1] + result["N2"].iloc[-1] + result["N0"].iloc[-1]
        n1[i] = result["N1"].iloc[-1]# / nt
        n2[i] = result["N2"].iloc[-1]# / nt
    return np.linalg.norm([
            np.linalg.norm(n1-example_hernan3.n1),
            np.linalg.norm(n2 - example_hernan3.n2)
            ])

model_params_etu = {
    #Example.N1:1e5,
    #Example.N2:1e5,
    #Example.N0:1e5,
    Example.sigma0:1e1,
    Example.sigma1:5E-1,
    Example.ketu:6e6,
    Example.k1:2e6,
    Example.k2:1e7
    }

pots = np.geomspace(1e-3, 1e4, num=100)
#data = np.concatenate((n1, n2))
p0 = list(model_params_etu.values())
print(p0,type(p0) )
bounds = []
for i, i0 in enumerate(p0):
    bounds.append((i0 - 0.5*i0, i0+0.5*i0))
result = differential_evolution(p_vs_i, bounds=bounds)
print(result)
