"""Driver for database, holds interactions between collection and server."""


from datetime import datetime
import pandas as pd
import numpy as np
import os
import time
import requests
from databases.onlinedb import OnlineDB
from driver.globals import columns, header, Datatype


class Database:
    """Holds collected data on disk, memory, and online."""
    CACHE_SIZE = 1000

    def __init__(self,
                 dropbox_name, dropbox_key, dropbox_secret,
                 directory: str = "", filename: str = ""):
        current_time = time.time()

        if directory == "":
            directory = "./"
        self.directory = directory
        self.filename = filename
        self.data = pd.DataFrame(
                        np.full((len(columns), Database.CACHE_SIZE), np.nan),
                        index=columns)
        self.row_index = 0
        self.data[self.row_index] = [float("NaN") for i in range(len(columns))]
        self.data_time = current_time
        self.num_disk_files = 0
        self.start_disk_time = current_time
        self.online_database = OnlineDB(dropbox_name,
                                        dropbox_key,
                                        dropbox_secret)

        # init earliest time in disk.
        for name in os.listdir(self.directory):
            try:
                path = os.path.join(self.directory, name)
                if not os.path.isfile(path) or not path.endswith(".csv"):
                    continue  # not csv file

                file = open(path, 'r')
                line = file.readline()
                if (line != header):
                    continue  # not a data file

                # this is slow
                for line in file:
                    # gets time value
                    time_val = float(file.readline().split(',')[Datatype.TIME])
                    self.start_disk_time = min(time_val, self.start_disk_time)
                file.close()
            except OSError:
                print("ERROR: DataBase::__init__ couldnt init files on disk")
            except FileNotFoundError:
                print("ERROR: DataBase::__init__ path couldnt be found")
            except NotADirectoryError:
                print("ERROR: DataBase::__init__ path is not a directory")
            except PermissionError:
                print("ERROR: DataBase::__init__ permission must be granted")

    def change_file(self, new_fname, save_old):
        if (save_old):
            os.remove(self.filename)
        self.filename = new_fname
        try:
            with open(self.filename, 'w') as file:
                file.write(header)
        except OSError:
            print("couldnt change file")

    # currently unused
    def writeCSV(self):
        try:
            with open(self.filename, 'w') as file:
                file.write(header)
                output = ''
                for row in self.data:
                    for elt in row:
                        if (',' in elt):
                            elt = f'\"{elt}\"'
                        output += f'{elt},'
                    output = output[:-1]
                    output += '\n'

                file.write(output)
        except OSError:
            print("couldnt write CSV to file")

    def upload(self, fname) -> bool:
        try:
            self.online_database.upload(fname)  # dropbox

            # disk
            with open(self.filename, 'w') as file:
                condition = "not time.isnull()"
                queried = self.data.query(condition, engine="python").to_csv()
                file.write(queried)
            self.change_file(f"rws_lite_data{time.time()}.csv", False)

            # memory
            self.row_index = 0
            self.data.fillna()
            return True
        except requests.exceptions.ConnectionError as ex:
            self.change_file(f"rws_lite_data{time.time()}.csv", True)
            print(ex)
            print("Connection Error to Dropbox")
            return False

    # Returns seconds since epoch
    def convert_time(self, time):
        if isinstance(time, datetime):
            return (time - datetime(1970, 1, 1)).total_seconds()
        return time

    # Sets internal data point of type to datum
    # Returns True if successfully sets data
    def set(self, type: Datatype, datum) -> bool:
        if type == Datatype.TIME:
            datum = self.convert_time(datum)
            # can times be other datatypes?
            if not isinstance(datum, float):
                return False

        self.data.iat[self.row_index, int(type)] = datum
        return True

    # Pushes currently held data to stored data
    # Sets currently held data to NaN
    # TODO: write to disk
    def push(self):
        print(f'PUSHING at time {time.time()}')

        # dont need to push cache onto the disk
        if self.row_index < Database.CACHE_SIZE:
            self.row_index += 1
            return

        try:
            with open(self.filename, 'w') as file:
                file.write(self.data.to_csv())
            self.row_index = 0
            self.data.fillna()
        except OSError:
            print("could not push to disk")

    # Sets start to closest stamp greater than or equal to time_start
    # # and end to closest stamp lesser than or equal to time_end
    # Requires time to be in UTC
    def set_time(self, time_start, time_end):
        self.start = self.convert_time(time_start)
        self.end = self.convert_time(time_end)

    def from_disk(self, start, end,
                  types: list[Datatype] = []) -> pd.DataFrame:
        """
        returns Dataframe with data after start from disk
        requires to not have to get data from cloud
        """
        df = pd.DataFrame()
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            time_val = row.at[Datatype.TIME]
            if start <= time_val < end:
                df.loc[len(df)] = row

        for name in os.listdir(self.directory):
            with open(os.path.join(self.directory, name), 'r') as file:
                line = file.readline()
                if (line != header):  # not a data file
                    continue

                for line in file:
                    # gets time value
                    time_val = file.readline().split(',')[Datatype.TIME]
                    if start <= time_val < end:
                        df.loc[len(df)] = row

        df.sort_values(columns[Datatype.TIME])
        return df[types]

    def get(self, start, end=None,
            types_in: list[Datatype] = []) -> pd.DataFrame | None:
        """
        Returns table of data requested and empty table if failed
        Time is the first column, rest of columns are returned
            in order of parameter types
        """
        types = [t for t in types_in if t in columns]
        if columns[Datatype.TIME] not in types:
            return None
        elif len(types) == 0:
            return None

        time_now = time.time()
        start = self.convert_time(start)
        end = self.convert_time(end)
        if (start < time_now or start >= end):
            return None

        df = pd.DataFrame(types)
        if (start < self.start_disk_time):
            print("getting from cloud")
            # TODO call online db method
        if (start < self.data_time):
            print("getting from disk")
            df = pd.concat([df, self.from_disk(start, end, types)])

        q_start = f'{columns[Datatype.TIME]} >= {str(start)}'
        q_end = f'{columns[Datatype.TIME]} < {str(end)}'
        return pd.concat([df, self.data[types].query(q_start).query(q_end)])
