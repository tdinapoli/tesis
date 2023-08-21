if __name__ == "__main__":
    import time
    import rpyc
    from instruments import Spectrometer

    conn = None
    while not conn:
        try:
            print("Trying connection...")
            conn = rpyc.connect('rp-f05512.local', port=18861)
        except:
            time.sleep(1)

    spec = Spectrometer.constructor_default(conn)
    spec.calibrate()
    pass


