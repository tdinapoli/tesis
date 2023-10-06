from . import abstract
import yaml
import rpyc
from . import user_interface as ui
import numpy as np

class OscilloscopeChannel:
    def __init__(self, conn, *, channel= 0, voltage_range=20.0,
                  decimation=1, trigger_post=2**14, trigger_pre=0):
        self._maximum_sampling_rate = 125e6
        self.osc = conn.root.create_osc_channel(channel=channel,
                                                voltage_range=voltage_range,
                                                decimation=decimation,
                                                trigger_post=trigger_post,
                                                trigger_pre=trigger_pre)

    def set_measurement_time(self, seconds, offset=0):
        # Debería agregarle error o algo si seconds < offset
        decimation_exponent = int(np.ceil(np.log2(
            self._maximum_sampling_rate * seconds / self.buffer_size
            )))
        self.decimation = decimation_exponent
        self.trigger_pre = offset * self.sampling_rate
        self.trigger_post = (seconds - offset) * self.sampling_rate
        print(f"Setting decimation exponent to {decimation_exponent}")
        print(f"The sampling rate is {self._maximum_sampling_rate/self.decimation} Hz")
        print(f"Setting trigger_pre to {self.trigger_pre}")
        print(f"Setting trigger_post to {self.trigger_post}")
        print(f"A total of {self.amount_datapoints} data points will be taken")
        print(f"Measurement time will be {self.get_measurement_time()}")

    def get_measurement_time(self):
        return self.amount_datapoints / self.sampling_rate

    # Debería cambiarle el nombre a trigger no?
    def measure(self, transit_seconds=0.01):
        return self.osc.measure(data_points=self.amount_datapoints,
                                transit_seconds=transit_seconds)
    
    @property
    def amount_datapoints(self):
        amount = self.trigger_pre + self.trigger_post 
        if amount > self.buffer_size:
            print("Warning: amount of data points is greater than buffer size")
        return amount
    
    @property
    def buffer_size(self):
        return self.osc.buffer_size()

    @property
    def sampling_rate(self):
        return self._maximum_sampling_rate/self.decimation

    @property
    def trigger_pre(self):
        return self.osc.trigger_pre()

    @trigger_pre.setter
    def trigger_pre(self, amount):
        self.osc.set_trigger_pre(amount)

    @property
    def trigger_post(self):
        return self.osc.trigger_post()

    @trigger_post.setter
    def trigger_post(self, amount):
        self.osc.set_trigger_post(amount)

    @property
    def decimation(self):
        return self.osc.decimation()
    
    @decimation.setter
    def decimation(self, amount):
        self.osc.set_decimation(amount)

    # Esto tira algún tipo de warning que después 
    # Tengo que ver qué significa
    # Pero por ahora parece que funciona
    def __del__(self):
        self.osc.delete()

class RPTTL(abstract.TTL):
    def __init__(self, state, pin, gpio):
        column, number = pin
        self._gpio = gpio(column, number, 'out')
        super().__init__(state)
        
    def _get_state(self):
        return self._gpio.read()
        
    def _set_state(self, state):
        self._gpio.write(state)

class A4988(abstract.MotorDriver):
    ttls: dict
    # Mientras se use la shell para el pololu esto está 
    # fijo en "full step".
    # Sin embargo, Por algún motivo 400 pasos es aprox 360 grados
    _MODES = (
                (False, False, False), #Full step
                (True, False, False) , #Half 
                (False, True, False) , #Quarter
                (True, True, False)  , #Eighth
                (True, True, True)   , #Sixteenth
               )

    def __init__(self, ttls: dict, mode: int = 0):
        for ttl in ttls:
            setattr(self, ttl, ttls[ttl])

    def set_stepping(self, mode: int):
        s1, s2, s3 = self._MODES[mode]
        self.ms1.set_state(s1)
        self.ms2.set_state(s2)
        self.ms3.set_state(s3)

    def get_stepping(self):
        return self._MODES.index((self.ms1.state, self.ms2.state, self.ms3.state))

    #Obs: creo que la minima duracion del pulso es 1 micro segundo
    #Obs2: para q funcione el step debe ir de low a high. Si se 
    # Desconfigura a mano el step (por ejemplo poniendo 
    # driver.step.state = True), esta driver.step() no va a hacer lo
    # esperado (pensar cómo solucionar).
    def step(self, ontime=10e-3, offtime=10e-3, amount=1):
        self.pin_step.pulse(ontime, offtime, amount)
    
