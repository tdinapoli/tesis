
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
    direction: int
    pins: dict

    def __init__(self, overlay, pins: dict, mode: int = 0):
        self.overlay = overlay

    def _configure_overlay(self, pins):
        for pin in pins:
            self.attr

    def set_mode(self, mode: int):
        pass

    def set_mode(self, mode: int):
        pass


class TTL:
    def __init__(self, GPIO, pins_dict: dict):
        self.gpio = GPIO
        self.pin_map = {}
        for pin_name, config in pins_dict.items():
            self.pin_map[pin_name] = self.gpio(*config)

        def __getattr__(self, pin_name):
            if pin_name in self.pin_map:
                return self.pin_map[pin_name].read()
            else:
                raise AttributeError(f"'TTL' object has no attribute '{pin_name}'")

        def __setattr__(self, pin_name, value):
            if pin_name in pin_map:
                if 


    def set_pin(self, column: str, pin_number: int, io: str):
        return self.gpio(column, pin_number, io)

    def set_config(self, pins_dict: dict):
        for pin in pins_dict:
            col, pin_number, io = pins_dict[pin]
            set_pin(col, pin_number, io)
class Motor:
    def __init__(self, motor_driver):
        self.motor_driver = motor_driver

    def rotate(self, angle: float, ):
        self.direction_pin.write(direction)

    def step(self, direction):
        pass




if __name__ == "__main__":
    myttl = TTL()
    myttl.step = True -> self.step.write(True)

