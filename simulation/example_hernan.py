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
    ratio: Parameter = assign(default=1)

    val = rate * excited

    down = ground.derive() << ratio * val
    up = excited.derive() << - val

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

    N1N0 = FluorescenceTransition(ground=N0, excited=N1, rate=1, ratio=1)
    N0N1 = StateAbsorption(ground=N0, excited=N1, rate=laser)
    #N2_const = N2.derive() << 0
    N1etuN2 = ETU(donator=N1, acceptor=N2, relaxation=N0, rate=1)
    #N1esaN2 = StateAbsorption(ground=N1, excited=N2, rate=laser)
    #N2N1 = FluorescenceTransition(ground=N1, excited=N2, rate=1, ratio=1)
    N2N0 = FluorescenceTransition(ground=N0, excited=N2, rate=1, ratio=2)

def find_closest_index(array, value):
    return (np.abs(array - value)).argmin()

def simple_pulsed_excitation(simulator, period, duty_cycle, n_pulses, stabilization_time, N0, N1, N2):
    times = np.linspace(0, period * n_pulses + stabilization_time, 10000)
    t_on, t_off = period*duty_cycle, period*(1-duty_cycle)
    result = pd.DataFrame()
    t_initial_idx = 0
    for i in range(2*n_pulses):
        t_sim = t_on if i%2 == 0 else t_off
        t_final_idx = find_closest_index(times, times[t_initial_idx] + t_sim)
        laser = ((i+1)%2)
        partial_result = simulator.solve(
            save_at=times[t_initial_idx:t_final_idx],
            values={
                Example.laser:laser,
                Example.N0:N0,
                Example.N1:N1,
                Example.N2:N2
            }
        )
        N0 = partial_result["N0"].iloc[-1]
        N1 = partial_result["N1"].iloc[-1]
        N2 = partial_result["N2"].iloc[-1]
        partial_result["laser"] = np.repeat(laser, t_final_idx - t_initial_idx)
        result = pd.concat([result, partial_result])
        t_initial_idx = t_final_idx + 1

    partial_result = simulator.solve(
        save_at=times[t_initial_idx:],
        values={
            Example.laser:0,
            Example.N0:N0,
            Example.N1:N1,
            Example.N2:N2
        }
    )
    partial_result["laser"] = 0
    return pd.concat([result, partial_result])

print(Example.fluorescence_spectra("nm"))
kwargs = {
    "simulator":Simulator(Example),
    "period":100,
    "duty_cycle":0.995,
    "n_pulses":1,
    "N0":1000,
    "N1":0,
    "N2":0,
    "stabilization_time":0,
}
result = simple_pulsed_excitation(**kwargs)
result["E"] = result["N0"] + result["N1"] + 2*result["N2"]
result["laser"] = result["laser"] * max(result["N1"].max(), result["N2"].max())
#result.loc[:, result.columns.difference(["E", "N0"])].plot()
result.plot()
plt.show()
a = poincare.compile.build_first_order_symbolic_ode(Example)

total = 0
for key, val in a.func.items():
    total = total + val
    print(f"d{key}/dt = {val}")
