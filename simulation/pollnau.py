import matplotlib.pyplot as plt
import numpy as np
from poincare import Derivative, Parameter, Simulator, System, Variable, assign, initial
import matplotlib as mpl
plt.style.use('seaborn')
mpl.rcParams['figure.dpi'] = 200
mpl.rcParams['legend.fontsize'] = 15
mpl.rcParams['axes.labelsize'] = 15
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10

class GSA(System):
    #lmb: Parameter = assign(default=980)
    #h: Parameter = assign(default=1)
    #c: Parameter = assign(default=1)
    #wp: Parameter = assign(default=1)
    #P: Parameter = assign(default=1)
    #rho: Parameter = lmb*P/(np.pi*c*h*wp**2)
    rate: Parameter = assign(default=1)

    N0: Variable = initial(default=1000)
    N1: Variable = initial(default=0)

    gsa = N1.derive() << rate * N0
    antigsa = N0.derive() << - rate * N0

class ETU(System):
    W1: Parameter = assign(default=1)
    A1: Parameter = assign(default=1)
    A2: Parameter = assign(default=1)

    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    etu1 = N1.derive() << - 2 * W1 * N1**2 - A1 * N1
    etu2 = N2.derive() << W1 * N1**2 - A2 * N2
    antietu1 = N2.derive() << W1 * N1**2 + A1 * N1
    antietu2 = N1.derive() << + A2 * N2

class ESA(System):
    rate: Parameter = assign(default=1)

    N0: Variable = initial(default=0)
    N1: Variable = initial(default=0)
    esa = GSA(rate=rate, N0=N0, N1=N1)

class UCNP(System):
    N0: Variable = initial(default=1000)
    N1: Variable = initial(default=0)
    N2: Variable = initial(default=0)

    W1: Parameter = assign(default=1)
    A1: Parameter = assign(default=1)
    A2: Parameter = assign(default=1)
    rate_gsa: Parameter = assign(default=1)
    rate_esa: Parameter = assign(default=0)

    etu = ETU(N1=N1, N2=N2, A1=A1, A2=A2, W1=W1)
    gsa = GSA(N0=N0, N1=N1, rate=rate_gsa)
    esa = ESA(N0=N1, N1=N2, rate=rate_esa)
    # Creo que debería agregar stimulated y spontaneous emission
    # (No cambia el modelo pero ahora están absorbidas por los parámetros de ETU)


if __name__ == "__main__":
    intensidades = []
    potencias = np.linspace(0, 100, 100)
    for pot in potencias:
        sim = Simulator(UCNP, transform={"N":UCNP.N0 + UCNP.N1 + UCNP.N2, "N1": UCNP.N1, "N2":UCNP.N2})
        result = sim.solve(times=np.linspace(0, 50, 1000))
        Nest = result[["N1", "N2"]].iloc[-1]
        N1est, N2est = Nest[0], Nest[1]
        intensidad = N2est/N1est
        intensidades.append(intensidad)

    print(intensidades)
    plt.loglog(potencias, intensidades)
    #result.plot()
    plt.show()
    #plt.show()
