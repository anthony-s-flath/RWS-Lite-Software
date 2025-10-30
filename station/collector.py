"""HELPER CLASS TO STORE DATA IN AN OBJECT"""

import time
import requests
from driver import config
from driver.config import options
from driver.globals import columns, Datatype
from databases import Database
from station import out_board, out_pi, soiltemp, radoneye, tphg


class Collector:
    def __init__(self, fname):
        self.fname = fname

        if config.DEBUG:
            return
        
        if (options[Datatype.WIND_DIR] 
            or options[Datatype.SOIL_MOIS]
            or options[Datatype.UV]):
            self.oboard = out_board.OutBoard()
        self.is_raining = False
        self.bmes = tphg.BMEs()
        self.meas_time_start = time.time()
        out_pi.init()

    def __str__(self):
        return self.fname
        
    async def collect(self, db: Database):
        db.set(Datatype.TIME, time.time())
        if config.DEBUG:
            global columns
            for i in range(1, len(columns)):
                db.set(i, i)
            return


        # inside temp, pressure, humidity, gas_resistance
        if (options[Datatype.IN_TEMP]
                or options[Datatype.IN_PRESS]
                or options[Datatype.IN_HUM]
                or options[Datatype.IN_GAS]):
            temp, press, humid, gas_resistance = await self.collect_tphg(False)
            if options[Datatype.IN_TEMP]:
                db.set(Datatype.IN_TEMP, temp)
                print(f"IN_TEMP: {db.get_one(Datatype.IN_TEMP)}")
            if options[Datatype.IN_PRESS]:
                db.set(Datatype.IN_PRESS, press)
                print(f"IN_PRESS: {db.get_one(Datatype.IN_PRESS)}")
            if options[Datatype.IN_HUM]:
                db.set(Datatype.IN_HUM, humid)
                print(f"IN_HUM: {db.get_one(Datatype.IN_HUM)}")
            if options[Datatype.IN_GAS]:
                db.set(Datatype.IN_GAS, gas_resistance)
                print(f"IN_GAS: {db.get_one(Datatype.IN_GAS)}")

        # outside temp, pressure, humidity, gas_resistance
        if (options[Datatype.OUT_TEMP]
                or options[Datatype.OUT_PRESS]
                or options[Datatype.OUT_HUM]
                or options[Datatype.OUT_GAS]):
            temp, press, humid, gas_resistance = await self.collect_tphg(False)
            if options[Datatype.OUT_TEMP]:
                db.set(Datatype.OUT_TEMP, temp)
                print(f"OUT_TEMP: {db.get_one(Datatype.OUT_TEMP)}")
            if options[Datatype.OUT_PRESS]:
                db.set(Datatype.OUT_PRESS, press)
                print(f"OUT_PRESS: {db.get_one(Datatype.OUT_PRESS)}")
            if options[Datatype.OUT_HUM]:
                db.set(Datatype.OUT_HUM, humid)
                print(f"OUT_HUM: {db.get_one(Datatype.OUT_HUM)}")
            if options[Datatype.OUT_GAS]:
                db.set(Datatype.OUT_GAS, gas_resistance)
                print(f"OUT_GAS: {db.get_one(Datatype.OUT_GAS)}")
                db.get_one

        if options[Datatype.WIND_SPEED]:
            db.set(Datatype.WIND_SPEED, self.get_wind_speed())
            print(f"WIND_SPEED: {db.get_one(Datatype.WIND_SPEED)}")

        if options[Datatype.WIND_DIR]:
            db.set(Datatype.WIND_DIR, self.get_wind_direction())
            print(f"WIND_DIR: {db.get_one(Datatype.WIND_DIR)}")
            
        if options[Datatype.IS_RAINING]:
            db.set(Datatype.IS_RAINING, self.get_is_raining())
            print(f"IS_RAINING: {db.get_one(Datatype.IS_RAINING)}")
        
        if options[Datatype.SOIL_TEMP]:
            db.set(Datatype.SOIL_TEMP, soiltemp.read_soil_temp())
            print(f"SOIL_TEMP: {db.get_one(Datatype.SOIL_TEMP)}")

        if options[Datatype.SOIL_MOIS]:
            db.set(Datatype.SOIL_MOIS, self.oboard.read_soil_moisture())
            print(f"SOIL_MOIS: {db.get_one(Datatype.SOIL_MOIS)}")

        if options[Datatype.UV]:
            db.set(Datatype.UV, self.oboard.read_UV_light())
            print(f"UV: {db.get_one(Datatype.UV)}")

        # TODO: this needs complete reworking
        if options[Datatype.RADON]:
            db.set(Datatype.RADON, radoneye.read_radon())
            print(f"RADON: {db.get_one(Datatype.RADON)}")

        if options[Datatype.CPM]:
            db.set(Datatype.CPM, self.get_diygm())
            print(f"CPM: {db.get_one(Datatype.CPM)}")
        

    async def collect_tphg(self, is_inside: bool) -> tuple[float, float, float, float]:
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

    def get_is_raining(self) -> float:
        is_raining = out_pi.rain_interrupts * 0.018
        out_pi.rain_interrupts = 0
        return is_raining
    
    def get_wind_speed(self) -> float:
        print(f"wind interrupts {out_pi.wind_interrupts}")
        windspeed = (out_pi.wind_interrupts/3.6) / (time.time() - self.meas_time_start)
        self.meas_time_start = time.time()
        out_pi.wind_interrupts = 0
        return windspeed

    def get_wind_direction(self) -> float:
        voltage = self.oboard.read_wind_direction()
        if voltage is None:
            return None
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

    def get_diygm(self):
        try:
            diygm = requests.get(config.URL, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            return diygm_data['cpm_slow'][-1]
        except Exception as e:
            print("Could not read diygm")
            return None
