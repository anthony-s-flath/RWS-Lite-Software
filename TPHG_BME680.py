import bme680

def initialize(inside):
    if inside:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    else:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        
    return sensor

def read_data(sensor):
    

    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    '''
    print('\n\nInitial reading:')
    for name in dir(sensor.data):
        value = getattr(sensor.data, name)

        if not name.startswith('_'):
            print('{}: {}'.format(name, value))
    '''

    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    while(not sensor.get_sensor_data()):
        pass

    if sensor.data.heat_stable:
        return sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, sensor.data.gas_resistance
    else:
        return sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, -1

    
