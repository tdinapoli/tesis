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
    def __init__(self, osc, channel, voltage_range, decimation=1,
                  trigger_post=None, trigger_pre=0):
        self.osc = osc(channel, voltage_range)
        self._channel = channel
        if trigger_post is None:
            self.osc.trigger_post = self.osc.buffer_size
        else:
            self.osc.trigger_post = trigger_post
        self.osc.trigger_pre = trigger_pre
        self._maximum_sampling_rate = 125e6
    
    def exposed_measure(self, data_points=None, transit_seconds=0):
        if data_points is None:
            data_points = self.osc.buffer_size
        if data_points > self.osc.buffer_size:
            print("Warning: the amount of data points asked for is greater than the buffer size")
        self.osc.reset()
        self.osc.start()
        time.sleep(transit_seconds)
        # acá probablemente tenga que agregar un sleep o algo así pq
        # Si trigger_pre es >0 debería dejar al osciloscopio correr un rato
        # Antes de apretar el trigger para que tome datos.
        time.sleep(self.osc.trigger_pre * self.osc.decimation / self._maximum_sampling_rate)
        self.osc.trigger()
        while (self.osc.status_run()):
            pass
        return self.osc.data(data_points)

    def exposed_set_decimation(self, decimation_exponent):
        if decimation_exponent not in range(0, 18):
            print("Warning: decimation should be a power of 2 between 0 and 17")
        self.osc.decimation = 2**decimation_exponent
    
    def exposed_set_trigger_pre(self, trigger_pre):
        print(trigger_pre)
        self.osc.trigger_pre = int(trigger_pre)

    def exposed_set_trigger_post(self, trigger_post):
        print(trigger_post)
        self.osc.trigger_post = int(trigger_post)

    def exposed_decimation(self):
        return self.osc.decimation

    def exposed_buffer_size(self):
        return self.osc.buffer_size

    def exposed_trigger_pre(self):
        return self.osc.trigger_pre
    
    def exposed_trigger_post(self):
        return self.osc.trigger_post

    def exposed_decimation(self):
        return self.osc.decimation

    def exposed_buffer_size(self):
        return self.osc.buffer_size

    # Esto tira algún tipo de warning que después 
    # Tengo que ver qué significa
    # Pero por ahora parece que funciona
    def exposed_delete(self):
        del self.osc

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

    def exposed_create_osc_channel(self, *, channel, voltage_range, decimation=1,
                                   trigger_post=None, trigger_pre=0):
        oscilloscope_channel = OscilloscopeChannel(self.osc, channel, voltage_range,
                                                    decimation=decimation,
                                                    trigger_post=trigger_post,
                                                    trigger_pre=trigger_pre)
        setattr(self, "exposed_oscilloscope_ch{channel}".format(channel=channel),
                oscilloscope_channel)
        return oscilloscope_channel


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

    server = ThreadedServer(RPManager(), port=18861)
    server.start()

