import cv2
import time
from ucnpexp.instruments import Spectrometer
import rpyc
import numpy as np
import pandas as pd



#result, image = cam.read()

#if result:
#    cv2.imwrite("/home/dina/imagen_prueba.png", image)



def generate_random_wl(min_wl, max_wl, n):
    return np.random.randint(min_wl + 1, max_wl - 1, size=n)

def take_picture(wl, t, path):
    cam_port = 2
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        cv2.imwrite(f"{path}/{wl}_{t}.png", image)

def repeat_measurements(wls, n, spec, path):
    n_mediciones = len(wls) * n
    medicion = 1
    with open(f"{path}/test.txt", "w") as f:
        for _ in range(n):
            for wl in wls:
                print(f"{medicion=}\n{wl=}\n\n")
                time.sleep(3)
                spec.goto_wavelength(wl)
                t = time.strftime("%H:%M:%S")
                take_picture(wl, t, path)
                print(f"{wl} {t}", file=f)

conn = rpyc.connect("rp-f05512.local", port=18861)
spec = Spectrometer.constructor_default(conn)
calibration_path = "/home/dina/Documents/facultad/tesis/calibration_22_sep.yaml"
spec.load_calibration(calibration_path)
spec.set_wavelength(601)
wls = pd.read_pickle("/home/dina/Documents/facultad/tesis/git/instrumentation/calibracion/calibration_data/swipe_wavelengths/exp_1/wavelengths.pickle")
#print(wls)
path = "/home/dina/Documents/facultad/tesis/git/instrumentation/calibracion/calibration_data/swipe_wavelengths/exp_1"
for i, wl in enumerate(wls[0]):
    t = time.strftime("%H:%M:%S")
    print(f"{wl}_{t}_{i}.png")
    spec.goto_wavelength(wl)
    take_picture(wl, t+f"_{i}", path)
#time.sleep(5)
#repeat_measurements(wls, 5, spec, path)
#
