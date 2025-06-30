###################################################################
# Stores data, holds interactions between collection and server
###################################################################

from enum import Enum
from datetime import datetime
import pandas as  pd
import math

class Datatype(Enum):
    TIME = 0
    IN_TEMP = 1
    IN_PRESS = 2
    IN_HUM = 3
    IN_GAS  = 4
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



class Database:
    index = [
            Datatype.TIME,
            Datatype.IN_TEMP,
            Datatype.IN_PRESS,
            Datatype.IN_HUM,
            Datatype.IN_GAS,
            Datatype.OUT_TEMP,
            Datatype.OUT_PRESS,
            Datatype.OUT_HUM,
            Datatype.OUT_GAS,
            Datatype.WIND_DIR,
            Datatype.WIND_SPEED,
            Datatype.IS_RAINING,
            Datatype.SOIL_TEMP,
            Datatype.SOIL_MOIS,
            Datatype.UV,
            Datatype.RADON,
            Datatype.CPM
        ]

    def __init__(self):
        # save the first time stamp in local memory
        self.local_bound = 0
        # save the first time stamp in Dropbox
        self.online_bound = 0
        # this objects time stamps
        self.this_start = None
        self.this_end = None

        self.current_data = pd.Series(index=Database.index)
        self.data = pd.DataFrame(index=Database.index)

    # TODO: test this
    # returns seconds since epoch
    def convert_time(self, time):
        if isinstance(time, datetime):
            return (time - datetime(1970,1,1)).total_seconds()
        return time
    


    # returns true if successfully sets internal data to datum
    def set(self, datum, type: Datatype) -> bool:
        if type == Datatype.TIME:
            datum = self.convert_time(datum)
            # can times be other datatypes?
            if not isinstance(datum, float): return False
        self.current_data[type] = datum
        return True


    # TODO: this is slow and doesnt work
    def push(self):
        self.data = pd.concat([self.data, self.current_data.to_frame().T])

        # manipulate in place instead !! not this
        self.current_data = [float("nan") for x in self.current_data]  
    

    # Requires time to be in UTC
    # Sets start to closest stamp greater than or equal to time_start
    # # and end to closest stamp lesser than or equal to time_end
    def set_time(self, time_start, time_end):
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

    def get(self, time_start=None, time_end=None, type: Datatype=None):
        if (time_end is None 
            and time_end is None 
            and self.start is None 
            and self.end is None):
            return None
        
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

        # return 2d Arr with time v type (if type)



# addTypes(...)
# # sets internal types to parameters

# resetSettings()

# set_time(time_start, time_end)

# get_type()


