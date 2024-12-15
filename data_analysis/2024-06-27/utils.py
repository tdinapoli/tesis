import numpy as np


# peak_counting function that was used (with defaults)
def find_arrival_times(data, threshold=0.5):
    # TODO: calibrate this
    return data.iloc[np.where(np.diff(data.ch1) > threshold)[0]]

def cfd(data, f=0.2):
    tr = 3e-8
    td = tr * (1 - f)
    dt = data.loc["time", 1] - data.loc["time", 0]
    sig = - data.ch1 * f + data.loc["ch1", data.index - td // dt]
    return np.where(sig == 0)