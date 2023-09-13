from poincare import Variable, System, Parameter, assign, Simulator
from poincare.types import Initial
from poincare._utils import class_and_instance_method
from typing_extensions import dataclass_transform

import pint
import matplotlib.pyplot as plt
import numpy as np


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
    up = excited.derive() << - val

    @property
    def energy_difference(self) -> pint.Quantity:
        return self.excited.energy - self.ground.energy

class StateAbsorption(System):
    ground: State = initial(0., default=0)
    excited: State = initial(0., default=0)

    rate: Parameter = assign(default=0)

    equation = FluorescenceTransition(ground=excited, excited=ground, rate=rate)

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

    N0: State = initial(0, default=0)
    N1: State = initial(532 * ureg.nm, default=1_000)

    fluo = FluorescenceTransition(ground=N0, excited=N1, rate=1)
    fluo2 = StateAbsorption(ground=N0, excited=N1, rate=1)

print(Example.fluorescence_spectra("nm"))
sim = Simulator(Example)
result = sim.solve(save_at=np.linspace(0, 50, 1000))
result.plot()
plt.show()

