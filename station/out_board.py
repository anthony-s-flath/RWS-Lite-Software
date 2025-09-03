"""ADS1115"""

import busio
import board
from driver.config import DEBUG
if not DEBUG:
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

# originally used as ADS1115.ADS1115():
# #   readADCSingleEnded(channel=0)
# seems like its on some old documentation
# not sure if this is correct: value vs voltage?


class OutBoard:
    def __init__(self):
        if DEBUG:
            return
        self.ads = ADS.ADS1115(busio.I2C(board.SCL, board.SDA))

    # read_A0
    def read_wind_direction(self):
        return AnalogIn(self.ads, ADS.P0).value

    # read_A1
    def read_soil_moisture(self):
        return AnalogIn(self.ads, ADS.P1).value

    # read_A2
    def read_UV_light(self):
        return AnalogIn(self.ads, ADS.P2).value
