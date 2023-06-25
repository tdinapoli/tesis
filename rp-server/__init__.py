import rpyc
import time

class RPTTL:
    def __init__(self, state, pin, gpio):
        col, num = pin
        self._gpio = gpio(col, num, 'out')
        self.exposed_state = state

    @property
    def exposed_state(self):
        return self._get_state()

    @state.setter(self, state):
    def exposed_state(self, state):
        self._set_state(state)

    def _get_state(self):
        return self._gpio.read()

    def _set_state(self, state):
        self._gpio.write(state)

    def exposed_toggle(self):
        self.exposed_state = not self.exposed_state

    def exposed_pulse(self, duration):
        self.exposed_toggle()
        time.sleep(duration)
        self.exposed_toggle()

    def __str__(self):
        return str(self.state)


class TTL_Manager(rpyc.Service):
    def __init__(self):
        from redpitaya.overlay.mercury import mercury as FPGA
        overlay = FPGA()
        self.gpio = FPGA.gpio
        self.exposed_ttls = {}

    def on_connect(self, conn):
        print("TTL Manager connected")

    def on_disconnect(self, conn):
        print("TTL Manager disconnected")

    def exposed_create_RPTTL(self, name, config):
        state, pin = config[0], config[1:]
        ttl = RPTTL(state, pin, self.gpio)
        setattr(self, "exposed_{name}".format(name=name), ttl)
        return ttl

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    server = ThreadedServer(TTL_Manager(), port=18861)
    server.start()

