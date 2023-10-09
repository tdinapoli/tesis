import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt

def count_photons(sig):
    xs, hs = sp.signal.find_peaks(sig, height=(-20, 4.5))
    return len(xs)

spectrum = []
directory = "/home/tdinapoli/Documents/personales/facultad/tesis/git/data/europio/med1/data.pickle"
df = pd.read_pickle(directory)
wls = df.columns

for wl in wls:
    sig = df[wl].values[0]

    x = np.arange(0, len(sig))
    #plt.plot(x, sig)
    #plt.show()
    spectrum.append(count_photons(sig))


#for wl in wls:
#    a = df[wl].values[1]
#    plt.plot(np.arange(0, len(a)), a)
#    plt.show()
#    spectrum.append(count_photons(a))
#
plt.plot(wls, spectrum)

plt.show()