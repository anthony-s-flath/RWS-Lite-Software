import board
import busio
import datetime
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)

channel = AnalogIn(ads, ADS.P0)

vals = ((0, 33000),
        (22.5, 6570),
        (45, 8200),
        (67.5, 891),
        (90, 1000),
        (112.5, 688),
        (135, 2200),
        (157.5, 1410),
        (180, 3900),
        (202.5, 3140),
        (225, 16000),
        (247.5, 14120),
        (270, 120000),
        (292.5, 42120),
        (315, 64900),
        (337.5, 21880))

r = 10000*channel.voltage / (3.3-channel.voltage)
closest_index = 0
closest_dist = 1000000
for x in range(0, 16):
    if abs(r - vals[x][1]) < closest_dist:
        closest_index = x
        closest_dist = abs(r - vals[x][1])

datum = vals[closest_index][0]
current_time = datetime.datetime.now()
filename = "rws-test/winddir.csv"

file = open(filename, 'a+')
new_entry = "%s,%.2f" % (current_time, datum)
file.write(new_entry + "\n")
file.close()
print("wrote to %s: %s" % (filename, new_entry))
