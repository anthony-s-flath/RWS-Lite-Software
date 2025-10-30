"""ADS1115"""


import busio
import board
from driver import config
from adafruit_ads1x15 import ads1x15, AnalogIn, ADS1115
import adafruit_veml6075
    # specific to Raspberry Pi 4
    #from adafruit_blinka.microcontroller.bcm2711 import pin

# originally used as ADS1115.ADS1115():
# #   readADCSingleEnded(channel=0)
# seems like its on some old documentation
# not sure if this is correct: value vs voltage?


class OutBoard:
    def __init__(self):
        if config.DEBUG:
            return
        self.ads = ADS1115(busio.I2C(board.SCL, board.SDA))

    def try_read(self, pin: ads1x15.Pin) -> float:
        try:
            return AnalogIn(self.ads, pin).value
        except:
            print("Could not read out_board on pin %s", pin)
            return None

    # read_A0
    def read_wind_direction(self) -> int:
        return self.try_read(ads1x15.Pin.A0)

    # read_A1
    def read_soil_moisture(self) -> int:
        return self.try_read(ads1x15.Pin.A1)

    # read_A2
    def read_UV_light(self) -> int:
        #return self.try_read(ads1x15.Pin.A2)
        i2c = busio.I2C(board.SCL, board.SDA)

        veml = adafruit_veml6075.VEML6075(i2c, integration_time=100)

        datum = veml.uv_index
        return self.try_read(ads1x15.Pin.A2)
