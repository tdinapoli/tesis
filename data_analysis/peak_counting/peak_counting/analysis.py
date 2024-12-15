from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from peak_counting import utils
from peak_counting.constants import PEAKS_PATH

from .types import ConuntStrat


def plot_peaks(strat: ConuntStrat):
    sig = pd.read_pickle(PEAKS_PATH)
    plt.plot(sig.time, sig.ch1)
    peaks = strat(sig)
    plt.plot(peaks.time, peaks.ch1)
    plt.show()


def plot_spectrum(path: Path, strat: ConuntStrat, rng: tuple = None):
    wls, spectrum = utils.calc_spectrum(path, strat, rng=rng)
    plt.plot(wls, spectrum)


def plot_histogram(path: Path, strat: ConuntStrat, rng: tuple = None):
    differences = utils.calc_distances(path, strat, rng=rng)
    freq, bin_edges = np.histogram(differences)
