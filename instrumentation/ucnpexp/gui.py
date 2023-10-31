from ucnpexp.instruments import Spectrometer
import ipywidgets as widgets
from IPython.display import HTML, display, clear_output
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from dataclasses import dataclass, asdict
import json
import datetime
import pandas as pd
import ipyfilechooser
    

output = widgets.Output()
@dataclass(frozen=True)
class Measurement:
    starting_wavelength: float
    ending_wavelength: float
    wavelength_step: float
    integration_time: float
    stationary_monochromator_wavelength: float
    spectrum_type: str
    date: str
    time: str
    name: str
    data: pd.DataFrame

    def to_csv(self, path):
        self.data.to_csv(f"{path}.csv")
        self.save_metadata(path)
    
    def to_excel(self, path):
        self.data.to_excel(f"{path}.xlsx")
        self.save_metadata(path)
    
    def to_pickle(self, path):
        self.data.to_pickle(f"{path}.pickle")
        self.save_metadata(path)

    def to_dict(self):
        self_dict = asdict(self)
        return self_dict
    
    def save_metadata(self, path):
        with open(f"{path}.json", 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)
    
    @property
    def metadata(self):
        self_dict = self.to_dict()
        del self_dict["data"]
        return self_dict

    def plot_line(self, ax, **kwargs):
        line, = ax.plot(self.data["wavelength"], self.data["counts"]/self.data["integration time"], '-o', **kwargs)
        return line

