import abstract
import yaml

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
    notenable: RPTTL
    ms1: RPTTL
    ms2: RPTTL
    ms3: RPTTL
    notreset: RPTTL
    notsleep: RPTTL
    pin_step: RPTTL
    direction: RPTTL
    ttls: dict
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
        self.ms1.state, self.ms2.state, self.ms3.state = self._MODES[mode]

    def get_stepping(self):
        return self._MODES.index((self.ms1.state, self.ms2.state, self.ms3.state))

    #Obs: creo que la minima duracion del pulso es 1 micro segundo
    #Obs2: para q funcione el step debe ir de low a high. Si se 
    # Desconfigura a mano el step (por ejemplo poniendo 
    # driver.step.state = True), esta driver.step() no va a hacer lo
    # esperado (pensar cómo solucionar).
    def step(self, duration=1e-6):
        self.pin_step.pulse(duration)
    

class M061CS02(abstract.Motor):
    _STEPS_MODE = (200, 400, 800, 1600, 3200)

    def __init__(self, driver, steps: int = 200, angle: float = 0.0):
        self._driver = driver
        self._angle = angle
        self._angle_relative = angle % 360
        self.steps = steps
        self._min_angle = 360.0/self.steps
        self._min_pulse_duration = 1e-6

    def rotate(self, angle: float, cw: bool):
        angle_change_sign = (int(cw)*2 - 1)
        self._driver.direction.state = cw
        while abs(round(self._angle - angle, 5)) >= self._min_angle:
            self._driver.step(duration = self._min_pulse_duration)
            self._angle +=  angle_change_sign * self._min_angle
        self._angle = round(self._angle, 5)

    def rotate_relative(self, angle: float, cw: bool, change_angle: bool = True):
        angle_done = 0.0
        self._driver.direction.state = cw
        while abs(round(angle - angle_done, 5)) >= self._min_angle:
            self._driver.step(duration = self._min_pulse_duration)
            angle_done += self._min_angle
        if change_angle:
            angle_change_sign = (int(cw)*2 - 1)
            self._angle = round(self._angle + angle_change_sign * angle_done, 5)

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

    def set_origin(self, angle):
        self._angle = angle


class Spectrometer(abstract.Spectrometer):
    def __init__(self, motor: abstract.Motor):
        self._motor = motor
        # Es necesario definir todas estas cosas? o directamente ni las defino
        self._wavelength = None # nm
        self._greater_wl_cw = None 
        self._wl_angle_ratio = None # nm/degree
        self._calibration = None
        self._max_wl = None
        self._min_wl = None

    @classmethod
    def constructor_default(cls):
        ttls = {
                'notenable' :   RPTTL(False, ('n', 0), GPIO_helper),
                'ms1'       :   RPTTL(False, ('n', 1), GPIO_helper),
                'ms2'       :   RPTTL(False, ('n', 2), GPIO_helper),
                'ms3'       :   RPTTL(False, ('n', 3), GPIO_helper),
                'notreset'  :   RPTTL(True , ('n', 4), GPIO_helper),
                'notsleep'  :   RPTTL(True , ('n', 5), GPIO_helper),
                'pin_step'  :   RPTTL(False, ('n', 6), GPIO_helper),
                'direction' :   RPTTL(True , ('n', 7), GPIO_helper),
                }
        driver = A4988(ttls)
        motor = M061CS02(driver)
        return Spectrometer(motor)

    # Esto es necesario?
    def set_wavelength(self, wavelength: float):
        self._wavelength = wavelength

    def check_safety(self, wavelength):
        # este check no parece muy bueno. Pensar cómo mejorarlo
        if self._min_wl < wavelength < self._max_wl:
            return True
        else:
            return False 

    def goto_wavelength(self, wavelength: float):
        angle, cw = self._goto_wavelength(wavelength)
        if self.check_safety(wavelength):
            self._motor.rotate_relative(angle, cw)

    def _goto_wavelength(self, wavelength: float):
        cw = self._cw_from_wl(wavelength)
        angle = self._angle_from_wl(wavelength)
        return angle, cw

    # Tabla de verdad para saber si ir cw o counter cw:
    # self._greater_wl_cw | wl_dif > 0 | cw
    # 1 | 1 | 1
    # 1 | 0 | 0
    # 0 | 1 | 0
    # 0 | 0 | 1
    # Equivalente a (wl_dif > 0) == self._greater_wl_cw
    def _cw_from_wl(self, wavelength):
        wl_dif = wavelength - self._wavelength
        if (wl_dif > 0) == self._greater_wl_cw:
            return True
        else:
            return False

    def _angle_from_wl(self, wavelength: float, cw: bool):
        angle = abs(wavelength - self._wavelength)/self._wl_deg_ratio
        return angle

    def load_calibration(self, path): #wavelength
        with open(path, 'r') as f:
            self._calibration = yaml.safe_load(f)
        for param in self._calibration:
            setattr(self, f"_{param}", self._calibration[param])
            # Esto hace que la property se agregue a la clase, y no a la
            # instancia (diferencia entre self y self.__class__). Creo que
            # En este caso no importa, pero es algo a tener en cuenta
            setattr(self.__class__, param,
                    property(fget=lambda self: getattr(self, f"_{param}")))


class GPIO_helper:
    def __init__(self, column: str, pin: int, io: str):
        self.column = column
        self.pin = pin
        self.io = io
        self.state = True

    def write(self, state: bool):
        self.state = state

    def read(self):
        return self.state

if __name__ == "__main__":
    spec = Spectrometer.constructor_default()
    spec.load_calibration("calibration.yaml")
    print(spec.max_wl)
    pass

