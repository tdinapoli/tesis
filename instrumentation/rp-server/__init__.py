import rpyc
import time

class RPTTL:
    def __init__(self, state, pin, gpio):
        col, num = pin
        self._gpio = gpio(col, num, 'out')
        self.exposed_set_state(state)

    @property
    def exposed_state(self):
        return self._gpio.read()

    def exposed_set_state(self, state):
        self._gpio.write(state)

    def exposed_toggle(self):
        self.exposed_set_state(not self.exposed_state)

    def exposed_pulse(self, ontime, offtime, amount=1):
        for _ in range(amount):
            self.exposed_toggle()
            time.sleep(ontime)
            self.exposed_toggle()
            time.sleep(offtime)

    def __str__(self):
        return str(self.state)

class OscilloscopeChannel:
    def __init__(self, osc, channel, range, decimation=1,
                  trigger_post=None, trigger_pre=0):
        self.osc = osc(channel, range)
        if trigger_post is None:
            self.osc.trigger_post = self.osc.buffer_size
        self.osc.trigger_pre = trigger_pre
    
    def exposed_measure(self):
        self.osc.reset()
        self.osc.start()
        self.osc.trigger()
        while (self.osc.status_run()):
            pass
        data_points = self.trigger_pre + self.trigger_post
        if data_points > self.osc.buffer_size:
            print("Warning: the amount of data points asked for is greater than the buffer size")
        return self.osc.data(data_points)

    def exposed_set_decimation(self, decimation_exponent):
        if decimation_exponent not in range(0, 18):
            print("Warning: decimation should be a power of 2 between 0 and 17")
        self.osc.decimation = 2**decimation_exponent
    
    def exposed_set_trigger_pre(self, trigger_pre):
        self.osc.trigger_pre = trigger_pre
    

class RPManager(rpyc.Service):
    def __init__(self):
        from redpitaya.overlay.mercury import mercury as FPGA
        overlay = FPGA()
        self.gpio = FPGA.gpio
        self.osc = FPGA.osc
        self.exposed_ttls = {}

    def on_connect(self, conn):
        print("RP Manager connected")

    def on_disconnect(self, conn):
        print("RP Manager disconnected")

    def exposed_create_RPTTL(self, name, config):
        state, pin = config[0], config[1:]
        ttl = RPTTL(state, pin, self.gpio)
        setattr(self, "exposed_{name}".format(name=name), ttl)
        return ttl

    def exposed_create_osc_channel(self, channel, range, decimation=1,
                                   trigger_post=None, trigger_pre=0):
        oscilloscope_channel = OscilloscopeChannel(self.osc, channel, range,
                                                    decimation=decimation,
                                                    trigger_post=trigger_post,
                                                    trigger_pre=trigger_pre)
        setattr(self, "exposed_oscilloscope_ch{channel}".format(channel=channel),
                oscilloscope_channel)


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    server = ThreadedServer(RPManager(), port=18861)
    server.start()

