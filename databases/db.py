###################################################################
# Driver for database, holds interactions between collection and server
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

    def __init__(self):
        self.current_data = pd.Series(index=Database.index)
        self.data = pd.DataFrame(index=Database.index)


    # Returns seconds since epoch
    def convert_time(self, time):
        if isinstance(time, datetime):
            return (time - datetime(1970,1,1)).total_seconds()
        return time
    


    # Sets internal data point of type to datum
    # Returns True if successfully sets data
    def set(self, datum, type: Datatype) -> bool:
        if type == Datatype.TIME:
            datum = self.convert_time(datum)
            # can times be other datatypes?
            if not isinstance(datum, float): return False
        self.current_data[type] = datum
        return True


    # TODO: this is slow and doesnt work
    # Pushes currently held data to stored data
    # Sets currently held data to NaN
    def push(self):
        self.data = pd.concat([self.data, self.current_data.to_frame().T])

        # manipulate in place instead !! not this
        self.current_data = [float("nan") for x in self.current_data]  
    

    # Sets start to closest stamp greater than or equal to time_start
    # # and end to closest stamp lesser than or equal to time_end
    # Requires time to be in UTC
    def set_time(self, time_start, time_end):
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

    #
    def get(self, time_start, time_end=None, type: Datatype=None):
        
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

        # return 2d Arr with time v type (if type)



# addTypes(...)
# # sets internal types to parameters

# resetSettings()

# set_time(time_start, time_end)

# get_type()


