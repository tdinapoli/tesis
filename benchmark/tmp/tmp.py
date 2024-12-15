from redpipy.rpwrap import init
from refurbishedPTI.instruments import Spectrometer

init()

spec = Spectrometer.constructor_default()
spec.excitation_mono.set_wavelength(510)
spec.emission_mono.set_wavelength(520)
print(f"{spec._osc.channel1.enabled=}") 
print(f"{spec._osc.channel2.enabled=}") 

def profile_this():
    iterator = spec._yield_spectrum(integration_time=1, starting_wavelength=520, ending_wavelength=521, wavelength_step=1) 

    for a in iterator:
        print(a)
profile_this()