class M061CS02(abstract.Motor):
    _STEPS_MODE = (200, 400, 800, 1600, 3200)

    def __init__(self, driver, steps: int = 400, angle: float = 0.0):
        self._driver = driver
        self._angle = angle
        self._angle_relative = angle % 360
        self.steps = steps
        self._min_angle = 360.0/self.steps
        self._min_offtime = 10e-3
        self._min_ontime = 10e-3

    def rotate(self, angle: float):
        relative_angle = angle - self._angle
        angle_rotated = self.rotate_relative(relative_angle)
        return angle_rotated

    def rotate_relative(self, angle: float, change_angle: bool = True):
        cw, angle = angle > 0, abs(angle)
        self._driver.direction.set_state(cw)
        steps = int(angle/self.min_angle)
        self.rotate_step(steps, cw, change_angle=change_angle)
        angle_rotated = (2 * cw - 1) * self.min_angle * steps
        return angle_rotated

    def rotate_step(self, steps: int, cw: bool, change_angle: bool = True):
        self._driver.direction.set_state(cw)
        self._driver.step(ontime = self._min_ontime,
                          offtime= self._min_offtime,
                          amount = steps)
        if change_angle:
            angle_change_sign = (int(cw)*2 - 1)
            self._angle = round(self._angle + angle_change_sign * self.min_angle * steps, 5)

    @property
    def angle(self):
        return self._angle

    @property
    def angle_relative(self):
        return self._angle % 360

    @property
    def min_angle(self):
        return 360 / self.steps

    @property
    def steps(self, steps: int = 200):
        return self._STEPS_MODE[self._driver.get_stepping()]

    @steps.setter
    def steps(self, steps: int = 200):
        self._driver.set_stepping(self._STEPS_MODE.index(steps))

    def set_origin(self, angle: float = 0):
        self._angle = angle

class GPIO_helper:
    def __init__(self, column: str, pin: int, io: str):
        self.column = column
        self.pin = pin
        self.io = io
        self.set_state(True)

    def write(self, state: bool):
        self.set_state(state)

    def read(self):
        return self.state

class Monochromator:
    def __init__(self, motor: abstract.Motor):
        self.CALIB_ATTRS = [ '_wl_step_ratio',
                    '_greater_wl_cw',
                    '_max_wl',
                    '_min_wl',
                    '_wavelength']
        self._motor = motor

    @classmethod
    def constructor_default(cls, conn, pin_step, pin_direction, MOTOR_DRIVER=A4988,
                             MOTOR=M061CS02):
        ttls = {
                'notenable' :   conn.root.create_RPTTL('notenable', (False, 'n', 0)),
                'ms1'       :   conn.root.create_RPTTL('ms1', (False, 'n', 1)),
                'ms2'       :   conn.root.create_RPTTL('ms2', (False, 'n', 2)),
                'ms3'       :   conn.root.create_RPTTL('ms3', (False, 'n', 3)),
                'notreset'  :   conn.root.create_RPTTL('notreset', (True, 'n', 4)),
                'pin_step'  :   conn.root.create_RPTTL('pin_step', (False, 'p', pin_step)),
                'direction' :   conn.root.create_RPTTL('direction', (True, 'p', pin_direction)),
                }
        driver = MOTOR_DRIVER(ttls)
        motor = MOTOR(driver)
        return cls(motor)

    @property
    def wavelength(self):
        try:
            return self._wavelength
        except:
            return None

    @property
    def min_wl(self):
        return self._min_wl

    @property
    def max_wl(self):
        return self._max_wl

    @property
    def greater_wl_cw(self):
        return self._greater_wl_cw

    @property
    def wl_step_ratio(self):
        return self._wl_step_ratio

    def set_wavelength(self, wavelength: float):
        if self.check_safety(wavelength):
            self._wavelength = wavelength
        else:
            print(f"Wavelength must be between {self._min_wl} and {self._max_wl}")

    def check_safety(self, wavelength):
        return self._min_wl <= wavelength <= self._max_wl

    def goto_wavelength(self, wavelength: float):
        if self.check_safety(wavelength):
            steps = abs(int((wavelength - self.wavelength)/self._wl_step_ratio))
            cw = (wavelength - self.wavelength) > 0
            cw = not (cw ^ self.greater_wl_cw)
            self._motor.rotate_step(steps, cw)
            self._wavelength = wavelength
        else:
            print(f"Wavelength must be between {self._min_wl} and {self._max_wl}")
        return self._wavelength


    def load_calibration(self, path): #wavelength
        with open(path, 'r') as f:
            self._calibration = yaml.safe_load(f)
        for param in self._calibration:
            setattr(self, f"_{param}", self._calibration[param])

    def calibrate(self):
        ui.SpectrometerCalibrationInterface(self).cmdloop()
        # Esto no se hace pero por ahora lo resuelvo así. Cambiar
        self.load_calibration(self.calibration_path)

    def swipe_wavelengths(self,
                          starting_wavelength: float=None,
                          ending_wavelength: float=None,
                          wavelength_step: float=None,
                          ):
        if starting_wavelength is None:
            starting_wavelength = self.monochromator.min_wl
        if ending_wavelength is None:
            ending_wavelength = self.max_wl
        if wavelength_step is None:
            wavelength_step = self.wl_step_ratio

        n_measurements = int((ending_wavelength - starting_wavelength)/wavelength_step)
        for i in range(n_measurements):
            yield self.goto_wavelength(starting_wavelength + i * wavelength_step)
        

