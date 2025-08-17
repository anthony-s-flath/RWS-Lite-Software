###################################################################
# Driver for database, holds interactions between collection and server
###################################################################

from enum import Enum
from datetime import datetime
import pandas as  pd
import os

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

    files_in_mem = 0
    files_on_disk = 0
    files_in_cloud = 0

    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename
        self.current_data = pd.Series(index=Database.index)
        self.data = pd.DataFrame(index=Database.index)
    
    def change_file(self, new_fname, save_old):
        if (save_old):
            os.remove(self.filename)
        self.filename = new_fname
                

    def writeCSV(self):
        with open(self.filename, 'w') as file:
            file.write('time,in_temp,in_press,in_hum,in_gas,out_temp,out_press,out_hum,out_gas,winddir,windspeed,is_raining,soil_temp,soil_mois,uv,radon,CPM\n')
            output = ''
            for row in self.current_data:
                for elt in row:
                    if (',' in elt):
                        elt = f'\"{elt}\"'
                    output += f'{elt},'
                output = output[:-1]
                output += '\n'

            file.write(output)

    # Returns seconds since epoch
    def convert_time(self, time):
        if isinstance(time, datetime):
            return (time - datetime(1970,1,1)).total_seconds()
        return time
    
    # Sets internal data point of type to datum
    # Returns True if successfully sets data
    def set(self, type: Datatype, datum) -> bool:
        if type == Datatype.TIME:
            datum = self.convert_time(datum)
            # can times be other datatypes?
            if not isinstance(datum, float): return False
        self.current_data[type] = datum
        return True


    # TODO: this is slow and doesnt work?
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

    # Returns table of data requested
    # Time is the first column, rest of columns are returned in order of parameter types
    def get(self, time_start, time_end=None, types: list[Datatype] = []) -> pd.DataFrame:
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

        # return 2d Arr with time v type (if type)



