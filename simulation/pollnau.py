import matplotlib.pyplot as plt
import numpy as np
from poincare import Derivative, Parameter, Simulator, System, Variable, assign, initial

class GSA(System):
    #lmb: Parameter = assign(default=980)
    #h: Parameter = assign(default=1)
    #c: Parameter = assign(default=1)
    #wp: Parameter = assign(default=1)
    #P: Parameter = assign(default=1)
    #rho: Parameter = lmb*P/(np.pi*c*h*wp**2)
    rho: Parameter = assign(default=1)
    sigma0: Parameter = assign(default=1)

    N0: Variable = initial(default=1000)
    N1: Variable = initial(default=0)

    gsa = N1.derive() << rho * sigma0 * N0

class ETU(System):
    W1: Parameter = assign(default=1)
    A1: Parameter = assign(default=1)
    A2: Parameter = assign(default=1)

    N0: Variable = initial(default=1000)
    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    etu1 = N1.derive() << - 2 * W1 * N1**2 - A1 * N1
    etu2 = N2.derive() << W1 * N1**2 - A2 * N2

class UCNP(System):
    N0: Variable = initial(default=1000)
    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    W1: Parameter = assign(default=1)
    A1: Parameter = assign(default=1)
    A2: Parameter = assign(default=1)
    rho: Parameter = assign(default=1)
    sigma0: Parameter = assign(default=1)

    etu = ETU(N0=N0, N1=N1, N2=N2, A1=A1, A2=A2, W1=W1)
    gsa = GSA(N0=N0, N1=N1, rho=rho, sigma0=sigma0)

if __name__ == "__main__":
    sim = Simulator(UCNP)
    result = sim.solve(times=np.linspace(0, 50, 1000))
    result.plot()
    plt.show()

