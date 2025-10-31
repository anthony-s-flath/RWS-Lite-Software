"""Software global constants."""

from enum import IntEnum


COLUMNS = ['time',
           "in_temp",
           "in_press",
           "in_hum",
           "in_gas",
           "out_temp",
           "out_press",
           "out_hum",
           "out_gas",
           "winddir",
           "windspeed",
           "is_raining",
           "soil_temp",
           "soil_mois",
           "uv",
           "radon",
           "CPM"
           ]
HEADER = ','.join(COLUMNS) + '\n'


class Datatype(IntEnum):
    TIME = 0
    IN_TEMP = 1
    IN_PRESS = 2
    IN_HUM = 3
    IN_GAS = 4
    OUT_TEMP = 5
    OUT_PRESS = 6
    OUT_HUM = 7
    OUT_GAS = 8
    WIND_DIR = 9
    WIND_SPEED = 10
    IS_RAINING = 11
    SOIL_TEMP = 12
    SOIL_MOIS = 13
    UV = 14
    RADON = 15
    CPM = 16
