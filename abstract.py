from abc import ABC, abstractmethod

class Motor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def rotate(self, angle: float, direction: str):
        pass

class Spectrometer(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def set_wavelength(self, wavelength: float):
        pass

class MotorDriver(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def step(self):
        pass

class TTL(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def pulse(self, duration: float):
        pass

class RPTTL(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def pulse(self, pin: int, duration: float):
        pass
