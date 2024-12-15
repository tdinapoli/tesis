from functools import partial
import time
import os

import yaml
from redpipy.rpwrap import init
from refurbishedPTI.instruments import ITC4020, Spectrometer
import numpy as np
from pathlib import Path
import pandas as pd

def add_attrs(df, dict):
    for key, val in dict.items():
        df.attrs[key] = val
    return df

def home_mono(spec: Spectrometer):
    print("Homing emission monochromator...")
    spec.emission_mono.set_wavelength(256.5)
    spec.emission_mono.goto_wavelength(265)
    spec.emission_mono.home(ignore_limit=True)

def init_spec():
    print("Initializing spectrometer")
    spec = Spectrometer.constructor_default()
    spec.excitation_mono.set_wavelength(300)
    return spec

def turn_on_laser(itc: ITC4020):
    itc.tec_output = True
    while itc.temp_tripped:
        print("Waiting for laser to cool")
        time.sleep(1)
    time.sleep(1)
    itc.ld_output = True
    time.sleep(3)
    time.sleep(1)

def init_laser(itc_config_path):
    itc = ITC4020(itc_config_path, verbose=True)
    itc.qcw_mode = False
    return itc

def configure_laser(itc, curr):
    itc.qcw_mode = True
    itc.frequency = 100
    itc.laser_current = curr
    itc.duty_cycle = 80
    print(f"{itc.qcw_mode=}")
    print(f"{itc.frequency=}")
    print(f"{itc.laser_current=}")
    print(f"{itc.duty_cycle=}")

def acquire_lifetime(spec, itc, wl, curr, amount_buffers, max_delay):
    spec.emission_mono.goto_wavelength(wl)
    configure_laser(itc, curr)
    turn_on_laser(itc)
    spec.set_decay_configuration()
    return spec.acquire_decay(amount_buffers=amount_buffers, max_delay=max_delay)

def main():
    # Load measurement parameters
    #path = "/home/tomi/Documents/academicos/facultad/tesis/tesis/measurement_scripts/2024-08-29/spectrum_config_test.yaml"
    path = Path("/root/scripts/2024-09-03/lifetimes_config.yaml")

    if path is None:
        raise ValueError("Add path")

    with open(path, "r") as f:
        config = yaml.full_load(f)

    wls = config["wavelengths"]
    currs = config["currents"]
    max_delay = config["max_delay"]
    amount_buffers = config["amount_buffers"]
    base_path = Path("/mnt/data/2024-09-11")
    data_path = base_path/"lifetimes"

    # Init instruments
    print("Initializing instruments")
    print("Initializing RP")
    init()
    print("Initializing SPEC")
    spec = init_spec()
    print("Initializing ITC")
    itc_config_path = "/root/.local/refurbishedPTI/configs/itc_config.yaml"
    itc = init_laser(itc_config_path)


    measure_lifetime = partial(
        acquire_lifetime,
        spec=spec,
        itc=itc,
        max_delay=max_delay,
    )

    for wl in wls:
        print(f"Acquiring at wavelength {wl} nm")
        home_mono(spec)
        for curr, buffers in zip(currs, amount_buffers):
            print(f"With {curr=}")
            df = measure_lifetime(wl=wl, curr=curr, amount_buffers=buffers)
            itc.ld_output = False
            df.to_pickle(data_path/f"{wl}_{curr:.4f}_{buffers}.pickle")


if __name__ == "__main__":
    main()
