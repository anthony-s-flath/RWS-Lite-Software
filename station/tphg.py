"""Orignal file name: TPHG_BME680.py"""

import bme680


class BMEs:
    def __init__(self):
        try:
            self.inside = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        except Exception as e:
            print(e)
            print("could not initialize inside BME680")
        try:
            self.outside = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except Exception as e:
            print(e)
            print("could not initialize outside BME680")

    def reinit(self, is_inside: bool):
        if (is_inside):
            try:
                self.inside = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
            except Exception as e:
                print(e)
                print("could not re-initialize inside BME680")
        else:
            try:
                self.outside = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
            except Exception as e:
                print(e)
                print("could not re-initialize outside BME680")

    def in_data(self):
        return self.read_data(self.inside)

    def out_data(self):
        return self.read_data(self.outside)

    def read_data(self, sensor : bme680.BME680):
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)
        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)

        while (not sensor.get_sensor_data()):
            pass

        t = sensor.data.temperature
        p = sensor.data.pressure
        h = sensor.data.humidity
        g = sensor.data.gas_resistance

        if sensor.data.heat_stable:
            return t, p, h, g
        else:
            return t, p, h, -1
