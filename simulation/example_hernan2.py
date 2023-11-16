from poincare import Variable, System, Parameter, assign, Simulator, Independent
from poincare.types import Initial
from poincare._utils import class_and_instance_method
from typing_extensions import dataclass_transform
import poincare.compile

import pint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ureg = pint.get_application_registry()

DIM_WAVELENGTH = {'[length]': 1}
DIM_WAVENUMBER = {'[length]': -1}
DIM_FREQUENCY = {'[time]': -1}
DIM_ENERGY = ureg.get_dimensionality("eV")


class State(Variable):
    
    energy: pint.Quantity


def initial(energy: float | pint.Quantity, *, default: Initial | None = None, init: bool = True) -> State:
    state = State(initial=default)

    dim = ureg.get_dimensionality(energy)

    if dim == {}:
        energy = energy * ureg.electron_volt
        
    elif dim in (DIM_WAVELENGTH, DIM_WAVENUMBER, DIM_FREQUENCY):
        with ureg.context("spectroscopy"):
            energy = energy.to("eV")

    elif dim != DIM_ENERGY:
        raise ValueError("energy must be a float (which is interpreted as eV) or have dimensionality of wavelength, wavenumber, frequency and energy, not {dim}")

    assert isinstance(energy, pint.Quantity)
    state.energy = energy
    return state


@dataclass_transform(
    field_specifiers=(initial, )
)
class FluorescenceTransition(System):

    ground: State = initial(0., default=0)
    excited: State = initial(0., default=0)

    rate: Parameter = assign(default=0)

    val = rate * excited

    down = ground.derive() << val
    up = excited.derive() << -val

    @property
    def energy_difference(self) -> pint.Quantity:
        return self.excited.energy - self.ground.energy

@dataclass_transform(
    field_specifiers=(initial, )
)
class StateAbsorption(System):
    
    ground: State = initial(0., default=0)
    excited: State = initial(0., default=0)

    rate: Parameter = assign(default=0)

    val = rate * ground

    down = ground.derive() << - val
    up = excited.derive() << val

    @property
    def energy_difference(self) -> pint.Quantity:
        return self.excited.energy - self.ground.energy

@dataclass_transform(
    field_specifiers=(initial, )
)
class ETU(System):

    donator: State = initial(0., default=0)
    acceptor: State = initial(0., default=0)
    relaxation: State = initial(0., default=0)

    rate: Parameter = assign(default=0)

    val = rate * donator**2

    donation = donator.derive() << - 2 * val
    accept = acceptor.derive() << val
    relax = relaxation.derive() << val

@dataclass_transform(
    field_specifiers=(initial, )
)
class FluorescentSystem(System, abstract=True):

    @class_and_instance_method
    def fluorescence_spectra(cls, unit: str | pint.Unit) -> dict[pint.Quantity, Parameter]:
        dim = ureg.get_dimensionality(unit)

        if dim == DIM_ENERGY:
            # energy
            return {
                transition.energy_difference.to(unit): transition.val
                for transition in cls._yield(FluorescenceTransition)
            }
        
        elif dim == DIM_WAVENUMBER:
            # wavenumber
            with ureg.context("spectroscopy"):
                return {
                    transition.energy_difference.to(unit): transition.val
                    for transition in cls._yield(FluorescenceTransition)
                }
            
        elif dim == DIM_WAVELENGTH:
            # wavelength
            with ureg.context("spectroscopy"):
                return {
                    transition.energy_difference.to(unit): transition.val
                    for transition in cls._yield(FluorescenceTransition)
                }
            
        elif dim == DIM_FREQUENCY:
            # frequency
            with ureg.context("spectroscopy"):
                return {
                    transition.energy_difference.to(unit): transition.val
                    for transition in cls._yield(FluorescenceTransition)
                } 
            
        else:
            raise ValueError(f"Cannot provide the spectra in {unit} ({dim})")
        

