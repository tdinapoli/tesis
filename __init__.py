import abstract


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
    def steps(self, steps: int = 200):
        return self._STEPS_MODE[self._driver.get_stepping()]

    @steps.setter
    def steps(self, steps: int = 200):
        self._driver.set_stepping(self._STEPS_MODE.index(steps))

    def set_origin(self):
        self._angle = 0.0


class Spectrometer:
    def __init__(self, motor):
        self.motor = motor

    def set_wavelength(self, wavelength: float):
        angle = self._angle_from_wl(wavelength)
        self.motor.rotate(angle)

    def _angle_from_wl(self, wavelength: float):
        raise NotImplementedError

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
    ttls = {
            'notenable':RPTTL(False, ('n', 0), GPIO_helper),
            'ms1'   :   RPTTL(False, ('n', 1), GPIO_helper),
            'ms2'   :   RPTTL(False, ('n', 2), GPIO_helper),
            'ms3'   :   RPTTL(False, ('n', 3), GPIO_helper),
            'notreset': RPTTL(True, ('n', 4), GPIO_helper),
            'notsleep': RPTTL(True, ('n', 5), GPIO_helper),
            'pin_step'  :   RPTTL(False, ('n', 6), GPIO_helper),
            'direction':RPTTL(True, ('n', 7), GPIO_helper),
            }

    driver = A4988(ttls)
    motor = M061CS02(driver)
    print(motor.angle)
    motor.rotate(180, True)
    print(motor.angle)
    motor.rotate_relative(180, True)
    print(motor.angle)

    pass

