from . import abstract
import yaml
import rpyc
from . import user_interface as ui
import numpy as np

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
    def step(self, ontime=10e-6, offtime=10e-6, amount=1):
        self.pin_step.pulse(ontime, offtime, amount)
    

class M061CS02(abstract.Motor):
    _STEPS_MODE = (200, 400, 800, 1600, 3200)

    def __init__(self, driver, steps: int = 200, angle: float = 0.0):
        self._driver = driver
        self._angle = angle
        self._angle_relative = angle % 360
        self.steps = steps
        self._min_angle = 360.0/self.steps
        self._min_offtime = 10e-6
        self._min_ontime = 10e-6

    def rotate(self, angle: float):
        relative_angle = angle - self._angle
        self.rotate_relative(relative_angle)

    def rotate_relative(self, angle: float, change_angle: bool = True):
        cw, angle = angle > 0, abs(angle)
        self._driver.direction.set_state(cw)
        steps = int(angle/self._min_angle)
        self.rotate_step(steps, cw, change_angle=change_angle)

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

    def set_origin(self, angle):
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
    CALIB_ATTRS = [ '_wl_deg_ratio',
                    '_greater_wl_cw',
                    '_max_wl',
                    '_min_wl',
                    '_wavelength']

    def __init__(self, motor: abstract.Motor):
        self._motor = motor
        # Es necesario definir todas estas cosas? o directamente ni las defino
        [setattr(self, f"_{calib_attr}", None) for calib_attr in CALIB_ATTRS]

    @classmethod
    def constructor_default(cls, conn, MOTOR_DRIVER=A4988, MOTOR=M061CS02):
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
        return cls(motor)

    # Esto es necesario?
    def set_wavelength(self, wavelength: float):
        self._wavelength = wavelength

    def check_safety(self, wavelength):
        # este check no parece muy bueno. Pensar cómo mejorarlo
        return self._min_wl < wavelength < self._max_wl

    def goto_wavelength(self, wavelength: float):
        angle = (wavelength - self._wavelength)/self._wl_deg_ratio
        if self.check_safety(wavelength):
            self._motor.rotate_relative(angle)

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

    def _calibration_options(self):
        print()
        print("abort: q")
        print("set max wl: mxwl")
        print("set min wl: mnwl")
        print("set wl growth direction: wgd")
        print("set wl to deg ratio: wdeg")
        print("set current wl in nm: wl")
        print("write to file: write")
        print("print calibration status: s")
        print("show this message: h")
        print("\n")

    def _write_calibration_file(self, filename):
        with open(filename, "w") as f:
            calibration_dict = self.get_calibration_dict()
            yaml.dump(calibration_dict, f)

    def status(self):
        for attr in self.CALIB_ATTRS:
            if not getattr(self, attr):
                return False
        return True

    def get_calibration_dict(self):
        calibration_dict = {}
        for attr in self.CALIB_ATTRS:
            calibration_dict[attr[1:]] = getattr(self, attr)
        return calibration_dict

    def _wgd_menu(self):
        print('abort: a')
        print('rotate clowckwise: cw')
        print('rotate counterclockwise: ccw')
        print('rotate n steps: r')
        print('wavelength grows clockwise: cwg')
        print('wavelength grows counterclockwise: ccwg')

    def _wgd_is_clockwise(self):
        cw = None
        cmd = ''
        while cmd != 'a':
            cmd = input('input command: ')
            if cmd == 'cw':
                cw = True
            elif cmd == 'ccw':
                cw = False
            elif cmd == 'r':
                if cw is not None:
                    steps = input('amount of steps: ')
                    try:
                        steps = int(steps)
                        print(self._motor.angle)
                        self._motor.rotate_step(steps, cw)
                        print(self._motor.angle)
                    except:
                        print(steps, type(steps))
                        print("invalid input")
                        self._wgd_menu()
                        cmd = ''
                else:
                    print("define cw first")
            elif cmd == 'cwg':
                return True
            elif cmd == 'ccwg':
                return False
            elif cmd == '' or cmd == 'a':
                pass
            else:
                print("invalid command")
        return None

    def _wdeg_functionality(self):
        cw = None
        cmd = ''
        cmd = input('input clockwise(t) or counterclockwise(f): ')
        if cmd == 't':
            cw = True
        elif cmd == 'f':
            cw = False
        else:
            print('invalid command')
            print('aborting...')
            return None
        degs = input('input rotation angle (in deg): ')
        try:
            degs = float(degs)
            print(self._motor.angle)
            self._motor.rotate_relative(degs, cw)
            print(self._motor.angle)
        except:
            print("invalid input")
            print("aborting...")
            return None
        wl_change = input('input wl change in nm: ')
        try:
            wl_change = float(wl_change)
        except:
            print('invalid input')
            print('aborting...')
            return None
        return wl_change/degs

    def calibrate_cmd(self):
        ui.SpectrometerCalibrationInterface(self)


    def calibrate(self):
        print("Calibration menu ")
        cmd = "h"
        self._calibration_options()
        while cmd != 'q':
            print()
            cmd = input('input command: ')
            if cmd == 'mxwl':
                print("input max wavelength value in nm: ")
                max_wl = input()
                try:
                    self._max_wl = float(max_wl)
                except:
                    print("invalid input")
                    cmd = ''
            elif cmd == 'mnwl':
                print("input min wavelength value in nm: ")
                min_wl = input()
                try:
                    self._min_wl = float(min_wl)
                except:
                    print("invalid input")
                    cmd = ''
            elif cmd == 'wgd':
                self._wgd_menu()
                self._greater_wl_cw = self._wgd_is_clockwise()
            elif cmd == 'wdeg':
                self._wl_deg_ratio = self._wdeg_functionality()
            elif cmd == 'write':
                if self.status():
                    print("Enter calibration full path: \n")
                    path = input()
                    self._write_calibration_file(path)
                else:
                    print("Complete calibration first")
            elif cmd == 's':
                print()
                for attr in self.CALIB_ATTRS:
                    print(f"{attr[1:]}: {getattr(self, attr)}")
                print(f"calibration complete: {self.status()}")
            elif cmd == 'wl':
                wl = input("input current wl (in nm): ")
                try:
                    wl = float(wl)
                    self.set_wavelength(wl)
                except:
                    print("invalid input")
                    cmd = ''
            elif cmd == 'h':
                self._calibration_options()
            elif cmd == 'q':
                pass
            elif cmd == '':
                pass
            else:
                print("invalid command")