class Example(FluorescentSystem):
    N0: State = initial(0, default=1_000)
    N1: State = initial(490 * ureg.nm, default=0)
    N2: State = initial(980 * ureg.nm, default=0)

    laser: Parameter = assign(default=0)
    sigma0: Parameter = assign(default=0)
    sigma1: Parameter = assign(default=0)
    k1: Parameter = assign(default=0)
    k2: Parameter = assign(default=0)
    ketu: Parameter = assign(default=0)

    N1N0 = FluorescenceTransition(ground=N0, excited=N1, rate=k1)
    N0N1 = StateAbsorption(ground=N0, excited=N1, rate=laser * sigma0)
    #N2_const = N2.derive() << 0
    N1etuN2 = ETU(donator=N1, acceptor=N2, relaxation=N0, rate=ketu)
    N1esaN2 = StateAbsorption(ground=N1, excited=N2, rate=laser * sigma1)
    #N2N1 = FluorescenceTransition(ground=N1, excited=N2, rate=1)
    N2N0 = FluorescenceTransition(ground=N0, excited=N2, rate=k2)

def find_closest_index(array, value):
    return (np.abs(array - value)).argmin()


def cw_excitation(simulator, total_time, model_params):
    times = np.linspace(0, total_time, 10000)
    partial_result = simulator.solve(
        save_at=times,
        values=model_params
    )
    return partial_result

def simple_pulsed_excitation(simulator, period, duty_cycle,
                            n_pulses, stabilization_time,
                            model_params):
    assert 0 < duty_cycle <= 1
    if duty_cycle == 1:
        return cw_excitation(simulator, period * n_pulses, model_params) 
    times = np.linspace(0, period * n_pulses + stabilization_time, 10000)
    t_on, t_off = period*duty_cycle, period*(1-duty_cycle)
    result = pd.DataFrame()
    t_initial_idx = 0
    for i in range(2*n_pulses):
        t_sim = t_on if i%2 == 0 else t_off
        t_final_idx = find_closest_index(times, times[t_initial_idx] + t_sim)
        laser = ((i+1)%2) * pot
        partial_result = simulator.solve(
            save_at=times[t_initial_idx:t_final_idx],
            values=model_params
        )
        N0 = partial_result["N0"].iloc[-1]
        N1 = partial_result["N1"].iloc[-1]
        N2 = partial_result["N2"].iloc[-1]
        partial_result["laser"] = np.repeat(laser, t_final_idx - t_initial_idx)
        result = pd.concat([result, partial_result])
        t_initial_idx = t_final_idx + 1

    partial_result = simulator.solve(
        save_at=times[t_initial_idx:],
        values=model_params
    )
    partial_result["laser"] = 0
    return pd.concat([result, partial_result])

print(Example.fluorescence_spectra("nm"))
model_params_etu = {
    Example.N1:0,
    Example.N2:0,
    Example.N0:1000,
    Example.laser:1,
    Example.sigma0:1,
    Example.sigma1:5E-1,
    Example.ketu:2,
    Example.k1:1e5,
    Example.k2:1e5
    }

model_params_esa = {
    Example.N1:0,
    Example.N2:0,
    Example.N0:1000,
    Example.laser:1,
    Example.sigma0:1,
    Example.sigma1:1e-4,
    Example.ketu:1e-2,
    Example.k1:1e5,
    Example.k2:1e5
    }


for model_params in (model_params_esa, model_params_etu):
    kwargs = {
        "simulator":Simulator(Example),
        "period":10,
        "duty_cycle":1,
        "n_pulses":1,
        "stabilization_time":0,
        "model_params": model_params
    }

    pots = np.geomspace(1e-3, 1e4, num=100)
    n1, n2 = np.zeros_like(pots), np.zeros_like(pots)
    for i, pot in enumerate(pots):
        model_params[Example.laser] = pot
        result = simple_pulsed_excitation(**kwargs)
        nt = result["N1"].iloc[-1] + result["N2"].iloc[-1] + result["N0"].iloc[-1]
        n1[i] = result["N1"].iloc[-1] / nt
        n2[i] = result["N2"].iloc[-1] / nt
        result.plot()
        plt.show()
    #result["E"] = result["N0"] + result["N1"] + 2*result["N2"]
    #result["laser"] = result["laser"] * max(result["N1"].max(), result["N2"].max())
    #result.loc[:, result.columns.difference(["E", "N0"])].plot()
    #result.plot()
    #plt.show()
    result["N"] = result["N0"] + result["N1"] + result["N2"]
    a = poincare.compile.build_first_order_symbolic_ode(Example)

    plt.loglog(pots, n1, label="N1")
    plt.loglog(pots, n2, label="N2")
    plt.legend()

    total = 0
    for key, val in a.func.items():
        total = total + val
        print(f"d{key}/dt = {val}")
plt.show()
