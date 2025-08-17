import datetime
import time
import pigpio
import station.tphg as tphg
import smbus
import asyncio
import requests
import os
import station.collector as collector
from server.main import start_server
from databases import OnlineDB
from databases import Database

# lmaooooo
import matplotlib.pyplot as plt

url = "https://192.168.4.1:8080/data"



DEBUG = True

SEND_RATE = 1 # days
POLL_RATE = .2 # Hz
CALLBACK_SLEEP = 0.001 # seconds

# These need to be calibrated with saturated and desicated soil
SOIL_MOISTURE_MIN = 348
SOIL_MOISTURE_MAX = 3658



wind_interrupts = 0
is_raining = False
rain_interrupts = 0

def rain_callback(gpio, level, tick):
    global rain_interrupts
    rain_interrupts += 1
    last_rain_time = datetime.datetime.now()
    time.sleep(CALLBACK_SLEEP)

def wind_speed_callback(gpio, level, tick):
    global wind_interrupts
    wind_interrupts += 1
    time.sleep(CALLBACK_SLEEP)


'''
Takes counts from the soil moisture sensor as input and remaps
the values to calibrated points
'''
def soilMoisture(counts):
    return (counts - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)



bus = smbus.SMBus(1)

###################################################################
# Globals
###################################################################
data_collection = None
data_directory = ""
fname = ""

# For the dropbox API
APP_KEY = ""
APP_SECRET = ""
STATION_NAME = "RyanRWSlite"
online_database = OnlineDB(APP_KEY, APP_SECRET, STATION_NAME)



###################################################################
# COLLECTING DATA
###################################################################

async def collect_data():
    global online_database
    global data_collection

    last_send = time.time()
    while (True):
        print(f"time since: {time.time()-last_send}")

        # collect
        # return datatype and datum
        data_collection.collect(database)
        
        # save
        # as in have database save it on disk
        database.push()

        # upload if its been a day
        ## As of right now, local files only stay if they're not uploaded
        if time.time() - last_send >= SEND_RATE * 60*60*24:
            database.writeCSV()
            try:
                online_database.upload(fname)
                database.change_file(f"rws_lite_data{time.time()}.csv", False)
                last_send = time.time()
            except requests.exceptions.ConnectionError as ex:
                database.change_file(f"rws_lite_data{time.time()}.csv", True)
                print(ex)
                print("Connection Error to Dropbox")
                time.sleep(1)

        # strange way of pausing?
        plt.pause(1/POLL_RATE)






def main():
    global database
    global data_collection

    database = Database(data_directory, f"rws_lite_data{time.time()}.csv")
    data_collection = collector.Collector(fname, url)
    asyncio.run(collect_data())
    start_server()



if __name__ == "__main__":
    main()