import numpy as np
import matplotlib.pyplot as plt

#jtimes = np.load("times.npy")
decimations = np.load("decimations.npy")
arr1 = np.load("arr1.npy")
arr2 = np.arange(0, len(arr1), 1, dtype=int)

#n = 10
#kernel = np.ones(n)/n

#measurements = np.convolve(measurements, kernel)

#times = np.array(list(range(len(measurements))))


plt.plot(arr2, arr1)
plt.show()

