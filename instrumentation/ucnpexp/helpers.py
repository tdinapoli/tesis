import numpy as np

class DetectorSignal:
    def __init__(self, sample_rate, measurement_time, offset=0) -> None:
        self.datapoints = int(sample_rate * measurement_time)
        self.signal = np.zeros(self.datapoints) + offset
        self.offset = offset
        self.sample_rate = sample_rate
        self.measurement_time = measurement_time

        pass

    def emit(self, n_photons):
        pass
        
    def emit_photon(self, times, decay_rate):
        times = np.asarray(times)
        point = int(time*self.sample_rate)
        length_until_end = len(self.signal[point:])
        for time in times:
            t = self.signal[point:length_until_end]
            t = t + np.exp(-decay_rate * t)

if __name__ == "__main__":
    sig = DetectorSignal(125e6, 1e-6)
    print(sig.signal)





