from ucnpexp.instruments import Spectrometer
from ipywidgets import interact_manual, HBox, FloatSlider, FloatRangeSlider, interact, BoundedFloatText, interactive
from IPython.display import HTML, display, clear_output
import numpy as np
import matplotlib.pyplot as plt

class MonochromatorDummy:
    def __init__(self, name):
        self.name = name

    def home(self):
        print(f"homing {self.name}")

class SpectrometerDummy:
    def __init__(self):
        self.monochromator = MonochromatorDummy("monochromator")
        self.lamp = MonochromatorDummy("lamp")
        self.min_wl = 250
        self.max_wl = 750

    def get_emission(self, integration_time, excitation_wavelength,
        starting_wavelength, ending_wavelength, wavelength_step):
        print(f"Getting emission spectrum from {starting_wavelength} to {ending_wavelength} with {wavelength_step} steps and {integration_time} integration time, exciting at {excitation_wavelength}.")
        for wl in np.arange(starting_wavelength, ending_wavelength, wavelength_step):
            print(f"Measuring at {wl} for {integration_time} seconds, exciting at {excitation_wavelength}.")
            yield np.random.randint(0, 10)

    def get_excitation(self, integration_time, emission_wavelength,
        starting_wavelength, ending_wavelength, wavelength_step):
        print(f"Getting excitation spectrum from {starting_wavelength} to {ending_wavelength} with {wavelength_step} steps and {integration_time} integration time, emitting at {emission_wavelength}.")
        for wl in np.arange(starting_wavelength, ending_wavelength, wavelength_step):
            print(f"Measuring at {wl} for {integration_time} seconds, emitting at {emission_wavelength}.")
            yield np.random.randint(0, 10)
    
def spectrometerGUI():
    spec = Spectrometer.constructor_default()
    spec.home()

    def home_emission():
        spec.monochromator.home()
    
    def home_excitation():
        spec.lamp.home()

    def get_excitation(integration_time, emission_wavelength,
        wavelength_range, wavelength_step):
        starting_wavelength, ending_wavelength = wavelength_range
        return spec.get_excitation(integration_time,
        emission_wavelength=emission_wavelength,
        starting_wavelength=starting_wavelength,
        ending_wavelength=ending_wavelength,
        wavelength_step=wavelength_step)

    def get_emission(integration_time, excitation_wavelength,
        wavelength_range, wavelength_step):
        starting_wavelength, ending_wavelength = wavelength_range
        return spec.get_emission(integration_time,
        emission_wavelength=excitation_wavelength,
        starting_wavelength=starting_wavelength,
        ending_wavelength=ending_wavelength,
        wavelength_step=wavelength_step)

    def generate_spectrum_widgets(monochromator, counterpart):
            integration_time = BoundedFloatText(value=0.1, min=0.01,
                max=10.0, step=0.01, description="Integration time:",
                disabled=False)
            counterpart_wavelength = BoundedFloatText(
                value=counterpart.min_wl,
                min=counterpart.min_wl,
                max=counterpart.max_wl,
                step=counterpart.wl_step_ratio,
                description="Emission/Excitation wavelenth:",
                disabled=False)
            wavelength_range = FloatRangeSlider(
                value=(monochromator.min_wl, monochromator.max_wl),
                min=monochromator.min_wl,
                max=monochromator.max_wl,
                step=monochromator.wl_step_ratio,
                description="Swipe range:",
                disabled=False,
                continuous_update=False,
                orientation="horizontal",
                readout_format='.2f',
                readout=True)
            wavelength_step = BoundedFloatText(
                value=1.0,
                min=monochromator.wl_step_ratio,
                max=10.0,
                step=monochromator.wl_step_ratio,
                description="Wavelength step:",
                disabled=False)
            return integration_time, counterpart_wavelength, wavelength_range, wavelength_step

    def get_spectrum(type):
        if type == "Excitation":
            integration_time, emission_wavelength, wavelength_range, wavelength_step = generate_spectrum_widgets(
                monochromator=spec.lamp,
                counterpart=spec.monochromator
            )
            excitation_interact = interact_manual(get_excitation,
            integration_time=integration_time, 
            emission_wavelength=emission_wavelength,
            wavelength_range=wavelength_range,
            wavelength_step=wavelength_step)
            excitation_interact.widget.children[0].description = "Get Spectrum"
            display(excitation_interact)
        elif type == "Emission":
            integration_time, excitation_wavelength, wavelength_range, wavelength_step = generate_spectrum_widgets(
                monochromator=spec.lamp,
                counterpart=spec.monochromator
            )
            emission_interact = interact_manual(get_emission,
            integration_time=integration_time, 
            excitation_wavelength=excitation_wavelength,
            wavelength_range=wavelength_range,
            wavelength_step=wavelength_step)
            emission_interact.widget.children[-1].description = "Get Spectrum"
            df = display(emission_interact)
            return df

    def plot(df):
        if df:
            plt.plot(df["wavelength"], df["counts"]/df["integration time"], '-o')
            plt.grid()
            plt.title("Spectrum")
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Counts/second (1/s)")
            plt.show()
        else:
            print("No data acquired")

    hem_int = interact_manual(home_emission)
    hem_int.widget.children[0].description = 'Home Emission'
    hex_int = interact_manual(home_excitation)
    hex_int.widget.children[0].description = "Home Lamp"


    type = ["Excitation", "Emission"]
    get_spectrum_interact = interact(get_spectrum, type=type)
    df = None
    df = display(get_spectrum_interact)
    display(hem_int, hex_int)
    plot_interact = interact_manual(plot, df=df, description="Plot data")
    display(plot_interact)

