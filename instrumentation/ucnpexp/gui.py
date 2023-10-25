from ucnpexp.instruments import Spectrometer
import ipywidgets as widgets
from IPython.display import HTML, display, clear_output
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import datetime
import pandas as pd

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
    
@dataclass(frozen=True)
class Measurement:
    starting_wavelength: float
    ending_wavelength: float
    wavelength_step: float
    integration_time: float
    counterpart_wavelength: float
    spectrum_type: str
    date: datetime.date
    time: datetime.time
    name: str
    data: pd.DataFrame

class SpectrometerGUI:
    def __init__(self):
        from ucnpexp.instruments import Spectrometer
        self.df = None
        self.spec = Spectrometer.constructor_default()
        self.spec.lamp.set_wavelength(self.spec.lamp.min_wl)
        self.spec.monochromator.set_wavelength(self.spec.monochromator.min_wl)
        self.measurements = []

    def plot_data(self):
        if self.df is not None:
            self.ax.plot(self.df["wavelength"], self.df["counts"] / self.df["integration time"], '-o')
        else:
            print("No data acquired")

    def initialize_plot(self):
        self.figure, self.ax = plt.subplots()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Counts/second (1/s)")
        self.ax.set_title("Spectrum")
        self.ax.grid()

    def get_excitation(self):
        starting_wavelength, ending_wavelength = self.wavelength_range.value
        self.df = self.spec.get_excitation(self.integration_time.value,
            emission_wavelength=self.counterpart_wavelength.value,
            starting_wavelength=starting_wavelength,
            ending_wavelength=ending_wavelength,
            wavelength_step=self.wavelength_step.value)

    def get_emission(self):
        starting_wavelength, ending_wavelength = self.wavelength_range.value
        self.df = self.spec.get_emission(self.integration_time.value,
            excitation_wavelength=self.counterpart_wavelength.value,
            starting_wavelength=starting_wavelength,
            ending_wavelength=ending_wavelength,
            wavelength_step=self.wavelength_step.value)

    def create_spectrum_widgets(self):
        def _create_spectrum_widgets(type):
            if type == "Emission":
                swiping_monochromator = self.spec.monochromator
                stationary_monochromator = self.spec.lamp
                stationary_monochromator_text = 'Emission wavelength (nm):\t\t'
            elif type == "Excitation":
                swiping_monochromator = self.spec.lamp
                stationary_monochromator = self.spec.monochromator
                stationary_monochromator_text = 'Excitation wavelength (nm):\t\t'
            else:
                print("ERROR: wrong spectrum type")

            layout = widgets.Layout(width='auto')
            kwargs = {'style':self.style, 'layout':layout}

            self.integration_time = widgets.BoundedFloatText(
                value=0.1, min=0.01,
                max=10.0,
                step=0.01,
                description="Integration time (s):\t\t",
                disabled=False,
                **kwargs)

            self.stationary_monochromator_wavelength = widgets.BoundedFloatText(
                value=stationary_monochromator.min_wl,
                min=stationary_monochromator.min_wl,
                max=stationary_monochromator.max_wl,
                description=stationary_monochromator_text,
                disabled=False,
                **kwargs)

            self.wavelength_range = widgets.FloatRangeSlider(
                value=(swiping_monochromator.min_wl, swiping_monochromator.max_wl),
                min=swiping_monochromator.min_wl,
                max=swiping_monochromator.max_wl,
                step=swiping_monochromator.wl_step_ratio,
                description="Swipe range (nm):\t\t",
                disabled=False,
                **kwargs)

            self.wavelength_step = widgets.BoundedFloatText(
                value=1.0,
                min=abs(swiping_monochromator.wl_step_ratio),
                max=10.0,
                step=abs(swiping_monochromator.wl_step_ratio),
                description="Wavelength step (nm):\t\t",
                disabled=False,
                **kwargs)

            display(self.wavelength_step, self.wavelength_range, self.stationary_monochromator_wavelength, self.integration_time)
        return _create_spectrum_widgets

    def measure():
        pass

    def create_gui(self):

        self.style = {'description_width':'initial'}

        type = widgets.Dropdown(options=["Emission", "Excitation"],
             description="Spectrum type:", style=self.style)

        spectrum_widgets = widgets.interact(self.create_spectrum_widgets(), type=type)

        self.initialize_plot()
        plot_button = widgets.interact_manual(self.plot_data)
        plot_button.widget.children[0].description = "Plot data"

        display(spectrum_widgets)
        display(plot_button)

if __name__ == "__main__":
    app = SpectrometerGUI()
    app.create_gui()
 