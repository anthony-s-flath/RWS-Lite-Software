###################################################################
# Maintains local file data
###################################################################

import pandas as  pd
from db import Datatype


# earliest local time data
# latest local time data
# sort by day


class LocalDB:
    def __init__(self, directory):
        self.directory = directory
    
    # writes daily file
    def write(self):
        return False
    
    # Returns all local data within given time
    def get(self, time_start, time_end) -> pd.DataFrame:
        return False
