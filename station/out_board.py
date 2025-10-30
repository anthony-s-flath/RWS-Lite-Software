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
        self.bus = board.I2C(board.SCL, board.SDA)
        self.ads = ADS1115(self.bus)

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
        try:
            voltage =  AnalogIn(self.ads, ads1x15.Pin.A2).voltage
        except:
            print("Could not read out_board on pin %s", ads1x15.Pin.A2)
            return None
        
        real = 10000 * 3.3 / voltage - 10000
        return real

