from w1thermsensor import W1ThermSensor

def readSoilTemp():
    sensor = W1ThermSensor()

    return sensor.get_temperature()

