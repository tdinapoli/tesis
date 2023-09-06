import cmd
from typing import IO

class SpectrometerCalibrationInterface(cmd.Cmd):
    intro = '''
Spectrometer calibration interface. This interface aims to help you generate a calibration yaml file for the Spectrometer object. \n
Type help or ? to list commands.\n'''
    prompt = '(spec-calib)'
    file = None

    def __init__(self, spec):
        super(SpectrometerCalibrationInterface, self).__init__()
        self.spec = spec

    def do_maxwl(self, max_wl: float):
        'Set maximum Spectrometer wavelength'
        try:
            max_wl = float(max_wl)
            self.spec._max_wl = max_wl
        except:
            print("Wrong argument")
            print("max_wl should be float")

    def do_minwl(self, min_wl: float):
        'Set maximum Spectrometer wavelength'
        try:
            min_wl = float(min_wl)
            self.spec._min_wl = min_wl
        except:
            print("Wrong argument")
            print("min_wl should be float")
    
    def do_growth_direction(self, arg):
        'Set wavelength growth direction for the monocromator motor'
        self.gd_ui = GrowthDirection(self.spec)
        self.gd_ui.cmdloop()

    def do_wavelength_to_degree_ratio(self, arg):
        'Set wavelength to degree ratio for the spectrometer'
        self.wl_to_gd_ui = WavelengthDegreeRatio(self.spec)
        self.wl_to_gd_ui.cmdloop()

    def do_quit(self, arg):
        'Quit calibration menu'
        return True
    
    def do_print_calibration(self, arg):
        'Prints currently configured calibartion'
        directions = {True:"Clockwise", False:"Counter Clockwise", None:"None"}
        calibration_str = f'''
Max wavelength:\t\t\t {self.spec._max_wl}
Min wavelength:\t\t\t {self.spec._min_wl}
Growth direction:\t\t {directions[self.spec._greater_wl_cw]}
Wavelength to degree ratio:\t {self.spec._wl_deg_ratio}
        '''
        print(calibration_str)

class WavelengthDegreeRatio(cmd.Cmd):
    intro='''
Wavelength to degree ratio of the spectrometer configuration menu.
Type help or ? to list commands.

This menu aims to help you determine what is the value of the ratio
(wl2 - wl1)/angle
that determines how much does wavelength change (from wl1 to wl2)
for a given angle change.
    '''
    prompt='(wavelength-degree-ratio)'

    def __init__(self, spec):
        super(WavelengthDegreeRatio, self).__init__()
        self.spec = spec
        self._direction_dict = {True:"clockwise", False:"counter clockwise"}

    def do_start(self, arg):
        'Start calibration of the wavelength to degree ratio'
        done = False
        while not done:
            self.initial_wavelength = self.ask_wavelength()
            self.rot_angle()
            self.final_wavelength = self.ask_wavelength()
            done = self.ask_done()
        print("Calculating...")
        wl_deg_ratio = self.calculate_ratio()
        print(f"Setting wavelength to degree ratio to {wl_deg_ratio} nm/deg")
        self.spec._wl_deg_ratio = wl_deg_ratio
        self.onecmd('quit')

    def do_quit(self, arg):
        'Go back to main calibration menu'
        return True

    def calculate_ratio(self):
        ratio = (self.final_wavelength - self.initial_wavelength)/self.rotation_angle
        print(self.final_wavelength, self.initial_wavelength, self.rotation_angle)
        return ratio

    def ask_done(self):
        print("Calibration parameters you input:")
        print(f"Initial wavelength:\t\t{self.initial_wavelength}")
        print(f"Rotation angle:\t\t{self.rotation_angle}")
        print(f"Final wavelength:\t\t{self.final_wavelength}")
        answer = input("Do you want to calculate wavelength to degree ratio?[Y/n]").lower()
        done = answer in ["y", ""]
        if not done:
            print("Aborting...")
        return done

    def rot_angle(self):
        angle = input("Input a rotation angle for the motor in degrees: ")
        try:
            angle = float(angle)
            self.rotation_angle = angle
            self.rotation_angle = self.spec._motor.rotate_relative(self.rotation_angle)
            print(f"Rotate {angle} degrees {self._direction_dict[self.rotation_angle > 0]}")
        except:
            print("Wrong argument")
            print("Rotation angle should be a float")
    
    def ask_wavelength(self):
        keep_going  = True
        while keep_going:
            wavelength = input("Input current wavelength in nm: ")
            try:
                wavelength = float(wavelength)
                print(f"The spectrometer is now at {wavelength} nm")
                keep_going = False
            except:
                print("Wrong argument")
                print("wavelenght should be a float")
        return wavelength

    def do_set_ratio(self, arg):
        print("Calculating wavelength to degree ratio")
        print(f"Initial wavelength:\t {self.initial_wavelength}")
        print(f"Final wavelength:\t {self.final_wavelength}")
        print(f"Rotation angle:\t {self.rotation_angle}")
        ratio = (self.final_wavelength - self.initial_wavelength)/self.rotation_angle
        print(f"(final_wl - initial_wl)/angle = {ratio}")
        self.spec._wl_deg_ratio = ratio
        
    
class GrowthDirection(cmd.Cmd):
    intro='''
Growth direction of the monochromator motor configuration menu.
Type help or ? to list commands.

This menu aims to help you determine wether the spectrometer wavelength increases clockwise (True)
or counterclockwise (False).
Input l to turn 10 steps counter clockwise.
Input r to turn 10 steps clockwise.
Input L to turn 100 steps counter clockwise.
Input R to turn 100 steps clockwise.
Input set_growth_direction to set the growth direction.
    '''
    prompt=f'(growth-direction)'

    def __init__(self, spec):
        super(GrowthDirection, self).__init__()
        self.spec = spec
        self.steps = 1
        self.small_rotation = 10
        self.large_rotation = 100

    def do_r(self, arg):
        'Rotate monochromator motor 10 steps clockwise'
        self.spec._motor._rotate_step(self.small_rotation, True)

    def do_l(self, arg):
        'Rotate monochromator motor 10 steps clockwise'
        self.spec._motor._rotate_step(self.small_rotation, False)

    def do_R(self, arg):
        'Rotate monochromator motor 100 steps clockwise'
        self.spec._motor._rotate_step(self.large_rotation, True)

    def do_L(self, arg):
        'Rotate monochromator motor 100 steps clockwise'
        self.spec._motor._rotate_step(self.large_rotation, False)

    def do_set_growth_direction(self, cw: str):
        '''Set wavelength growth direction.\n
Usage: Input True for clowckwise or False for counter clockwise'''
        cw = cw.lower()
        if cw == "true":
            self.spec._greater_wl_cw = True
            return True
        elif cw == "false":
            self.spec._greater_wl_cw = False
            return True
        else:
            print("Wrong argument")
            self.onecmd("help set_growth_direction")

class TestMotor:
    def __init__(self):
        self.directions = {True:"cw", False:'ccw'}

    def _rotate_step(self, steps, direction):
        print(f"rotate {steps} steps in {self.directions[direction]} direction")

    def rotate_relative(self, angle):
        print(f"rotate {angle}")
        return angle

class TestSpec:
    def __init__(self):
        self._motor = TestMotor()
        self._max_wl = None
        self._min_wl = None
        self._wl_deg_ratio = None
        self._greater_wl_cw = None

    def calibrate(self):
        ui = SpectrometerCalibrationInterface(self)
        ui.cmdloop()

if __name__ == '__main__':
    spec = TestSpec()
    hola = spec.calibrate()
    print(hola)

