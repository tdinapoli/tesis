from jablonski.types import FluorescentSystem, State, initial
from jablonski.transitions import FluorescenceTransition, StateAbsorption
from jablonski.transitions import EnergyTransferUpconversion as ETU
from poincare import Parameter, assign, Simulator, Independent, Variable
import pint
import numpy as np
import pandas as pd

ureg = pint.get_application_registry()

class Example(FluorescentSystem):
    N0: State = initial(0, default=1_000)
    N1: State = initial(490 * ureg.nm, default=0)
    N2: State = initial(980 * ureg.nm, default=0)
    #t: Independent()

    laser: Parameter = assign(default=0)
    sigma0: Parameter = assign(default=0)
    sigma1: Parameter = assign(default=0)
    k1: Parameter = assign(default=0)
    k2: Parameter = assign(default=0)
    ketu: Parameter = assign(default=0)

    N1N0 = FluorescenceTransition(ground=N0, excited=N1, rate=k1)
    N0N1 = StateAbsorption(ground=N0, excited=N1, rate=laser * sigma0)
    N1etuN2 = ETU(sensitizer=N1, activator=N2, relaxator=N0, rate=ketu)
    N1esaN2 = StateAbsorption(ground=N1, excited=N2, rate=laser * sigma1)
    #N2N1 = FluorescenceTransition(ground=N1, excited=N2, rate=1)
    N2N0 = FluorescenceTransition(ground=N0, excited=N2, rate=k2)

def indexes_where_value_changes(array: np.array):
    indexes = []
    lastval = array[0]
    for i, val in enumerate(array):
        if val != lastval: 
            indexes.append(i)
            lastval = val
    return indexes

def find_closest_index(array, value):
    return (np.abs(array - value)).argmin()

def duty_cycle_signal(times: np.array, period: float, pulses: int,
            duty_cycle: float=0.5, time_before: float=0, before_off: bool=True):
    assert 0 < duty_cycle <= 1

    #if duty_cycle == 1:
    #    return np.ones_like(times)

    signal = np.ones_like(times) 
    t_first_pulse = times[0] + time_before
    last_index = find_closest_index(times, t_first_pulse)

    if before_off:
        signal[:last_index] *= 0

    for pulse in range(pulses):
        starting_index = find_closest_index(times, t_first_pulse + pulse*period + period * duty_cycle)
        ending_index = find_closest_index(times, t_first_pulse + (pulse+1)*(period))
        signal[starting_index:ending_index] *= 0
    signal[ending_index:] *= 0
    return signal

def pulsed_excitation(simulator: Simulator, times: np.array, excitation, values):
    values = values.copy()
    if type(excitation) == float or type(excitation) == int:
        excitation = excitation * np.ones_like(times)
    assert len(times) == len(excitation)
    last_index = 0
    result = pd.DataFrame()
    for index in indexes_where_value_changes(excitation):

        values[getattr(simulator.model, "excitation")] = float(excitation[last_index])
        partial_result = simulator.solve(
            save_at=times[last_index:index],
            values=values
        )
        partial_result["excitation"] = excitation[last_index]
        result = pd.concat([result, partial_result])
        for name in simulator.transform.output:
            variable = getattr(simulator.model, name)
            values[variable] = partial_result[name].iloc[-1]
        last_index = index

    values[getattr(simulator.model, "excitation")] = float(excitation[last_index])
    partial_result = simulator.solve(
        save_at=times[last_index:],
        values=values
    )
    partial_result["excitation"] = excitation[last_index]
    result = pd.concat([result, partial_result])
    return result

def p_vs_i(pots, sim, **kwargs):
    n1, n2 = np.zeros_like(pots), np.zeros_like(pots)
    for i, pot in enumerate(pots):
        kwargs["values"][sim.model.excitation] = pot
        res = sim.solve(save_at=kwargs["save_at"],
                        values=kwargs["values"])
        n1[i] = res["N1"].iloc[-1]
        n2[i] = res["N2"].iloc[-1]
    return n1, n2