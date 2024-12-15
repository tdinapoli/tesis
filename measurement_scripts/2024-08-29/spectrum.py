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


def init_laser(itc_config_path):
    itc = ITC4020(itc_config_path, verbose=True)
    itc.qcw_mode = False
    return itc

def turn_on_laser(itc: ITC4020):
    itc.tec_output = True
    while itc.temp_tripped:
        print("Waiting for laser to cool")
        time.sleep(1)
    time.sleep(1)
    itc.ld_output = True
    time.sleep(3)


def meas_spectrum(
    spec: Spectrometer,
    itc: ITC4020,
    starting_wl: float,
    ending_wl: float,
    wl_step: float,
    integration_time: float,
    current: float,
    feed_wl: callable = None,
):
    turn_on_laser(itc)
    itc.laser_current = current
    time.sleep(1)
    print(f"{spec.emission_mono.wavelength=}")
    print(f"{spec.emission_mono.limit_switch.state=}")
    print(f"{starting_wl=}, {ending_wl=}, {wl_step=}, {integration_time=}")
    df = spec.get_emission(
        integration_time=integration_time,
        excitation_wavelength=None,  # esto va none porque si no tira error
        feed=print,
        starting_wavelength=starting_wl,
        ending_wavelength=ending_wl,
        wavelength_step=wl_step,
        feed_wl=feed_wl,
    )
    optical_power = itc.optical_power
    params = {
        "starting_wl": starting_wl,
        "ending_wl": ending_wl,
        "wl_step": wl_step,
        "integration_time": int(integration_time/0.00026) * 0.00026,
        "current": current,
        "optical_power": optical_power,
    }
    df = add_attrs(df, params)
    return df


def feed_wl_gen(basedir: Path):
    def _feed_wl(wl):
        os.makedirs(basedir / f"{wl}")
        def _feed_data(data: pd.DataFrame, rep):
            p = basedir / f"{wl}" / f"{str(rep).zfill(4)}.pickle"
            data.to_pickle(p)
        return _feed_data
    return _feed_wl


def main():
    # Load measurement parameters
    #path = "/home/tomi/Documents/academicos/facultad/tesis/tesis/measurement_scripts/2024-08-29/spectrum_config_test.yaml"
    path = Path("/root/scripts/2024-09-02/spectrum_config.yaml")

    if path is None:
        raise ValueError("Add path")

    with open(path, "r") as f:
        config = yaml.full_load(f)

    currs = config["currents"][::-1]
    int_times = config["integration_times"][::-1]
    starting_wl = config["starting_wl"]
    ending_wl = config["ending_wl"]
    wl_step = config["wl_step"]
    #base_path = Path("/root/.local/refurbishedPTI/measurements/2024-09-02")
    base_path = Path("/mnt/data/2024-09-03")

    # Init instruments
    print("Initializing instruments")
    print("Initializing RP")
    init()
    print("Initializing SPEC")
    spec = init_spec()
    print("Initializing ITC")
    itc_config_path = "/root/.local/refurbishedPTI/configs/itc_config.yaml"
    itc = init_laser(itc_config_path)


    measure_spectrum = partial(
        meas_spectrum,
        spec=spec,
        itc=itc,
        starting_wl=starting_wl,
        ending_wl=ending_wl,
        wl_step=wl_step,
    )

    print(currs, int_times)
    for current, integration_time in zip(currs, int_times):
        print(f"Measuring spectrum with {current=}, {integration_time=}")
        home_mono(spec)
        data_path = base_path / f"{current:.4f}_{integration_time:.4f}"
        feed_wl = feed_wl_gen(data_path)
        df = measure_spectrum(
            integration_time=integration_time, current=current, feed_wl=feed_wl
        )
        df.to_pickle(f"{data_path}/{starting_wl}_{ending_wl}_{wl_step}_{integration_time}_{current:.3f}.pickle")
        itc.ld_output = False


if __name__ == "__main__":
    main()
