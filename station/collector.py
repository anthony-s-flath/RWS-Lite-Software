###################################################################
# HELPER CLASS TO STORE DATA IN AN OBJECT
###################################################################


import time
import requests
from station import tphg, out_board, soiltemp, radoneye, out_pi
from station.out_pi import wind_interrupts, rain_interrupts
from driver.config import DEBUG, URL
from driver.globals import columns, Datatype
from databases.db import Database


class Collector:
    def __init__(self, fname, diygm_url):
        self.fname = fname

        if DEBUG:
            return
        self.oboard = out_board.OutBoard()
        self.is_raining = False
        self.bmes = tphg.BMEs()
        out_pi.init()
    
    def __str__(self):
        return self.fname
    
    
    async def collect(self, database: Database):
        global rain_interrupts
        global wind_interrupts
        print(f"wind interrupts {wind_interrupts}")
        database.set(Datatype.TIME, time.time())
        if DEBUG:
            global columns
            for i in range(1, len(columns)):
                database.set(i, i)
            return


        
        # inside temp, pressure, humidity, gas_resistance
        temp, press, humid, gas_resistance = self.collect_tphg(True)
        database.set(Datatype.IN_TEMP, temp)
        database.set(Datatype.IN_PRESS, press)
        database.set(Datatype.IN_HUM, humid)
        database.set(Datatype.IN_GAS, gas_resistance)
            

            
        # inside temp, pressure, humidity, gas_resistance
        temp, press, humid, gas_resistance = self.collect_tphg(False)
        database.set(Datatype.OUT_TEMP, temp)
        database.set(Datatype.OUT_PRESS, press)
        database.set(Datatype.OUT_HUM, humid)
        database.set(Datatype.OUT_GAS, gas_resistance)
            
            
        
        # wind dir/speed + rain
        # wind speed: calculates speed from num of interrupts
        # wind dir: static calc
        # raining: calculates from num of rain interrups
        windspeed = (wind_interrupts/3.6) / (time.time()-meas_time_start)
        meas_time_start = time.time()
        wind_interrupts = 0.0
        try:
            winddirection = self.get_wind_direction(self.oboard.read_wind_direction())
            database.set(Datatype.WIND_DIR, winddirection)
            database.set(Datatype.WIND_SPEED, windspeed)
            database.set(Datatype.IS_RAINING, rain_interrupts * 0.018)
        except Exception as e:
            to_write += ',,,'
            print(e)
            print("Could not read wind direction (check ADC)")
        rain_interrupts = 0

        # soil temp
        soiltemp_result = soiltemp.read_soil_temp()
        database.set(Datatype.SOIL_TEMP, soiltemp_result)
            
        # soil moisture
        soil_moist = float("Nan")
        try:
            soil_moist = self.oboard.read_soil_moisture()
            print(f"soil moisture: {soil_moist}")
        except Exception as e:
            print("Could not read soil moisture (check ADC)")
        database.set(Datatype.SOIL_MOIS, soil_moist)   
        


        # uv
        uv = float("Nan")
        try:
            uv = self.oboard.read_UV_light()
            print(f"UV: {uv}")
        except Exception as e:
            print("Could not read UV (check ADC)")
        database.set(Datatype.UV, uv)


        # TODO: this needs complete reworking
        # probs need to work with the physical radoneye
        radon = float("NaN")
        try:
            radon = await radoneye.read_radon()
        except Exception as e:
            print("could not read radon")
        database.set(Datatype.RADON, radon)
            
        
        try:
            diygm = requests.get(URL, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            to_write += str(diygm_data['cpm_slow'][-1]) + '\n'
        except Exception as e:
            to_write += ','
            print("Could not read diygm")


        
        print()
        


    # HELPER FUNCTIONS FOR THE CLASS

    async def collect_tphg(self, is_inside: bool):
        temp, press, humid, gas_resistance = 0
        print_tag = ""
        try:
            if (is_inside):
                temp, press, humid, gas_resistance = self.bmes.in_data()
                print_tag = "INSIDE"
            else:
                temp, press, humid, gas_resistance = self.bmes.out_data()
                print_tag = "OUTSIDE"
            print(f"{print_tag} temperature: {temp} pressure: {press} \
                    humidity: {humid} gas_resistance {gas_resistance}")
            
            return temp, press, humid, gas_resistance
        except Exception as e:
            print("Could not read internal atmosphere")
            self.bmes.reinit(is_inside)
            return float('NaN'), float('NaN'), float('NaN'), float('NaN')
        
    
    def get_wind_direction(self, counts):
        print(counts)
        voltage = counts /1000
        # 16 possible values 
        '''
        vals = ((0, 49500),
                (22.5, 9855),
                (45, 12300),
                (67.5, 1336.5),
                (90, 1500),
                (112.5, 1032),
                (135, 3300),
                (157.5, 2115),
                (180, 5850),
                (202.5, 4710),
                (225, 24000),
                (247.5, 21180),
                (270, 180000),
                (292.5, 63180),
                (315, 97350),
                (337.5, 32820))
        '''
        vals = ((0, 68000),
                (45, 16700),
                (90, 2600),
                (135, 4400),
                (180, 8300),
                (225, 32000),
                (270, 255000),
                (315, 120000))
        # solve for resistance using voltage divider
        # 15000 is another resistor
        r = 15000*3.3 / voltage - 15000
        
        # get the index of the closest distance
        distances = [ abs(r - vals[x][1]) for x in range(0, len(vals)) ]
        closest_index = min(range(len(distances)), key=distances.__getitem__)

        return vals[closest_index][0]
        #return r
    
    