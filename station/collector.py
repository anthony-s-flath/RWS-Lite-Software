"""HELPER CLASS TO STORE DATA IN AN OBJECT"""

import time
import requests
from driver import config
from driver.globals import columns, Datatype
from databases import Database
if not config.DEBUG:
    from station import out_board, out_pi, soiltemp, radoneye, tphg


class Collector:
    def __init__(self, fname):
        self.fname = fname

        if config.DEBUG:
            return
        self.oboard = out_board.OutBoard()
        self.is_raining = False
        self.bmes = tphg.BMEs()
        self.meas_time_start = time.time()
        out_pi.init()

    def __str__(self):
        return self.fname
        
    async def collect(self, database: Database):
        database.set(Datatype.TIME, time.time())
        if config.DEBUG:
            global columns
            for i in range(1, len(columns)):
                database.set(i, i)
            return

        print(f"wind interrupts {out_pi.wind_interrupts}")
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
        windspeed = (out_pi.wind_interrupts/3.6) / (time.time() - self.meas_time_start)
        self.meas_time_start = time.time()
        try:
            wind_dir = self.oboard.read_wind_direction()
            winddirection = self.get_wind_direction(wind_dir)
            database.set(Datatype.WIND_DIR, winddirection)
            database.set(Datatype.WIND_SPEED, windspeed)
            database.set(Datatype.IS_RAINING, out_pi.rain_interrupts * 0.018)
        except Exception as e:
            print(e)
            print("Could not read wind direction (check ADC)")
        out_pi.wind_interrupts = 0
        out_pi.rain_interrupts = 0

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
            diygm = requests.get(config.URL, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            database.set(Datatype.CPM, diygm_data['cpm_slow'][-1])
        except Exception as e:
            print("Could not read diygm")
        

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

    def get_wind_direction(self, voltage):
        # voltage = counts / 1000 # counts is the function parameter
        k = lambda x : x * 1000
        # cdn.sparkfun.com/assets/d/1/e/0/6/DS-15901-Weather_Meter.pdf
        vals = ((0, k(33)),
                (22.5, k(6.57)),
                (45, k(8.2)),
                (67.5, k(.981)),
                (90, k(1)),
                (112.5, k(.688)),
                (135, k(2.2)),
                (157.5, k(1.41)),
                (180, k(3.9)),
                (202.5, k(3.14)),
                (225, k(16)),
                (247.5, k(14.12)),
                (270, k(120)),
                (292.5, k(42.12)),
                (315, k(64.9)),
                (337.5, k(21.88)))
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
        vals = ((0, 68000),
                (45, 16700),
                (90, 2600),
                (135, 4400),
                (180, 8300),
                (225, 32000),
                (270, 255000),
                (315, 120000))
        
        '''
        # solve for resistance using voltage divider
        # 3.3V
        # 10k resistor
        r = 10000*3.3 / voltage - 10000

        # this is more than likely wrong
        # r = 3.3 * (voltage / (k(10) - voltage))

        # this line was found in duplicate wind_dir code
        # 10000 is another resistor
        # r = 10000*voltage / (3.3-voltage)

        # get the index of the closest distance
        distances = [abs(r - vals[x][1]) for x in range(0, len(vals))]
        closest_index = min(range(len(distances)), key=distances.__getitem__)
        return vals[closest_index][0]
        # return r
