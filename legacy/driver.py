import datetime
import time
import pigpio
import ADS1115
import TPHG_BME680
import DS18B20
import RD200
import smbus
import asyncio
import requests
import dropbox
import pathlib
import os
import base64

from tqdm import tqdm

import matplotlib.pyplot as plt

url = 'https://192.168.4.1:8080/data'

ads = ADS1115.ADS1115()

SEND_RATE = 1 #days
POLL_RATE = .2 #Hz

# These need to be calibrated with saturated and desicated soil
SOIL_MOISTURE_MIN = 348
SOIL_MOISTURE_MAX = 3658

# For the dropbox API
APP_KEY = ''
APP_SECRET = ''
STATION_NAME = 'RyanRWSlite'

global numInterrupts
numInterrupts = 0

global is_raining
is_raining = False
last_rain_time = datetime.datetime.now()
global rain_interrupts
rain_interrupts = 0

def cb_func(gpio, level, tick):
    global rain_interrupts
    rain_interrupts += 1
    last_rain_time = datetime.datetime.now()
    time.sleep(0.001)

def wind_speed_func(gpio, level, tick):
    global numInterrupts
    numInterrupts += 1
    time.sleep(0.001)


'''
Takes counts from the soil moisture sensor as input and remaps
the values to calibrated points
'''
def soilMoisture(counts):
    return (counts - SOIL_MOISTURE_MIN)/(SOIL_MOISTURE_MAX-SOIL_MOISTURE_MIN)

def windDirection(counts):
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


PIN_RAIN = 20
PIN_WIND_SPEED = 21


pi = pigpio.pi()
pi.set_mode(PIN_RAIN, pigpio.INPUT)
pi.set_pull_up_down(PIN_RAIN, pigpio.PUD_DOWN)

pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)
pi.set_pull_up_down(PIN_WIND_SPEED, pigpio.PUD_OFF)

pi.set_mode(4, pigpio.INPUT)
pi.set_pull_up_down(4, pigpio.PUD_UP)

cb = pi.callback(PIN_RAIN, pigpio.RISING_EDGE, cb_func)
wind_speed = pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, wind_speed_func)

try: 
    inside = TPHG_BME680.initialize(True)
except Exception as e:
    print(e)

try:
    outside = TPHG_BME680.initialize(False)
except Exception as e:
    print(e)

bus = smbus.SMBus(1)
DIYgm = 0x13
t = 0
x = []
y = []

fname = ''
for x in os.listdir():
    if x.endswith('.csv'):
        fname = x
        break

if not fname:
    fname = f'rws_lite_data{time.time()}.csv'
    #fname = 'rws_lite_data1696184446.1469243.csv'

    with open(fname, 'w+') as file:
        file.write('time,in_temp,in_press,in_hum,in_gas,out_temp,out_press,out_hum,out_gas,winddir,windspeed,is_raining,soil_temp,soil_mois,uv,radon,CPM\n')

# get short-lived access token for user authorization
def get_initial_access_token():
    auth_url = 'https://www.dropbox.com/oauth2/authorize'
    token_url = 'https://api.dropbox.com/oauth2/token'

    auth_url += f'?client_id={APP_KEY}&response_type=code&token_access_type=offline'

    print(f"Visit this URL to get an authorization code: {auth_url}")
    auth_code = input("Enter the authorization code: ")

    data = {
        'code': auth_code,
        'grant_type': 'authorization_code',
    }
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()}',
    }
    response = requests.post(token_url, data=data, headers=headers)
    response_data = response.json()

    return response_data.get('access_token'), response_data.get('refresh_token')

# refresh to get longer access token
def refresh_access_token(refresh_token):
    token_url = 'https://api.dropbox.com/oauth2/token'

    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()}',
    }
    response = requests.post(token_url, data=data, headers=headers)
    response_data = response.json()

    return response_data.get('access_token')
    
