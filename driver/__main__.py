"""
Main driver for collecting data from weather station and serving local site.
"""
import time
import asyncio
import click
import station.collector as collector
from server.main import start_server
from databases.db import Database
from driver import config
from driver.config import SEND_RATE, POLL_RATE, URL, data_directory, DEBUG


# driver globals
data_collection = None
fname = ""


###################################################################
# ummm idk probs something important
###################################################################


# These need to be calibrated with saturated and desicated soil
SOIL_MOISTURE_MIN = 348
SOIL_MOISTURE_MAX = 3658


def soilMoisture(counts):
    """
    Takes counts from the soil moisture sensor as input and remaps
    the values to calibrated points
    """
    return (counts - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)


# ummmm.....
# bus = smbus.SMBus(1)


###################################################################
# COLLECTING DATA
###################################################################

def default_file() -> str:
    return f"ws_lite_data{time.time()}.csv"

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
        # # As of right now, local files only stay if they're not uploaded
        if time.time() - last_send >= SEND_RATE * 60*60*24:
            if (database.upload(fname)):
                last_send = time.time()

        time.sleep(1/POLL_RATE)


@click.command()
@click.option('--name', '-n',   "dropbox_name", default="", help="dropbox_name")
@click.option('--key', '-k',    "dropbox_key", default="", help="dropbox_key")
@click.option('--secret', '-s', "dropbox_secret", default="", help="dropbox_secret")
@click.option('--output', '-o', type=click.Path(), default="data", help='Output directory.')
@click.option('--file', '-f', type=click.Path(), default=default_file(), help='Output file.')
@click.option('--debug', '-d', flag_value=True, help='Set mode to DEBUG.')
def main(dropbox_name="", dropbox_key="", dropbox_secret="",
         output="output", file=default_file(),
         debug=False):
    """Serves RWS weather station data through a local site."""
    global database
    global data_collection
    global fname
    global data_directory

    config.DEBUG = debug
    fname = file
    data_directory = output
    database = Database(dropbox_name,
                        dropbox_key,
                        dropbox_secret,
                        data_directory,
                        file)
    data_collection = collector.Collector(file)
    asyncio.run(collect_data())
    #start_server()


if __name__ == "__main__":
    main()
