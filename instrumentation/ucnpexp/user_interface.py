import cmd
from typing import IO

class SpectrometerCalibrationInterface(cmd.Cmd):
    intro = '''
Spectrometer calibration interface. Type help or ? to list commands. \n
This interface aims to help you generate a calibration yaml file for the Spectrometer object.
            '''
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

This menu aims to help you determine wether the spectrometer wavelength increases clockwise (True) or counterclockwise (False).
    '''
    prompt='(growth-direction)'

    def __init__(self, spec):
        super(GrowthDirection, self).__init__()
        self.spec = spec

    def do_rotcw(self, steps: int=1):
        'Rotate monochromator motor n steps clockwise'
        try:
            steps = int(steps)
            self.spec._motor._rotate_step(steps, True)
        except:
            print("Wrong argument")
            print("Specify int steps")

    def do_rotccw(self, steps: int=1):
        'Rotate monochromator motor n steps counterclockwise'
        try:
            steps = int(steps)
            self.spec._motor._rotate_step(steps, False)
        except:
            print("Wrong argument")
            print("Specify int steps")
    
    def do_set_growth_direction(self, cw: str):
        'Set wavelength growth direction, clowckwise (True) or counterclockwise (False)'
        cw = cw.lower()
        if cw == "true":
            self.spec._greater_wl_cw = True
        elif cw == "false":
            self.spec._greater_wl_cw = False
        else:
            print("Wrong argument")
            print("Should be True or False")

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
    spec.calibrate()

