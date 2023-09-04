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

    def do_rot_angle(self, angle):
        'Rotate an angle (float). Positive is clockwise, negative couterclockwise.'
        try:
            # Esto puede llegar a traer problemas porque en realidad
            # angle debería ser múltiplo de 1.8. Si se hace la cuenta de
            # calibración con el angle de input puede tener un offset con 
            # el real
            angle = float(angle)
            print(f"Setting rotation angle to {angle}")
            self.rotation_angle = angle
            self.spec._motor.rotate_relative(self.rotation_angle)
        except:
            print("Wrong argument")
            print("Should be a float")
    
    def do_initial_wavelength(self, wavelength):
        'Set wavelength value before rotating'
        try:
            wavelength = float(wavelength)
            self.inital_wavelength = wavelength
        except:
            print("Wrong argument")
            print("Initial wavelenght should be float")

    def do_final_wavelength(self, wavelength):
        'Set wavelength value after rotating'
        try:
            wavelength = float(wavelength)
            self.final_wavelength = wavelength
        except:
            print("Wrong argument")
            print("Final wavelenght should be float")

    def do_set_ratio(self, arg):
        print("Calculating wavelength to degree ratio")
        print(f"Initial wavelength:\t {self.inital_wavelength}")
        print(f"Final wavelength:\t {self.final_wavelength}")
        print(f"Rotation angle:\t {self.rotation_angle}")
        ratio = (self.final_wavelength - self.inital_wavelength)/self.rotation_angle
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