class SpectrometerGUI:
    def __init__(self):
        from ucnpexp.instruments import Spectrometer
        self.df = None
        self.spec = Spectrometer.constructor_default()

    def plot_data(self):
        if self.df is not None:
            plt.plot(self.df["wavelength"], self.df["counts"] / self.df["integration time"], '-o')
            plt.grid()
            plt.title("Spectrum")
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Counts/second (1/s)")
            plt.show()
        else:
            print("No data acquired")

    def create_gui(self):

        def get_excitation(wavelength_range, integration_time, counterpart_wavelength,
                wavelength_step):
            starting_wavelength, ending_wavelength = wavelength_range
            self.df = self.spec.get_emission(integration_time,
                emission_wavelength=counterpart_wavelength,
                starting_wavelength=starting_wavelength,
                ending_wavelength=ending_wavelength,
                wavelength_step=wavelength_step)
            return self.df

        def get_emission(wavelength_range, integration_time, counterpart_wavelength,
                         wavelength_step):
            starting_wavelength, ending_wavelength = wavelength_range
            self.df = self.spec.get_emission(integration_time,
                excitation_wavelength=counterpart_wavelength,
                starting_wavelength=starting_wavelength,
                ending_wavelength=ending_wavelength,
                wavelength_step=wavelength_step)
            return self.df

        def create_spectrum_widgets(type):
            if type == "Emission":
                swiping_monochromator = self.spec.monochromator
                stationary_monochromator = self.spec.lamp
                spectrum_function = get_emission
            elif type == "Excitation":
                swiping_monochromator = self.spec.lamp
                stationary_monochromator = self.spec.monochromator
                spectrum_function = get_excitation   
            else:
                print("ERROR: wrong spectrum type")

            integration_time = BoundedFloatText(
                value=0.1, min=0.01,
                max=10.0,
                step=0.01,
                description="Integration time:",
                disabled=False)

            stationary_monochromator_wavelength = BoundedFloatText(
                value=stationary_monochromator.min_wl,
                min=stationary_monochromator.min_wl,
                max=stationary_monochromator.max_wl,
                description="Emission/Excitation wavelength:",
                disabled=False)

            wavelength_range = FloatRangeSlider(
                value=(swiping_monochromator.min_wl, swiping_monochromator.max_wl),
                min=swiping_monochromator.min_wl,
                max=swiping_monochromator.max_wl,
                step=swiping_monochromator.wl_step_ratio,
                description="Swipe range:",
                disabled=False)

            wavelength_step = BoundedFloatText(
                value=1.0,
                min=swiping_monochromator.wl_step_ratio,
                max=10.0,
                step=swiping_monochromator.wl_step_ratio,
                description="Wavelength step:",
                disabled=False)

            w = interact_manual(spectrum_function,
                integration_time=integration_time, 
                counterpart_wavelength=stationary_monochromator_wavelength,
                wavelength_range=wavelength_range,
                wavelength_step=wavelength_step,
                disabled=False)

            w.widget.children[4].description = "Get Spectrum"
            display(w)

        type = ["Emission", "Excitation"]
        interact(create_spectrum_widgets, type=type)

if __name__ == "__main__":
    app = SpectrometerGUI()
    app.create_gui()
 