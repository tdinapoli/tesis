from . import abstract
import yaml
import rpyc
from . import user_interface as ui
import numpy as np

class OscilloscopeChannel:
    # Hay una mejor forma de hacer esto no? tipo con **kwargs o *args o algo así
    def __init__(self, conn, channel, voltage_range, decimation, trigger_post, trigger_pre):
        self._maximum_sampling_rate = 125e6
        self.osc = conn.root.create_osc_channel(channel, voltage_range, decimation,
                                                 trigger_post, trigger_pre)

    def set_measurement_time(self, seconds):
        decimation_exponent = int(np.ceil(np.log2(self._maximum_sampling_rate * seconds / self.amount_datapoints)))
        self.osc.set_decimation(decimation_exponent)
        print(f"Setting measurement time to {self.get_measurement_time} seconds")

    def get_measurement_time(self):
        return self.amount_datapoints * self.osc.decimation / self._maximum_sampling_rate

    # Debería cambiarle el nombre a trigger no?
    def measure(self):
        data = self.osc.measure()
    
    @property
    def amount_datapoints(self):
        amount = self.osc.trigger_pre + self.osc.trigger_post 
        if amount > self.osc.buffer_size:
            print("Warning: amount of data points is greater than buffer size")
        return amount

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

class Spectrometer(abstract.Spectrometer):

    def __init__(self, motor: abstract.Motor, osc: OscilloscopeChannel):
        # Como puedo hacer que estas cosas sean una property?
        self.CALIB_ATTRS = [ '_wl_step_ratio',
                    '_greater_wl_cw',
                    '_max_wl',
                    '_min_wl',
                    '_wavelength']
        self._motor = motor
        self._osc = osc
        # Es necesario definir todas estas cosas? o directamente ni las defino
        [setattr(self, f"{calib_attr}", None) for calib_attr in self.CALIB_ATTRS]

    @property
    def wavelength(self):
        return self._wavelength

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

    @classmethod
    def constructor_default(cls, conn, MOTOR_DRIVER=A4988, MOTOR=M061CS02,
                             OSCILLOSCOPE_CHANNEL=OscilloscopeChannel):
        ttls = {
                'notenable' :   conn.root.create_RPTTL('notenable', (False, 'n', 0)),
                'ms1'       :   conn.root.create_RPTTL('ms1', (False, 'n', 1)),
                'ms2'       :   conn.root.create_RPTTL('ms2', (False, 'n', 2)),
                'ms3'       :   conn.root.create_RPTTL('ms3', (False, 'n', 3)),
                'notreset'  :   conn.root.create_RPTTL('notreset', (True, 'n', 4)),
                'notsleep'  :   conn.root.create_RPTTL('notsleep', (True, 'n', 5)),
                'pin_step'  :   conn.root.create_RPTTL('pin_step', (False, 'n', 6)),
                'direction' :   conn.root.create_RPTTL('direction', (True, 'p', 7)),
                }
        driver = MOTOR_DRIVER(ttls)
        motor = MOTOR(driver)
        osc = OSCILLOSCOPE_CHANNEL(conn, channel=0, voltage_range=20.0,
                                   decimation=1, trigger_post=None, trigger_pre=0)
        return cls(motor, osc)

    def set_wavelength(self, wavelength: float):
        if self.check_safety(wavelength):
            self._wavelength = wavelength
        else:
            print(f"Wavelength must be between {self._min_wl} and {self._max_wl}")

    def check_safety(self, wavelength):
        # este check no parece muy bueno. Pensar cómo mejorarlo
        #print(self._min_wl, wavelength, self._max_wl)
        return self._min_wl <= wavelength <= self._max_wl

    def goto_wavelength(self, wavelength: float):
        if self.check_safety(wavelength):
            steps = abs(int((wavelength - self._wavelength)/self._wl_step_ratio))
            cw = (wavelength - self._wavelength) > 0
            self._motor.rotate_step(steps, cw)
            self._wavelength = wavelength
        else:
            print(f"Wavelength must be between {self._min_wl} and {self._max_wl}")


    def load_calibration(self, path): #wavelength
        with open(path, 'r') as f:
            self._calibration = yaml.safe_load(f)
        for param in self._calibration:
            setattr(self, f"_{param}", self._calibration[param])
            # Esto hace que la property se agregue a la clase, y no a la
            # instancia (diferencia entre self y self.__class__). Creo que
            # En este caso no importa, pero es algo a tener en cuenta
            #setattr(self.__class__, param,
            #        property(fget=lambda self: getattr(self, f"_{param}")))

    def calibrate(self):
        ui.SpectrometerCalibrationInterface(self).cmdloop()
        # Esto no se hace pero por ahora lo resuelvo así. Cambiar
        self.load_calibration(self.calibration_path)

    def get_spectrum(self,
                     integration_time: float,
                     starting_wavelength: float = None,
                     ending_wavelength: float = None,
                     wavelength_step: float = None,
                     rounds: int = 1
                     ):
        if starting_wavelength is None:
            starting_wavelength = self.min_wl
        if ending_wavelength is None:
            ending_wavelength = self.max_wl
        if wavelength_step is None:
            wavelength_step = self.wl_step_ratio
        n_measurements = (ending_wavelength - starting_wavelength)/wavelength_step
        intensity_accum = np.zeros(n_measurements, dtype=float)
        intensity_squared_accum = np.zeros(n_measurements, dtype=float)
        for i in range(n_measurements):
            self.goto_wavelength(starting_wavelength + i * wavelength_step)
            intensity_accum[i], intensity_squared_accum[i], n_datapoints \
                                = self.get_intensity(integration_time, rounds)
        return intensity_accum, intensity_squared_accum, n_datapoints

    def get_intensity(self, seconds, rounds: int = 1):
        intensity_accum = 0
        intensity_squared_accum = 0
        # Este loop sería ideal que esté lo más cerca de la RP posible
        # el problema es que igual no podemos medir de forma continua ahora
        # así que da igual un delay de 10ms con uno de 100ms. 
        for _ in range(rounds):
            data = self.integrate(seconds)
            intensity_accum += sum(data)
            intensity_squared_accum += sum(data*data)
        n_datapoints = rounds * self._osc.amount_datapoints
        return intensity_accum, intensity_squared_accum, n_datapoints

    # Debería setear la escala vertical? ver en la rp
    def integrate(self, seconds):
        self._osc.set_measurement_time(seconds)
        return self._osc.measure()
