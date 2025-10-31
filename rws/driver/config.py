"""Project wide configuration variables"""
from rws.driver.globals import Datatype

###################################################################
# USER OPTIONS
###################################################################

DEBUG = True  # don't set to False
VERBOSE = False
ONLINE = False  # syncing with Dropbox
SEND_RATE = 1  # days
POLL_RATE = .2  # Hz
CALLBACK_SLEEP = 0.001  # seconds
DATA_DIRECTORY = ""

# radoneye i think
URL = "https://192.168.4.1:8080/data"

OPTIONS = {
    Datatype.TIME: False,
    Datatype.IN_TEMP: False,
    Datatype.IN_PRESS: False,
    Datatype.IN_HUM: False,
    Datatype.IN_GAS: False,
    Datatype.OUT_TEMP: False,
    Datatype.OUT_PRESS: False,
    Datatype.OUT_HUM: False,
    Datatype.OUT_GAS: False,
    Datatype.WIND_DIR: False,
    Datatype.WIND_SPEED: False,
    Datatype.IS_RAINING: False,
    Datatype.SOIL_TEMP: False,
    Datatype.SOIL_MOIS: False,
    Datatype.UV: False,
    Datatype.RADON: False,
    Datatype.CPM: False,
}