class Spectrometer(abstract.Spectrometer):

    def __init__(self, monochromator: Monochromator,
                  osc: OscilloscopeChannel,
                  lamp: Monochromator):
        self.monochromator = monochromator
        self._osc = osc
        self.lamp = lamp

    @classmethod
    def constructor_default(cls, conn, MONOCHROMATOR=Monochromator,
                             OSCILLOSCOPE_CHANNEL=OscilloscopeChannel):
        monochromator = MONOCHROMATOR.constructor_default(conn, pin_step=6, pin_direction=7)
        osc = OSCILLOSCOPE_CHANNEL(conn, channel=0, voltage_range=20.0,
                                   decimation=1, trigger_post=None, trigger_pre=0)
        lamp = MONOCHROMATOR.constructor_default(conn, pin_step=4, pin_direction=5)
        return cls(monochromator, osc, lamp)

    # Esto se hace o directamente dejo el self.monochromator.goto_wavelength?
    def goto_wavelength(self, wavelength):
        return self.monochromator.goto_wavelength(wavelength)
    
    def goto_excitation_wavelength(self, wavelength):
        return self.lamp.goto_wavelength(wavelength)

    def get_emission(self, integration_time: float, **kwargs):
        return self.get_spectrum(monochromator=self.monochromator,
                                 integration_time=integration_time,
                                 **kwargs)

    def get_excitation(self, integration_time: float, **kwargs):
        return self.get_spectrum(monochromator=self.lamp,
                                 integration_time=integration_time,
                                 **kwargs)

    def get_spectrum(self,
                     monochromator: Monochromator,
                     integration_time: float,
                     starting_wavelength: float = None,
                     ending_wavelength: float = None,
                     wavelength_step: float = None,
                     rounds: int = 1
                     ):
        n_measurements = int((ending_wavelength - starting_wavelength)/wavelength_step)
        intensity_accum = np.zeros(n_measurements, dtype=float)
        intensity_squared_accum = np.zeros(n_measurements, dtype=float)
        for i, wl in enumerate(monochromator.swipe_wavelengths(
            starting_wavelength=starting_wavelength,
            ending_wavelength=ending_wavelength,
            wavelength_step=wavelength_step)):
            intensity_accum[i], intensity_squared_accum[i], n_datapoints = self.get_intensity(integration_time, rounds)
        return intensity_accum, intensity_squared_accum, n_datapoints

    def get_intensity(self, seconds, rounds: int = 1):
        intensity_accum = 0
        intensity_squared_accum = 0
        # Este loop sería ideal que esté lo más cerca de la RP posible
        # el problema es que igual no podemos medir de forma continua ahora
        # así que da igual un delay de 10ms con uno de 100ms. 
        for _ in range(rounds):
            data = self.integrate(seconds)
            intensity_accum += np.sum(data)
            intensity_squared_accum += np.sum(data*data)
        n_datapoints = rounds * self._osc.amount_datapoints
        return intensity_accum, intensity_squared_accum, n_datapoints

    # Debería setear la escala vertical? ver en la rp
    def integrate(self, seconds):
        self._osc.set_measurement_time(seconds)
        return self._osc.measure()

    def set_wavelength(self, wavelength: float):
        return self.monochromator.set_wavelength(wavelength)

    def set_excitation_wavelength(self, wavelength: float):
        return self.lamp.set_wavelength(wavelength)
