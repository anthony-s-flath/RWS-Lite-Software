import time
import asyncio
import click
import station.collector as collector
from server.main import start_server
from databases.db import Database
from driver import config
from driver.config import SEND_RATE, POLL_RATE, URL, data_directory


# driver globals 
data_collection = None
fname = f"rws_lite_data{time.time()}.csv"



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
    global database

    last_send = time.time()
    while (True):
        print(f"time since: {time.time()-last_send}")

        # collect
        # return datatype and datum
        await data_collection.collect(database)
        
        # save in memory
        database.push()

        # upload if its been a day
        ## As of right now, local files only stay if they're not uploaded
        if time.time() - last_send >= SEND_RATE * 60*60*24:
            if (database.upload(fname)):
                last_send = time.time()

        # strange way of pausing?
        time.sleep(1/POLL_RATE)





@click.command()
@click.argument("dropbox_name", nargs=1)
@click.argument("dropbox_key", nargs=1)
@click.argument("dropbox_secret", nargs=1)
@click.option('--output', '-o', type=click.Path(), help='Output directory.')
def main(dropbox_name, dropbox_key, dropbox_secret, output):
    """Serves RWS weather station data through a local site."""
    global database
    global data_collection

    config.STATION_NAME = dropbox_name
    config.APP_KEY = dropbox_key
    config.APP_SECRET = dropbox_secret

    database = Database(data_directory, fname)
    data_collection = collector.Collector(fname, URL)
    asyncio.run(collect_data())
    #start_server()
