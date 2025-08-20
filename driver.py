import time
import asyncio
import station.collector as collector
from server.main import start_server
from databases import Database

# lmaooooo
import matplotlib.pyplot as plt


###################################################################
# Globals
###################################################################

DEBUG = True

# consts
SEND_RATE = 1 # days
POLL_RATE = .2 # Hz
CALLBACK_SLEEP = 0.001 # seconds

# radoneye i think
URL = "https://192.168.4.1:8080/data"

# driver globals 
data_collection = None
data_directory = ""
fname = ""



###################################################################
# ummm idk probs something important
###################################################################

# These need to be calibrated with saturated and desicated soil
SOIL_MOISTURE_MIN = 348
SOIL_MOISTURE_MAX = 3658

'''
Takes counts from the soil moisture sensor as input and remaps
the values to calibrated points
'''
def soilMoisture(counts):
    return (counts - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)


# ummmm.....
#bus = smbus.SMBus(1)




###################################################################
# COLLECTING DATA
###################################################################

async def collect_data():
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
            if (database.upload(fname)):
                last_send = time.time()

        # strange way of pausing?
        plt.pause(1/POLL_RATE)






def main():
    global database
    global data_collection

    database = Database(data_directory, f"rws_lite_data{time.time()}.csv")
    data_collection = collector.Collector(fname, URL)
    asyncio.run(collect_data())
    start_server()



if __name__ == "__main__":
    main()