def upload(
    access_token,
    file_path,
    target_path,
    timeout=900,
    chunk_size=4 * 1024 * 1024,
):
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        if file_size <= chunk_size:
            print(dbx.files_upload(f.read(), target_path))
        else:
            with tqdm(total=file_size, desc="Uploaded") as pbar:
                upload_session_start_result = dbx.files_upload_session_start(
                    f.read(chunk_size)
                )
                pbar.update(chunk_size)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell(),
                )
                commit = dropbox.files.CommitInfo(path=target_path)
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= chunk_size:
                        print(
                            dbx.files_upload_session_finish(
                                f.read(chunk_size), cursor, commit
                            )
                        )
                    else:
                        dbx.files_upload_session_append(
                            f.read(chunk_size),
                            cursor.session_id,
                            cursor.offset,
                        )
                        cursor.offset = f.tell()
                    pbar.update(chunk_size)

refresh_token = ''

for x in os.listdir():
    if x == 'key':
        with open("key") as f:
            refresh_token = f.read()

if not refresh_token:
    initial_access_token, refresh_token = get_initial_access_token()
    print("Initial access token:", initial_access_token)
    print("Refresh token:", refresh_token)
    with open("key", 'w+') as f:
        f.write(refresh_token)
    long_lived_access_token = refresh_access_token(refresh_token)
    print("Long-lived access token:", long_lived_access_token)

async def collect_data():
    global numInterrupts
    global is_raining
    global rain_interrupts
    global fname
    last_send = time.time()
    meas_time_start = time.time()
    while (True):
        print(f"time since: {time.time()-last_send}")
        print(f"num interrupts {numInterrupts}")
        to_write = ''
        to_write += str(time.time()) + ','
        windspeed = (numInterrupts/3.6) / (time.time()-meas_time_start)
        meas_time_start = time.time()
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
            
        try:
            winddirection = windDirection(ads.readADCSingleEnded(channel=0))
            to_write += str(winddirection)  + ',' + str(windspeed)+ ','
            to_write += str(rain_interrupts * 0.018) + ','
            rain_interrupts = 0
            print(f"wind direction: {winddirection} windspeed: {windspeed} is_raining: {rain_interrupts * 0.011}")
        except Exception as e:
            to_write += ',,,'
            print(e)
            print("Could not read wind direction (check ADC)")
            
        try:
            soiltemperature = DS18B20.readSoilTemp()
            to_write += str(soiltemperature) + ','
            print(f"soil temperature: {soiltemperature}")
        except Exception as e:
            print(e)
            to_write += ','
            print("Could not read soil temperature")
            
        try:
            soilmoisture = ads.readADCSingleEnded(channel=1)
            to_write += str(soilmoisture) + ','
            print(f"soil moisture: {soilmoisture}")
        except Exception as e:
            to_write += ','
            print("Could not read soil moisture (check ADC)")
            
        try:
            uv = ads.readADCSingleEnded(channel=2)
            to_write += str(uv) + ','
            print(f"UV: {uv}")
        except Exception as e:
            to_write += ','
            print("Could not read UV (check ADC)")

        try:
            radon = await RD200.read_radon()
            print(radon)
            if radon:
                to_write += str(radon) + ','
        except Exception as e:
            to_write += ','
            print("could not read radon")
            
        try:
            diygm = requests.get(url, verify=False)
            diygm_data = diygm.json()
            print(diygm_data['cpm_slow'][-1])
            to_write += str(diygm_data['cpm_slow'][-1]) + '\n'
        except Exception as e:
            to_write += ','
            print("Could not read diygm")

        numInterrupts = 0.0
        
        print()
        with open(fname, 'a+') as file:
            file.write(to_write)
        
        if time.time() - last_send >= 60*60*24:
            try:
                long_lived_access_token = refresh_access_token(refresh_token)
                print("Long-lived access token:", long_lived_access_token)
                upload(long_lived_access_token, fname, f"/ENGIN-NERS RWS/RWSlite-data-collection/{STATION_NAME}-{fname}")
                os.remove(fname)
                fname = f'rws_lite_data{time.time()}.csv'
                with open(fname, 'w+') as file:
                    file.write('time,in_temp,in_press,in_hum,in_gas,out_temp,out_press,out_hum,out_gas,winddir,windspeed,is_raining,soil_temp,soil_mois,uv,radon,CPM\n')
                last_send = time.time()
            except requests.exceptions.ConnectionError as ex:
                print(ex)
                print("Connection Error to Dropbox")
                time.sleep(1)
        
            
        plt.pause(1/POLL_RATE)

asyncio.run(collect_data())
