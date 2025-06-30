import datetime
import time
import pigpio
import station.tphg as tphg
import smbus
import asyncio
import requests
import os
import databases.onlinedb as onlinedb
import station.collector as collector
from server.main import start_server

# lmaooooo
import matplotlib.pyplot as plt

url = "https://192.168.4.1:8080/data"





SEND_RATE = 1 #days
POLL_RATE = .2 #Hz

# These need to be calibrated with saturated and desicated soil
SOIL_MOISTURE_MIN = 348
SOIL_MOISTURE_MAX = 3658



num_interrupts = 0
is_raining = False
rain_interrupts = 0

def cb_func(gpio, level, tick):
    global rain_interrupts
    rain_interrupts += 1
    last_rain_time = datetime.datetime.now()
    time.sleep(0.001)

def wind_speed_func(gpio, level, tick):
    global num_interrupts
    num_interrupts += 1
    time.sleep(0.001)


'''
Takes counts from the soil moisture sensor as input and remaps
the values to calibrated points
'''
def soilMoisture(counts):
    return (counts - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)




PIN_RAIN = 20
PIN_WIND_SPEED = 21


pi = pigpio.pi()
pi.set_mode(PIN_RAIN, pigpio.INPUT)
pi.set_pull_up_down(PIN_RAIN, pigpio.PUD_DOWN)

pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)
pi.set_pull_up_down(PIN_WIND_SPEED, pigpio.PUD_OFF)

pi.set_mode(4, pigpio.INPUT)
pi.set_pull_up_down(4, pigpio.PUD_UP)

cb = pi.callback(PIN_RAIN, pigpio.RISING_EDGE, cb_func)
wind_speed = pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, wind_speed_func)


# TODO: move these to collector
try: 
    inside = tphg.initialize(True)
except Exception as e:
    print(e)

try:
    outside = tphg.initialize(False)
except Exception as e:
    print(e)

bus = smbus.SMBus(1)

###################################################################
# Globals
###################################################################
data_collection = None
fname = ""

# For the dropbox API
APP_KEY = ""
APP_SECRET = ""
STATION_NAME = "RyanRWSlite"
online_database = onlinedb.OnlineDB(APP_KEY, APP_SECRET, STATION_NAME)


###################################################################
# GETTING/CREATING CSV FILE
###################################################################
def create_file():
    global fname
    for x in os.listdir():
        if x.endswith(".csv"):
            fname = x
            break

    if not fname:
        header = "time,in_temp,in_press,in_hum,in_gas,out_temp,out_press,out_hum,out_gas,winddir,windspeed,is_raining,soil_temp,soil_mois,uv,radon,CPM\n"
        fname = f"rws_lite_data{time.time()}.csv"
        with open(fname, "w+") as file:
            file.write(header)




###################################################################
# COLLECTING DATA
###################################################################

async def collect_data():
    global online_database
    global data_collection
    global fname

    last_send = time.time()
    while (True):
        print(f"time since: {time.time()-last_send}")

        data_collection.collect()
        
        if time.time() - last_send >= SEND_RATE * 60*60*24:
            try:
                online_database.upload(fname)
                data_collection.change_file(f"rws_lite_data{time.time()}.csv", False)
                last_send = time.time()
            except requests.exceptions.ConnectionError as ex:
                data_collection.change_file(f"rws_lite_data{time.time()}.csv", True)
                print(ex)
                print("Connection Error to Dropbox")
                time.sleep(1)
        plt.pause(1/POLL_RATE)






def main():
    global data_collection
    create_file()
    data_collection = collector.Collector(fname, url)
    asyncio.run(collect_data())
    start_server()



if __name__ == "__main__":
    main()