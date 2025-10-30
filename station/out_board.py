"""ADS1115 interface for wind direction, soil moisture, UV (voltage reads)."""

import busio
import board
from driver import config

# Correct imports for the Adafruit ADS1x15 stack:
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.ads1x15 import ADS1x15 as ADS  # for ADS.P0, ADS.P1, etc.
from adafruit_ads1x15.analog_in import AnalogIn


class OutBoard:
    def __init__(self):
        if config.DEBUG:
            return
        # I2C on Raspberry Pi (SCL/SDA)
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1115(i2c)

    def _read_voltage(self, positive_pin) -> float | None:
        """Return channel voltage in volts (None on failure)."""
        try:
            return AnalogIn(self.ads, positive_pin).voltage  # <-- volts, not counts
        except Exception as e:
            print(f"Could not read out_board on pin {positive_pin}: {e}")
            return None

    # A0: wind vane voltage
    def read_wind_direction(self) -> float | None:
        return self._read_voltage(ADS.P0)

    # A1: soil moisture voltage (you can later map V -> moisture %)
    def read_soil_moisture(self) -> float | None:
        return self._read_voltage(ADS.P1)

    # A2: UV sensor voltage
    def read_UV_light(self) -> float | None:
        return self._read_voltage(ADS.P2)
