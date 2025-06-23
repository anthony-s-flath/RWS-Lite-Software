import time
import requests
import os

import TPHG_BME680
import out_board
import soiltemp
import radoneye



class Collector:
    def __init__(self, fname, diygm_url):
        self.fname = fname
        self.diygm_url = diygm_url
        self.ads = out_board.ADS1115()
        self.num_interrupts = 0
        self.is_raining = False
        self.rain_interrupts = 0
    
    def __str__(self):
        return self.fname
    
    async def collect(self):
        print(f"num interrupts {numInterrupts}")
        to_write = ''
        to_write += str(time.time()) + ','
        windspeed = (numInterrupts/3.6) / (time.time()-meas_time_start)
        meas_time_start = time.time()

        # inside temp, pressure, humidity, gas_resistance
        try:
            intemperature, inpressure, inhumidity, ingas_resistance = TPHG_BME680.read_data(inside)
            to_write += str(intemperature) + ',' + str(inpressure) + ',' + str(inhumidity) + ',' + str(ingas_resistance) + ','
            print(f"INSIDE temperature: {intemperature} pressure: {inpressure} humidity: {inhumidity} gas_resistance {ingas_resistance}")
        except Exception as e:
            to_write += ',,,,'
            try: 
                inside = TPHG_BME680.initialize(True)
            except Exception as e:
                print(e)
            print("Could not read internal atmosphere")
            
        # inside temp, pressure, humidity, gas_resistance
        try:
            outtemperature, outpressure, outhumidity, outgas_resistance = TPHG_BME680.read_data(outside)
            to_write += str(outtemperature) + ',' + str(outpressure) + ',' + str(outhumidity) + ',' + str(outgas_resistance) + ','
            print(f"OUTSIDE temperature: {outtemperature} pressure: {outpressure} humidity: {outhumidity} gas_resistance {outgas_resistance}")
        except Exception as e:
            to_write += ',,,,'
            try:
                outside = TPHG_BME680.initialize(False)
            except Exception as e:
                print(e)
            print("Could not read outside atmosphere")
            
        # wind dir/speed + rain
        try:
            winddirection = self.windDirection(self.ads.readADCSingleEnded(channel=0))
            to_write += str(winddirection)  + ',' + str(windspeed)+ ','
            to_write += str(rain_interrupts * 0.018) + ','
            rain_interrupts = 0
            print(f"wind direction: {winddirection} windspeed: {windspeed} is_raining: {rain_interrupts * 0.011}")
        except Exception as e:
            to_write += ',,,'
            print(e)
            print("Could not read wind direction (check ADC)")

        # soil temp   
        try:
            soiltemperature = soiltemp.read_soil_temp()
            to_write += str(soiltemperature) + ','
            print(f"soil temperature: {soiltemperature}")
        except Exception as e:
            print(e)
            to_write += ','
            print("Could not read soil temperature")
            
        # soil moisture
        try:
            soilmoisture = self.ads.readADCSingleEnded(channel=1)
            to_write += str(soilmoisture) + ','
            print(f"soil moisture: {soilmoisture}")
        except Exception as e:
            to_write += ','
            print("Could not read soil moisture (check ADC)")
            
        try:
            uv = self.ads.readADCSingleEnded(channel=2)
            to_write += str(uv) + ','
            print(f"UV: {uv}")
        except Exception as e:
            to_write += ','
            print("Could not read UV (check ADC)")

        try:
            radon = await radoneye.read_radon()
            print(radon)
            if radon:
                to_write += str(radon) + ','
        except Exception as e:
            to_write += ','
            print("could not read radon")
            
        try:
            diygm = requests.get(self.diygm_url, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            to_write += str(diygm_data['cpm_slow'][-1]) + '\n'
        except Exception as e:
            to_write += ','
            print("Could not read diygm")

        numInterrupts = 0.0
        
        print()
        with open(self.fname, 'a+') as file:
            file.write(to_write)
        
        
    
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
    
    def change_file(self, new_fname, save_old):
        if (save_old):
            os.remove(self.fname)
        self.fname = new_fname
        with open(self.fname, 'w+') as file:
                    file.write('time,in_temp,in_press,in_hum,in_gas,out_temp,out_press,out_hum,out_gas,winddir,windspeed,is_raining,soil_temp,soil_mois,uv,radon,CPM\n')
                