if __name__ == "__main__":
    import time
    from instruments import Spectrometer

    conn = None
    while not conn:
        try:
            conn = rpyc.connect('rp-f05512.local', port=18861)
        except:
            time.sleep(1)

    spec = Spectrometer.constructor_default(conn)
    spec.calibrate_cmd()
    pass


