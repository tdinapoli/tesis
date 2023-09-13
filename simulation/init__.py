from poincare import Variable, System, Parameter, assign, Simulator
from poincare.types import Initial
from poincare._utils import class_and_instance_method
from typing_extensions import dataclass_transform

import pint
import numpy as np
import matplotlib.pyplot as plt


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

    low_state: State = initial(0., default=0)
    high_state: State = initial(0., default=0)

    rate: Parameter = assign(default=1)

    val = rate * high_state

    down = low_state.derive() << val
    up = high_state.derive() << - val

    @property
    def energy_difference(self) -> pint.Quantity:
        return self.high_state.energy - self.low_state.energy

@dataclass_transform(
    field_specifiers=(initial, )
)
class EnergyTransfer(System):
    donator: State = initial(0., default=0)
    acceptor: State = initial(0., default=0)

    rate: Parameter = assign(default=1)

    val = rate * donator

    donator_to_acceptor = donator.derive() << val
    acceptor_to_donator = donator.derive() << -val


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
    N1: State = initial(980 * ureg.nm, default=0)
    N2: State = initial(490 * ureg.nm, default=0)
    M0: State = initial(0, default=1_000)
    M1: State = initial(980 * ureg.nm, default=0)
    #an12: Parameter = assign(default=1)

    measure_fluo = FluorescenceTransition(low_state=N0, high_state=N2, rate=0)
    m0m1 = FluorescenceTransition(low_state=M0, high_state=M1)
    n0n1 = FluorescenceTransition(low_state=N0, high_state=N1)
    n1n2 = FluorescenceTransition(low_state=N1, high_state=N2, rate=0.1)
    et_m1n1 = EnergyTransfer(donator=M1, acceptor=N1)
    # El rate de et_m1n2 depende de n1 no?
    #et_m1n2 = EnergyTransfer(donator=M1, acceptor=N2, rate=)
    

#print(Example.fluorescence_spectra("eV"))

#print(Example.fluorescence_spectra("1/cm"))
a = Example.fluorescence_spectra("nm")
[print(f"{key} : a[key]") for key in a]
sim = Simulator(Example)
result = sim.solve(times=np.linspace(0, 50, 1000))
result.plot()
plt.show()
#print(Example.fluorescence_spectra("Hz"))
