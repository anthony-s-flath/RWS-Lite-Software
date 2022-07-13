import datetime
import time
import pigpio
import ADS1115
import TPHG_BME680
import DS18B20
import RD200
import smbus

POLL_RATE = .2 #Hz
SOIL_MOISTURE_MIN = 0 #counts
SOIL_MOISTURE_MAX = 3380 #counts

numInterrupts = 0
global is_raining
is_raining = False
last_rain_time = datetime.datetime.now()


def cb_func(gpio, level, tick):
    global is_raining
    is_raining = True
    last_rain_time = datetime.datetime.now()

def wind_speed_func(gpio, level, tick):
    global numInterrupts
    numInterrupts += 1



'''
Takes counts from the soil moisture sensor as input and remaps
the values to calibrated points
'''
def soilMoisture(counts):
    return (counts.value - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)

def windDirection(counts):
    voltage = counts.voltage
    # 16 possible values 
    vals = ((0, 33000),
            (22.5, 6570),
            (45, 8200),
            (67.5, 891),
            (90, 1000),
            (112.5, 688),
            (135, 2200),
            (157.5, 1410),
            (180, 3900),
            (202.5, 3140),
            (225, 16000),
            (247.5, 14120),
            (270, 120000),
            (292.5, 42120),
            (315, 64900),
            (337.5, 21880))

    # solve for resistance using voltage divider
    # 10000 is another resistor
    r = 10000*voltage / (3.3-voltage)

    # get the index of the closest distance
    distances = [ abs(r - vals[x][1]) for x in range(0, 16) ]
    closest_index = min(range(len(distances)), key=distances.__getitem__)

    return vals[closest_index][0]


PIN_RAIN = 20
PIN_WIND_SPEED = 21


pi = pigpio.pi()
pi.set_mode(PIN_RAIN, pigpio.INPUT)
pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)


cb = pi.callback(PIN_RAIN, pigpio.RISING_EDGE, cb_func)
wind_speed = pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, wind_speed_func)

inside = TPHG_BME680.initialize(True)
outside = TPHG_BME680.initialize(False)

bus = smbus.SMBus(1)
DIYgm = 0x13

while (True):
    windspeed = 2.4 * numInterrupts / (1/POLL_RATE)
    try:
        intemperature, inpressure, inhumidity, ingas_resistance = TPHG_BME680.read_data(inside)
        print(f"INSIDE temperature: {intemperature} pressure: {inpressure} humidity: {inhumidity} gas_resistance {ingas_resistance}")
    except Exception as e:
        print("Could not read internal atmosphere")
        
    try:
        outtemperature, outpressure, outhumidity, outgas_resistance = TPHG_BME680.read_data(outside)
        print(f"OUTSIDE temperature: {outtemperature} pressure: {outpressure} humidity: {outhumidity} gas_resistance {outgas_resistance}")
    except Exception as e:
        print("Could not read outside atmosphere")
        
    try:
        winddirection = windDirection(ADS1115.read_A0())
        print(f"wind direction: {winddirection} windspeed: {windspeed} is_raining: {is_raining}")
    except Exception as e:
        print("Could not read wind direction (check ADC)")
        
    try:
        soiltemperature = DS18B20.readSoilTemp()
        print(f"soil temperature: {soiltemperature}")
    except Exception as e:
        print("Could not read soil temperature")
        
    try:
        soilmoisture = soilMoisture(ADS1115.read_A1())
        print(f"soil moisture: {soilmoisture}")
    except Exception as e:
        print("Could not read soil moisture (check ADC)")
        
    try:
        uv = ADS1115.read_A2().value
        print(f"UV: {uv}")
    except Exception as e:
        print("Could not read UV (check ADC)")
    
    radon = RD200.read_radon()
        
    print(radon)
    
    counts = bus.read_i2c_block_data(DIYgm, 0, 4)
    
    print(f"Counts Per Minute: {chr(counts[0])}{chr(counts[1])}{chr(counts[2])}{chr(counts[3])}")


    if (is_raining and datetime.datetime.now() - last_rain_time >= datetime.timedelta(seconds=600)):
        is_raining = False
    numInterrupts = 0.0
    
    print()
    time.sleep(1/POLL_RATE)
