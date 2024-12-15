from refurbishedPTI.instruments import Spectrometer, ITC4020
from redpipy.rpwrap import init
import pandas as pd
import time

def ask(text: str) -> bool:
    result = input(f"{text}[Y/n]")
    return result in {"Y", "y", "\n", ""}


def is_it_ok(func, message):
    ok = False
    while not ok:
        val = func()
        ok = ask(message)
    return val

def turn_on_laser(itc: ITC4020):
    itc.tec_output = True
    if not itc.ld_output:
        while itc.temp_tripped:
            print("Waiting for laser to cool")
            time.sleep(1)
        time.sleep(1)
        itc.ld_output = True
        time.sleep(3)

def select_wl(txt: str):
    def _select_wl():
        wl = float(input(txt))
        return wl
    return _select_wl

def home_mono(spec):
    def _home_mono():
        spec.emission_mono.set_wavelength(256.5)
        spec.emission_mono.goto_wavelength(265)
        spec.emission_mono.home()
    return _home_mono

def select_current(itc: ITC4020):
    def _select_current():
        current = float(input("Select current: "))
        if 0 <= current <= 0.4:
            itc.laser_current = current
        else:
            raise ValueError(f"Current {current} A exceeds 0.4 A max possible current.")
        return current

    msg = "Is current value ok?"
    return is_it_ok(_select_current, msg)

def select_int(msg):
    def _select_int():
        integer = int(input(msg))
        return integer
    return _select_int

def add_attrs(df, dict):
    for key, val in dict.items():
        df.attrs[key] = val
    return df

def configure_itc(itc):
    print("\nConfiguring ITC")
    itc.qcw_mode = True
    itc.frequency = 100
    itc.duty_cycle = 80
    print(f"{itc.qcw_mode=}")
    print(f"{itc.frequency=}")
    print(f"{itc.duty_cycle=}")


def main():
    init()

    itc_config_path = "/root/.local/refurbishedPTI/configs/itc_config.yaml"
    data_path = "/root/.local/refurbishedPTI/measurements/2024-06-27/410/2"
    spec = Spectrometer.constructor_default()
    spec.excitation_mono.set_wavelength(300)
    itc = ITC4020(itc_config_path, verbose=True)

    configure_itc(itc)

    #picos = [378, 383, 410, 522, 530, 541, 546, 550, 556, 654, 661] 1st meas
    #currents = [0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05] 1st meas
    #picos = [410, 522, 530, 541, 546, 550, 556, 654, 661]
    #factores = [2, 2, 2, 2, 1, 1, 1, 1, 2, 2]
    #currents = [0.4, 0.35, 0.3, 0.25, 0.2]
    #amount_buffers_per_pot = [60, 65, 70, 90, 100, 120, 150, 200]
    #max_delay = 3
    
    ## CRUDOS
    picos = [410]
    currents = [0.4]
    factores = [2]
    amount_buffers_per_pot = [60]
    max_delay=3

    for pico, factor in zip(picos, factores):
        print(f"Starting lifetime measurement at {pico=}")
        spec.emission_mono.home(ignore_limit=True)
        spec.emission_mono.goto_wavelength(pico)
        for curr, amount_buffers in zip(currents, amount_buffers_per_pot):
            if 0 <= curr <= 0.4:
                print(f"Setting current to {curr}")
                itc.laser_current = curr
            else:
                raise ValueError(f"{curr} is too much current :(")

            print("Turning on laser")
            turn_on_laser(itc)
            time.sleep(2)
            optical_power = itc.optical_power
            if optical_power > 0.34:
                itc.ld_output = False
                raise ValueError(f"Laser optical power {optical_power} too high")

            amount_buffers = amount_buffers * factor
            
            params = {
                "wavelength": pico,
                "amount_buffers": amount_buffers,
                "max_delay" : max_delay,
                "current": curr,
                "optical_power": optical_power,
            }
            params_txt = "\n".join([f"{key}={val}" for key, val in params.items()])
            print(params_txt)
            arrival_times = spec.acquire_decay(
                max_delay=max_delay,
                amount_buffers=amount_buffers,
                step=1, 
                feed=print,
            )
            df = pd.DataFrame(dict(arrival_times=arrival_times))
            df = add_attrs(df, params)
            df.to_pickle(f"{data_path}/{pico}_{amount_buffers}_{max_delay}_{curr}_{optical_power}.pickle")
        itc.ld_output = False

if __name__ == "__main__":
    main()
