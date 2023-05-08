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
    step: RPTTL
    direction: RPTTL
    ttls: dict
    modes = (
            (False, False, False), #Full step
            (True, False, False) , #Half 
            (False, True, False) , #Quarter
            (True, True, False)  , #Eighth
            (True, True, True)   , #Sixteenth
            )

    def __init__(self, ttls: dict, mode: int = 0):
        for ttl in ttls:
            setattr(self, ttl, ttls[ttl])
        self.notreset.state = True
        self.notenable.state = False
        self.notsleep.state = True
        self.direction.state = True
        self.step.state = False
        self.set_stepping(0)

    def set_stepping(self, mode: int):
        self.ms1.state, self.ms2.state, self.ms3.state = modes[mode]

    #Obs: creo que la minima duracion del pulso es 1 micro segundo
    #Obs2: para q funcione el step debe ir de low a high. Si se 
    # Desconfigura a mano el step (por ejemplo poniendo 
    # driver.step.state = True), esta driver.step() no va a hacer lo
    # esperado (pensar cómo solucionar).
    def step(self, duration=1e-6):
        self.step.pulse(duration)
    

class Motor:
    def __init__(self, driver):
        self.driver = driver

    def rotate(self, angle: float, direction: str):
        self.driver.direction = direction

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
            'enable':   RPTTL(True, ('n', 0), GPIO_helper),
            'ms1'   :   RPTTL(True, ('n', 1), GPIO_helper),
            'ms2'   :   RPTTL(True, ('n', 2), GPIO_helper),
            'ms3'   :   RPTTL(True, ('n', 3), GPIO_helper),
            'notreset': RPTTL(True, ('n', 4), GPIO_helper),
            'notsleep': RPTTL(True, ('n', 5), GPIO_helper),
            'step'  :   RPTTL(True, ('n', 6), GPIO_helper),
            'direction':RPTTL(True, ('n', 7), GPIO_helper),
            }

    driver = A4988(ttls)
    print(driver.step.state)
    driver.step.state = False
    print(driver.step.state)
    driver.step.toggle()
    print(driver.step.state)
    driver.step.pulse(0)
    pass

