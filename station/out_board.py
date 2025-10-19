"""ADS1115"""


import busio
import board
from driver.config import DEBUG
if not DEBUG:
    from adafruit_ads1x15 import ads1x15, AnalogIn, ADS1115
    # specific to Raspberry Pi 4
    from adafruit_blinka.microcontroller.bcm2711 import pin

# originally used as ADS1115.ADS1115():
# #   readADCSingleEnded(channel=0)
# seems like its on some old documentation
# not sure if this is correct: value vs voltage?


class OutBoard:
    def __init__(self):
        if DEBUG:
            return
        # board.SCL and board.SDA don't exist
        # are they automatically configured? 
        #self.ads = ADS1115(busio.I2C(board.SCL, board.SDA))
        self.ads = ADS1115(busio.I2C(pin.SCL, pin.SDA))
        self.ads = ADS1115(board.I2C())

    # read_A0
    def read_wind_direction(self):
        return AnalogIn(self.ads, ads1x15.Pin.A0).value

    # read_A1
    def read_soil_moisture(self):
        return AnalogIn(self.ads, ads1x15.Pin.A1).value

    # read_A2
    def read_UV_light(self):
        return AnalogIn(self.ads, ads1x15.Pin.A2).value
