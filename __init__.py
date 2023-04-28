
class A4988:
    enable: int
    a1: int
    a2: int
    b1: int
    b2: int
    ms1: int
    ms2: int
    ms3: int
    notreset: int
    notsleep: int
    step: int
    dir: int


class TTL:
    def __init__(self, GPIO):
        self.gpio = GPIO

    def set_pin(self, column: str, pin_number: int, io: str):
        return self.gpio(column, pin_number, io)

class Motor:
    def __init__(self, direction_pin, step_pin):
        self.direction_pin = direction_pin
        self.step_pin = step_pin

    def set_direction(self, direction: bool):
        self.direction_pin.write(direction)

    def step(self, direction):


