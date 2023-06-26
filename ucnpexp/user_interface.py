import cmd

class SpectrometerCalibrationInterface(cmd.Cmd):
    intro = 'Spectrometer calibration interface. Type help or ? to list commands. \n'
    prompt = '(spec-calib)'
    file = None

    def __init__(self, spec):
        super(SpectrometerCalibrationInterface, self).__init__()
        self.spec = spec

    def do_maxwl(self, max_wl: float):
        'Set maximum Spectrometer wavelength'
        self.spec._max_wl = float(max_wl)

    def do_quit(self, arg):
        'Quit calibration menu'
        return True

class TestSpec:
    def calibrate(self):
        ui = SpectrometerCalibrationInterface(self)
        ui.cmdloop()
    pass

if __name__ == '__main__':
    spec = TestSpec()
    spec.calibrate()

