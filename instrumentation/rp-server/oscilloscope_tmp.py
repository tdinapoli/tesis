from redpitaya.overlay.mercury import mercury as overlay
import numpy as np
fpga = overlay()

osc0 = fpga.osc(0, 1.0)

# data rate decimation 
osc0.decimation = 50000000 // 10

# trigger timing [sample periods]
N = osc0.buffer_size
osc0.trigger_pre  = 0
osc0.trigger_post = N

# disable hardware trigger sourceosc0.trig_src = 0

# synchronization and trigger sources are the default,
# which is the module itself
osc0.reset()
osc0.start()
osc0.trigger()
# wait for data
while (osc0.status_run()): pass
print ('triggered')

import matplotlib.pyplot as plt

# show only the part of the buffer requested by pre/post trigger timing
data = osc0.data(N)
plt.plot(data)
plt.show()


def integrate(seconds):
    # data rate decimation 
    osc0.decimation = 50000000 // 10

    acq_frequency = 50000000 // 10
    
    # trigger timing [sample periods]
    buffer_size = osc0.buffer_size
    osc0.trigger_pre  = 0
    osc0.trigger_post = buffer_size

    # disable hardware trigger sources
    osc0.trig_src = 0

    accum1 = 0
    accum2 = 0
    
        
    rounds = int(np.ceil(seconds * acq_frequency / buffer_size))
    print(rounds)
    for n in range(rounds):
        osc0.reset()
        osc0.start()
        osc0.trigger()
        # wait for data
        while (osc0.status_run()):
            pass

        print("trigger", n)
        data = osc0.data(buffer_size)
        accum1 += np.sum(data)
        accum2 += np.sum(data*data)
        
    return accum1, accum2, rounds * buffer_size


def measure(seconds):
    accum1, accum2, size = integrate(seconds)
    return dict(accum1=accum1, 
                accum2=accum2,
                size=size,
                mean=accum1/size, 
                std=np.sqrt((accum2/size) - (accum1/size)**2)
               )

measure(0.01)