class SpectrometerGUI:
    def __init__(self):
        from ucnpexp.instruments import Spectrometer
        self.df = None
        self.spec = Spectrometer.constructor_default()
        #self.spec.lamp.set_wavelength(self.spec.lamp.min_wl)
        #self.spec.monochromator.set_wavelength(self.spec.monochromator.min_wl)
        self.spec.lamp.set_wavelength(289.5)
        self.spec.monochromator.set_wavelength(747)
        self.measurements = {}
        self.out = widgets.Output()
        self.style = {'description_width':'initial'}
        self.lines_on_graph = {}

    def plot_measurement(self):
        measurement_name = self.measurement_dropdown
        if measurement_name is not None:
            measurement = self.measurements[measurement_name]
            if measurement_name not in self.lines_on_graph.keys():
                line = measurement.plot_line(self.ax)
                self.lines_on_graph[measurement_name] = line
            else:
                self.lines_on_graph[measurement_name].remove()
                del self.lines_on_graph[measurement_name]
        self.update_plot()(measurement_name)

    def initialize_plot(self):
        self.figure, self.ax = plt.subplots(figsize=(15,5))
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Counts/second (1/s)")
        self.ax.set_title("Spectrum")
        self.ax.grid()

    def get_excitation(self):
        starting_wavelength, ending_wavelength = self.wavelength_range
        self.df = self.spec.get_excitation(self.integration_time,
            emission_wavelength=self.stationary_monochromator_wavelength,
            starting_wavelength=starting_wavelength,
            ending_wavelength=ending_wavelength,
            wavelength_step=self.wavelength_step)
        return self.df

    def get_emission(self):
        starting_wavelength, ending_wavelength = self.wavelength_range
        self.df = self.spec.get_emission(self.integration_time,
            excitation_wavelength=self.stationary_monochromator_wavelength,
            starting_wavelength=starting_wavelength,
            ending_wavelength=ending_wavelength,
            wavelength_step=self.wavelength_step)

        return self.df

    def disable_widgets(self, disabled, do_not_disable=[]):
        for w in self.gui_widgets:
            w.disabled = disabled

    def display_spectrum_widgets(self):
        def _display_spectrum_widgets(type):
            if type == "Emission":
                swiping_monochromator = self.spec.monochromator
                stationary_monochromator = self.spec.lamp
                stationary_monochromator_text = 'Excitation wavelength (nm):\t\t'
            elif type == "Excitation":
                swiping_monochromator = self.spec.lamp
                stationary_monochromator = self.spec.monochromator
                stationary_monochromator_text = 'Emission wavelength (nm):\t\t'
            else:
                print("ERROR: wrong spectrum type")

            layout = widgets.Layout(width='auto')
            kwargs = {'style':self.style, 'layout':layout}

            self.integration_time_widget = widgets.BoundedFloatText(
                value=0.01, min=0.01,
                max=10.0,
                step=0.01,
                description="Integration time (s):\t\t",
                disabled=False,
                **kwargs)

            self.stationary_monochromator_wavelength_widget = widgets.BoundedFloatText(
                value=stationary_monochromator.min_wl,
                min=stationary_monochromator.min_wl,
                max=stationary_monochromator.max_wl,
                description=stationary_monochromator_text,
                disabled=False,
                **kwargs)

            self.wavelength_range_widget = widgets.FloatRangeSlider(
                value=(swiping_monochromator.min_wl, swiping_monochromator.min_wl + 10),
                min=swiping_monochromator.min_wl,
                max=swiping_monochromator.max_wl,
                step=swiping_monochromator.wl_step_ratio,
                description="Swipe range (nm):\t\t",
                disabled=False,
                **kwargs)

            self.wavelength_step_widget = widgets.BoundedFloatText(
                value=1.0,
                min=abs(swiping_monochromator.wl_step_ratio),
                max=10.0,
                step=abs(swiping_monochromator.wl_step_ratio),
                description="Wavelength step (nm):\t\t",
                disabled=False,
                **kwargs)

            display(self.wavelength_step_widget, self.wavelength_range_widget,
             self.stationary_monochromator_wavelength_widget, self.integration_time_widget)
        return _display_spectrum_widgets

    def update_plot(self):
        def _update_plot(measurement_name):
            if measurement_name is not None:
                if self.ax.get_legend():
                    self.ax.get_legend().remove()
                measurement = self.measurements[measurement_name]
                self.ax.set_title(f"{measurement.spectrum_type} Spectrum, $\lambda=${measurement.stationary_monochromator_wavelength}, Integration time:{measurement.integration_time}")
                min_wl = measurement.data["wavelength"].min()
                max_wl = measurement.data["wavelength"].max()
                for name in self.lines_on_graph:
                    self.lines_on_graph[name].set_label(name)
                    min_wl = self.measurements[name].data["wavelength"].min() if self.measurements[name].data["wavelength"].min() < min_wl else min_wl
                    max_wl = self.measurements[name].data["wavelength"].max() if self.measurements[name].data["wavelength"].max() > max_wl else max_wl
                self.ax.set_xlim([min_wl-1, max_wl+1])
                self.ax.legend()

        return _update_plot

    def display_measurement_widgets(self):

        self.measure_button_widget = widgets.Button(description="Measure")
        self.measure_button_widget.on_click(self.measure)

        def select_data(measurement_name):
            if measurement_name is not None:
                df = self.measurements[measurement_name].data

        self.measurement_file_chooser_widget = ipyfilechooser.FileChooser()
        self.measurement_file_chooser_widget.default_path = "/home/tomi/HORIBA/measurements"
        self.measurement_file_chooser_widget.title = "Measurement name:"

        self.measurement_dropdown_widget = widgets.Dropdown(options=[name for name in self.measurements],
                                                            style=self.style)
        self.measurement_dropdown_interact = widgets.interact(self.update_plot(), measurement_name=self.measurement_dropdown_widget,
                          style=self.style)
        self.measurement_dropdown_interact.widget.children[0].description = "Measurements:"
        

        self.file_format_widget = widgets.Dropdown(options=["Excel", "csv", "pickle"],
                                                     description="File format:",
                                                     style=self.style)

        self.save_measurement_widget = widgets.Button(description="Save measurement")
        self.save_measurement_widget.on_click(self.save_measurement)

        display(self.measurement_file_chooser_widget, self.measure_button_widget,
             self.measurement_dropdown_interact, self.file_format_widget,
            self.save_measurement_widget)

    def save_measurement(self, widget_placeholder):
        if self.measurement_file_format == "Excel":
            self.measurements[self.measurement_dropdown].to_excel(f"{self.measurement_file_chooser_widget.selected}")
        elif self.measurement_file_format == "csv":
            self.measurements[self.measurement_dropdown].to_csv(f"{self.measurement_file_chooser_widget.selected}")
        elif self.measurement_file_format == "pickle":
            self.measurements[self.measurement_dropdown].to_pickle(f"{self.measurement_file_chooser_widget.selected}")
        else:
            print("Wrong file format")

    def measure(self, widget_placeholder):
        self.disable_widgets(True, do_not_disable=["spectrum_type_widget"])
        self.df = self.get_spectrum(self.spectrum_type)
        if self.measurement_file_chooser_widget.selected_filename is not None:
            name = self.measurement_file_chooser_widget.selected_filename
        else:
            name = str(datetime.datetime.now())
        measurement_data = {
            'starting_wavelength': self.starting_wavelength,
            'ending_wavelength': self.ending_wavelength,
            'wavelength_step': self.wavelength_step,
            'integration_time': self.integration_time,
            'stationary_monochromator_wavelength': self.stationary_monochromator_wavelength,
            'spectrum_type': self.spectrum_type,
            'date': str(datetime.date.today()),
            'time': str(datetime.datetime.now().time()),
            'name': name,
            'data': self.df,
        }
        measurement = Measurement(**measurement_data)
        self.measurements[measurement.name] = measurement
        self.measurement_dropdown_widget.options = [name for name in self.measurements]
        self.measurement_dropdown_widget.value = measurement.name
        self.plot_measurement()
        self.measurement_file_chooser_widget.reset(filename=measurement.name)
        self.disable_widgets(False, do_not_disable=["spectrum_type_widget"])

    def get_spectrum(self, type):
        if type == "Emission":
            df = self.get_emission()
        elif type == "Excitation":
            df = self.get_excitation()
        else:
            print("Error: Wrong spectrum type")
        return df

    @property
    def gui_widgets(self):
        lista = [w for attr, w in vars(self).items() if attr.endswith("widget")] 
        return lista

    @property
    def measurement_file_format(self):
        return self.file_format_widget.value

    @property
    def measurement_dropdown(self):
        return self.measurement_dropdown_widget.value

    @property
    def starting_wavelength(self):
        return self.wavelength_range_widget.value[0]
    
    @property
    def ending_wavelength(self):
        return self.wavelength_range_widget.value[1]

    @property
    def wavelength_step(self):
        return self.wavelength_step_widget.value
    
    @property
    def wavelength_range(self):
        return self.wavelength_range_widget.value
    
    @property
    def stationary_monochromator_wavelength(self):
        return self.stationary_monochromator_wavelength_widget.value

    @property
    def integration_time(self):
        return self.integration_time_widget.value
    
    @property
    def spectrum_type(self):
        return self.spectrum_type_widget.value

    def create_gui(self):

        self.spectrum_type_widget = widgets.Dropdown(options=["Emission", "Excitation"],
             description="Spectrum type:", style=self.style)

        spectrum_widgets = widgets.interact(self.display_spectrum_widgets(), type=self.spectrum_type_widget)

        display(spectrum_widgets)
        self.display_measurement_widgets()
        self.initialize_plot()
        self.plot_button_widget = widgets.interact_manual(self.plot_measurement)
        self.plot_button_widget.widget.children[0].description = "Plot measurement"

if __name__ == "__main__":
    app = SpectrometerGUI()
    app.create_gui()
 