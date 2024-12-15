import numpy as np
import pandas as pd
import pathlib
from functools import lru_cache
from .types import ConuntStrat
import matplotlib.pyplot as plt


def get_wls(path: pathlib.Path, rng: tuple | int = None):
    wls_paths = sorted([wl for wl in path.iterdir() if wl.is_dir()])
    wls = [int(wl.name) for wl in wls_paths]

    if isinstance(rng, tuple):
        min_idx = wls.index(rng[0])
        max_idx = wls.index(rng[1])
        wls_paths = wls_paths[min_idx:max_idx]
        wls = wls[min_idx:max_idx]
    elif isinstance(rng, int):
        idx = wls.index(rng)
        wls_paths = wls_paths[idx:idx+1]
        wls = wls[idx:idx+1]
    return wls, wls_paths


@lru_cache(maxsize=None)
def calc_spectrum(path: pathlib.Path, strategy: callable, rng: tuple = None, verbose: bool = False, counts_path: pathlib.Path = None):
    wls, wls_paths = get_wls(path, rng=rng)

    spectrum = np.zeros(len(wls))
    for i, wl_path in enumerate(wls_paths):
        if verbose:
            print(wl_path.name)
        counts = 0
        for screen in wl_path.iterdir():
            try:
                df = pd.read_pickle(screen)
                counts += len(strategy(df).time)
            except Exception as e:
                print(f"An exception ocurred: {e}")
        if counts_path is not None:
            print(wls[i], counts, file=counts_path)
        spectrum[i] = counts
    return wls, spectrum


#@lru_cache(maxsize=None)
def calc_distances(path: pathlib.Path, strategy: ConuntStrat, rng: tuple = None):
    wls, wls_paths = get_wls(path, rng=rng)
    differences = np.array([])
    for wl_path in wls_paths:
        for screen in wl_path.iterdir():
            df = pd.read_pickle(screen)
            diffs = np.diff(strategy(df).time)
            differences = np.hstack([differences, diffs])
    return differences

def plot_spectrums(normalization: callable = None):
    path = pathlib.Path('/home/tomi/Documents/academicos/facultad/tesis/tesis/measurement_scripts/2024-08-29/data/spectrums')
    for p in path.iterdir():
        curr = p.name.split("_")[0]
        df = pd.read_pickle(p)
        if normalization is not None:
            df = normalization(df)
        plt.plot(df.wavelength, df.counts, '-.', label=curr)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Counts per sec (1/s)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_spectrums()