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
    data_path = "/root/.local/refurbishedPTI/measurements/2024-06-26"
    spec = Spectrometer.constructor_default()
    spec.excitation_mono.set_wavelength(300)
    itc = ITC4020(itc_config_path, verbose=True)

    configure_itc(itc)

    run = True
    while run:
        print("Running lifetime measurement script\n")

        is_it_ok(home_mono(spec), "Stop homing emission mono?")
        print(f"{spec.emission_mono.wavelength=}")

        wl = is_it_ok(
            select_wl("Select wavelength "), "Is wavelength ok?"
        )
        spec.emission_mono.goto_wavelength(wl)

        amount_buffers = is_it_ok(
            select_int("Select amount of buffers "), "Is it ok?"
        )

        max_delay = is_it_ok(
            select_int("Select max delay "), "is it ok?"
        )

        current = select_current(itc)

        print("Turning on laser")
        turn_on_laser(itc)
        time.sleep(2)
        optical_power = itc.optical_power

        params = {
            "wavelength": wl,
            "amount_buffers": amount_buffers,
            "max_delay" : max_delay,
            "current": current,
            "optical_power": optical_power,
        }

        params_txt = "\n".join([f"{key}={val}" for key, val in params.items()])
        if ask(
            f"current params:\n{params_txt}\nTake lifetime?"
        ):
            print("taking lifetime")
            arrival_times = spec.acquire_decay(
                max_delay=max_delay,
                amount_buffers=amount_buffers,
                step=1, 
                feed=print,
            )
            df = pd.DataFrame(dict(arrival_times=arrival_times))
            df = add_attrs(df, params)
            df.to_pickle(f"{data_path}/{wl}_{amount_buffers}_{max_delay}_{current}_{optical_power}.pickle")
        itc.ld_output = False
        run = ask("Take another lifetime?")

if __name__ == "__main__":
    main()
