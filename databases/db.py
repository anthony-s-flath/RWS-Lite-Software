###################################################################
# Driver for database, holds interactions between collection and server
###################################################################

from enum import Enum
from datetime import datetime
import pandas as  pd
import os
import time
import requests
from databases import OnlineDB
from driver import APP_KEY, APP_SECRET, STATION_NAME

columns = ['time', 
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
header = ','.join(columns) + '\n'

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
    def __init__(self, directory, filename):
        current_time = time.time()

        self.directory = directory
        self.filename = filename
        self.current_data = pd.Series(index=columns)
        self.data = pd.DataFrame(index=columns)
        self.data_time = current_time
        self.num_disk_files = 0
        self.start_disk_time = current_time
        self.online_database = OnlineDB(APP_KEY, APP_SECRET, STATION_NAME)
        
        # init earliest time in disk
        for name in os.listdir(self.directory):
            with open(os.path.join(self.directory, name), 'r') as file:
                line = file.readline()
                if (line != header): # not a data file
                    continue

                for line in file:
                    time_val = file.readline().split(',')[Datatype.TIME] # gets time value
                    self.start_disk_time = min(time_val, self.start_disk_time)

    
    def change_file(self, new_fname, save_old):
        if (save_old):
            os.remove(self.filename)
        self.filename = new_fname
                

    def writeCSV(self):
        with open(self.filename, 'w') as file:
            file.write(header)
            output = ''
            for row in self.current_data:
                for elt in row:
                    if (',' in elt):
                        elt = f'\"{elt}\"'
                    output += f'{elt},'
                output = output[:-1]
                output += '\n'

            file.write(output)

    def upload(self, fname) -> bool:
        try:
            self.online_database.upload(fname)
            self.change_file(f"rws_lite_data{time.time()}.csv", False)
            return True
        except requests.exceptions.ConnectionError as ex:
            self.change_file(f"rws_lite_data{time.time()}.csv", True)
            print(ex)
            print("Connection Error to Dropbox")
            return False

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



    # Pushes currently held data to stored data
    # Sets currently held data to NaN
    def push(self):
        self.data += self.current_data.to_frame().T

        # manipulate in place instead !! not this
        self.current_data = [float("nan") for x in self.current_data]  
    

    # Sets start to closest stamp greater than or equal to time_start
    # # and end to closest stamp lesser than or equal to time_end
    # Requires time to be in UTC
    def set_time(self, time_start, time_end):
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)


    # returns Dataframe with data after start from disk
    # requires to not have to get data from cloud
    def from_disk(self, start, end, types: list[Datatype] = []) -> pd.DataFrame:
        df = pd.DataFrame()
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            time_val = row.at[Datatype.TIME]
            if start <= time_val < end:
                df += row
        
        for name in os.listdir(self.directory):
            with open(os.path.join(self.directory, name), 'r') as file:
                line = file.readline()
                if (line != header): # not a data file
                    continue

                for line in file:
                    time_val = file.readline().split(',')[Datatype.TIME] # gets time value
                    if start <= time_val < end:
                        df += row
        
        df.sort_values("time")
        return df
                    

                

    

    # Returns table of data requested
    # Returns empty table if failed
    # Time is the first column, rest of columns are returned in order of parameter types
    def get(self, start, end=None, types: list[Datatype] = []) -> pd.DataFrame:
        if any(True for t in types if t not in columns): # i think this works
            return pd.DataFrame()

        time_now = time.time()
        start = self.convert_time(start)
        end = self.convert_time(end)
        if (start < time_now or start >= end):
            return pd.DataFrame(index=columns)[types]

        df = pd.DataFrame(index=columns)
        if (start < self.start_disk_time):
            print("getting from cloud")
            #TODO call online db method
        if (start < self.data_time):
            print("getting from disk")
            df += self.from_disk(start, end, types)
        
        return df + self.data.query(f'time >= {str(str)}')



