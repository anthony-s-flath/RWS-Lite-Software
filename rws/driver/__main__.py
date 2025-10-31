"""
Main driver for collecting data from weather station and serving local site.
"""
import time
import asyncio
import click
from rws.server import start_server
from rws.databases import Database
from rws.station import Collector
from rws.driver import POLL_RATE, SEND_RATE, COLUMNS
import rws.driver as driver


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
        if driver.VERBOSE:
            database.print_data()

        # save in memory
        database.push()
        print()

        # upload if its been a day
        # # As of right now, local files only stay if they're not uploaded
        if time.time() - last_send >= SEND_RATE * 60*60*24:
            if (database.upload(fname)):
                last_send = time.time()

        time.sleep(1/POLL_RATE)


###################################################################
# CONSOLE
###################################################################

def read_options(filename):
    print(f"Reading option file {filename}")
    with open(filename, "r") as file:
        for line in file:
            try:
                op = line.strip()
                if op.startswith('#'):
                    continue
                if op in COLUMNS:
                    driver.OPTIONS[COLUMNS.index(op)] = True
            except:
                print("ERROR: Option parsing failed, please check docs for formatting.")
                return False
    return True



def option_menu():
    print("This is the option menu.")
    print("TODO THE OPTION MENU")


@click.command()
@click.option('--name', '-n',   "dropbox_name", help="dropbox_name")
@click.option('--key', '-k',    "dropbox_key", help="dropbox_key")
@click.option('--secret', '-s', "dropbox_secret", help="dropbox_secret")
@click.option('--output', '-o', type=click.Path(), default="data", help='Output directory.')
@click.option('--file', '-f', type=click.Path(), default=default_file(), help='Output file.')
@click.option('--debug', '-d', flag_value=True, help='Set data, besides time, to arbitrary integers.')
@click.option('--verbose', '-v', flag_value=True, help='Output data.')
@click.option('--options', '-p', is_flag=False, flag_value=False, help='Enter option mode or enter option file. See docs for details.')
def main(dropbox_name=None, dropbox_key=None, dropbox_secret=None,
         output="output", file=default_file(),
         debug=False, verbose=False, options=False):
    """Serves RWS weather station data through a local site."""
    global database
    global data_collection
    global fname

    driver.DEBUG = debug
    driver.VERBOSE = verbose
    if dropbox_key is not None:
        driver.ONLINE = True

    # parse options
    if isinstance(options, bool):
        if not options:
            for t in driver.OPTIONS:
                t = True
        else:
            option_menu()
    elif options is not None and not read_options(options):
        return

    fname = file
    database = Database(dropbox_name,
                        dropbox_key,
                        dropbox_secret,
                        output,
                        file)
    data_collection = Collector(file)
    asyncio.run(collect_data())
    #start_server()


if __name__ == "__main__":
    main()
