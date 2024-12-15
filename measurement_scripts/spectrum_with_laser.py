from redpipy.rpwrap import init
from refurbishedPTI.instruments import Spectrometer, ITC4020
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
    while itc.temp_tripped:
        print("Waiting for laser to cool")
        time.sleep(1)
    time.sleep(1)
    itc.ld_output = True
    time.sleep(3)


def select_current(itc: ITC4020):
    def _select_current():
        current = float(input("Select current: "))
        itc.laser_current = current
        return current

    msg = "Is current value ok?"
    return is_it_ok(_select_current, msg)


def select_wl(txt: str):
    def _select_wl():
        wl = float(input(txt))
        return wl

    return _select_wl


def add_attrs(df, dict):
    for key, val in dict.items():
        df.attrs[key] = val
    return df

def home_mono(spec):
    def _home_mono():
        spec.emission_mono.set_wavelength(256.5)
        spec.emission_mono.goto_wavelength(265)
        spec.emission_mono.home()
    return _home_mono

def main():

    init()

    itc_config_path = "/root/.local/refurbishedPTI/configs/itc_config.yaml"
    data_path = "/root/.local/refurbishedPTI/measurements/2024-06-25"
    spec = Spectrometer.constructor_default()
    spec.excitation_mono.set_wavelength(300)
    itc = ITC4020(itc_config_path, verbose=True)
    itc.qcw_mode = False

    run = True
    while run:
        is_it_ok(home_mono(spec), "Stop homing emission mono?")
        print(f"{spec.emission_mono.wavelength=}")

        starting_wl = is_it_ok(
            select_wl("Select starting wavelength "), "Is starting wavelength ok?"
        )
        ending_wl = is_it_ok(
            select_wl("Select ending wavelength "), "Is ending wavelength ok?"
        )
        wl_step = is_it_ok(
            select_wl("Select wavelength step "), "Is wavelength step ok?"
        )
        int_time = is_it_ok(
            select_wl("Select integration time "), "Is integration time ok?"
        )

        print("Turning on laser")
        turn_on_laser(itc)
        current = select_current(itc)
        optical_power = itc.optical_power

        params = {
            "starting_wl": starting_wl,
            "ending_wl": ending_wl,
            "wl_step": wl_step,
            "integration_time": int(int_time/0.00026) * 0.00026,
            "current": current,
            "optical_power": optical_power,
        }

        params_txt = "\n".join([f"{key}={val}" for key, val in params.items()])
        if ask(
            f"current params:\n{params_txt}\nTake spectrum?"
        ):
            df = spec.get_emission(
                integration_time=int_time,
                excitation_wavelength=None, # esto va none porque si no tira error
                feed=print,
                starting_wavelength=starting_wl,
                ending_wavelength=ending_wl,
                wavelength_step=wl_step,
            )
            df = add_attrs(df, params)
            df.to_pickle(f"{data_path}/{starting_wl}_{ending_wl}_{wl_step}_{int_time}_{optical_power:.4f}_{current:.3f}.pickle")
        itc.ld_output = False
        run = ask("Take another spectrum?")

if __name__ == "__main__":
    main()
