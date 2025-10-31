"""HELPER CLASS TO STORE DATA IN AN OBJECT"""

import time
import requests
from rws.driver import COLUMNS, Datatype, URL
import rws.driver as driver
from rws.databases import Database
from rws.station import out_board, out_pi, soiltemp, radoneye, tphg


class Collector:
    def __init__(self, fname):
        self.fname = fname
        print(driver.DEBUG)

        if driver.DEBUG:
            return
        
        if (driver.OPTIONS[Datatype.WIND_DIR] 
            or driver.OPTIONS[Datatype.SOIL_MOIS]
            or driver.OPTIONS[Datatype.UV]):
            self.oboard = out_board.OutBoard()
        self.is_raining = False
        self.bmes = tphg.BMEs()
        self.meas_time_start = time.time()
        out_pi.init()

    def __str__(self):
        return self.fname
        
    async def collect(self, db: Database):
        db.set(Datatype.TIME, time.time())
        if driver.DEBUG:
            global COLUMNS
            for i in range(1, len(COLUMNS)):
                db.set(i, i)
            return


        # inside temp, pressure, humidity, gas_resistance
        if (driver.OPTIONS[Datatype.IN_TEMP]
                or driver.OPTIONS[Datatype.IN_PRESS]
                or driver.OPTIONS[Datatype.IN_HUM]
                or driver.OPTIONS[Datatype.IN_GAS]):
            temp, press, humid, gas_resistance = await self.collect_tphg(False)
            if driver.OPTIONS[Datatype.IN_TEMP]:
                db.set(Datatype.IN_TEMP, temp)
                print(f"IN_TEMP: {db.get_one(Datatype.IN_TEMP)}")
            if driver.OPTIONS[Datatype.IN_PRESS]:
                db.set(Datatype.IN_PRESS, press)
                print(f"IN_PRESS: {db.get_one(Datatype.IN_PRESS)}")
            if driver.OPTIONS[Datatype.IN_HUM]:
                db.set(Datatype.IN_HUM, humid)
                print(f"IN_HUM: {db.get_one(Datatype.IN_HUM)}")
            if driver.OPTIONS[Datatype.IN_GAS]:
                db.set(Datatype.IN_GAS, gas_resistance)
                print(f"IN_GAS: {db.get_one(Datatype.IN_GAS)}")

        # outside temp, pressure, humidity, gas_resistance
        if (driver.OPTIONS[Datatype.OUT_TEMP]
                or driver.OPTIONS[Datatype.OUT_PRESS]
                or driver.OPTIONS[Datatype.OUT_HUM]
                or driver.OPTIONS[Datatype.OUT_GAS]):
            temp, press, humid, gas_resistance = await self.collect_tphg(False)
            if driver.OPTIONS[Datatype.OUT_TEMP]:
                db.set(Datatype.OUT_TEMP, temp)
                print(f"OUT_TEMP: {db.get_one(Datatype.OUT_TEMP)}")
            if driver.OPTIONS[Datatype.OUT_PRESS]:
                db.set(Datatype.OUT_PRESS, press)
                print(f"OUT_PRESS: {db.get_one(Datatype.OUT_PRESS)}")
            if driver.OPTIONS[Datatype.OUT_HUM]:
                db.set(Datatype.OUT_HUM, humid)
                print(f"OUT_HUM: {db.get_one(Datatype.OUT_HUM)}")
            if driver.OPTIONS[Datatype.OUT_GAS]:
                db.set(Datatype.OUT_GAS, gas_resistance)
                print(f"OUT_GAS: {db.get_one(Datatype.OUT_GAS)}")
                db.get_one

        if driver.OPTIONS[Datatype.WIND_SPEED]:
            db.set(Datatype.WIND_SPEED, self._get_wind_speed())
            print(f"WIND_SPEED: {db.get_one(Datatype.WIND_SPEED)}")

        if driver.OPTIONS[Datatype.WIND_DIR]:
            db.set(Datatype.WIND_DIR, self._get_wind_direction())
            print(f"WIND_DIR: {db.get_one(Datatype.WIND_DIR)}")
            
        if driver.OPTIONS[Datatype.IS_RAINING]:
            db.set(Datatype.IS_RAINING, self._get_is_raining())
            print(f"IS_RAINING: {db.get_one(Datatype.IS_RAINING)}")
        
        if driver.OPTIONS[Datatype.SOIL_TEMP]:
            db.set(Datatype.SOIL_TEMP, soiltemp.read_soil_temp())
            print(f"SOIL_TEMP: {db.get_one(Datatype.SOIL_TEMP)}")

        if driver.OPTIONS[Datatype.SOIL_MOIS]:
            db.set(Datatype.SOIL_MOIS, self.oboard.read_soil_moisture())
            print(f"SOIL_MOIS: {db.get_one(Datatype.SOIL_MOIS)}")

        if driver.OPTIONS[Datatype.UV]:
            db.set(Datatype.UV, self.oboard.read_UV_light())
            print(f"UV: {db.get_one(Datatype.UV)}")

        # TODO: this needs complete reworking
        if driver.OPTIONS[Datatype.RADON]:
            db.set(Datatype.RADON, radoneye.read_radon())
            print(f"RADON: {db.get_one(Datatype.RADON)}")

        if driver.OPTIONS[Datatype.CPM]:
            db.set(Datatype.CPM, self._get_diygm())
            print(f"CPM: {db.get_one(Datatype.CPM)}")
        

    async def collect_tphg(self, is_inside: bool) -> tuple[float, float, float, float] | tuple[None, None, None, None]:
        temp, press, humid, gas_resistance = 0, 0, 0, 0
        try:
            if (is_inside):
                temp, press, humid, gas_resistance = self.bmes.in_data()
            else:
                temp, press, humid, gas_resistance = self.bmes.out_data()

            return temp, press, humid, gas_resistance
        except Exception as e:
            print("Could not read internal atmosphere")
            self.bmes.reinit(is_inside)
            return None, None, None, None

    def _get_is_raining(self) -> float:
        is_raining = out_pi.rain_interrupts * 0.018
        out_pi.rain_interrupts = 0
        return is_raining
    
    def _get_wind_speed(self) -> float:
        """
        Returns wind speed in m/s using SparkFun SEN-15901 anemometer calibration:
        1 pulse/second = 1.492 mph = 2.4 km/h ≈ 0.667 m/s.
        """
        pulses = out_pi.wind_interrupts
        now = time.time()
        dt = now - self.meas_time_start
        self.meas_time_start = now
        out_pi.wind_interrupts = 0

        if dt <= 0 or pulses <= 0:
            return 0.0

        hz = pulses / dt
        # Choose your preferred unit:
        speed_ms = 0.66698368 * hz     # exact 0.44704*1.492
        # speed_kmh = 2.4 * hz
        # speed_mph = 1.492 * hz
        return speed_ms


    def _get_wind_direction(self) -> float | None:
        """
        Convert ADS1115 A0 voltage to a vane resistance (10k:Rvane divider @ 3.3V),
        then snap to the closest of the 16 SparkFun vane resistances and return
        its direction in degrees.
        """
        V_in = 3.3
        R_fixed = 10000.0  # 10k to 3.3V per SparkFun doc

        Vout = self.oboard.read_wind_direction()
        if Vout is None or Vout <= 0.01 or Vout >= V_in - 0.01:
            return None  # out of range or not connected

        # Correct algebra for divider where Vout is across Rvane (to GND):
        #   Vout = V_in * Rvane / (R_fixed + Rvane)  =>
        #   Rvane = R_fixed * Vout / (V_in - Vout)
        Rvane = R_fixed * Vout / (V_in - Vout)

        # SparkFun 16-position vane resistances (Ohms) and angles (deg)
        # From DS-15901 table (values in kΩ converted to Ω)
        k = lambda x: x * 1000.0
        table = (
            (0.0,    k(33.0)),   (22.5,  k(6.57)),  (45.0,  k(8.2)),   (67.5,  k(0.981)),
            (90.0,   k(1.0)),    (112.5, k(0.688)), (135.0, k(2.2)),   (157.5, k(1.41)),
            (180.0,  k(3.9)),    (202.5, k(3.14)),  (225.0, k(16.0)),  (247.5, k(14.12)),
            (270.0,  k(120.0)),  (292.5, k(42.12)), (315.0, k(64.9)),  (337.5, k(21.88)),
        )

        # Find the closest resistance
        closest = min(table, key=lambda tup: abs(Rvane - tup[1]))
        return closest[0]


    def _get_diygm(self):
        try:
            diygm = requests.get(URL, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            return diygm_data['cpm_slow'][-1]
        except Exception as e:
            print("Could not read diygm")
            return None
