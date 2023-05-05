from abc import ABC, abstractmethod


class Motor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def rotate(self, angle: float, cw: bool):
        # informarle al driver cuantos pulsos y direccion

class Spectrometer(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def set_current_wavelength(self, wavelength: float):
        pass
    
    def goto_wavelength(self, wavelength):
        pass
    
    def _goto_wavelength(self, wavelength):
        # return angulo y direccion
        # teniendo en cuenta la calibracion y posicion del motoro

class MotorDriver(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def step(self):
        pass

class TTL:

    def __init__(self, state):
        self.state = state

    @property
    def state(self):
        return self._get_state()
    
    @state.setter
    def state(self, state):
        self._set_state(state)
    
    @abstractmethod
    def _get_state(self):
        pass
       
    @abstractmethod
    def _set_state(self, state):
        pass
    
    def toggle(self) -> None:
        self.state = not self.state
    
    def __str__(self):
        return str(self.state)
    


