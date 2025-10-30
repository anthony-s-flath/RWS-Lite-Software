"""DS18B20"""

import datetime

from driver import config
if not config.DEBUG:
    from w1thermsensor import W1ThermSensor  # wont work on debug


def read_soil_temp() -> float:
    try:
        sensor = W1ThermSensor()
        return sensor.get_temperature()
    except Exception as e:
        print(e)
        print("Could not read soil temperature")
        return float("nan")


def write_soil_temp():
    sensor = W1ThermSensor()
    datum = sensor.get_temperature()
    current_time = datetime.datetime.now()
    filename = "rws-test/soiltemp.csv"

    file = open(filename, 'a+')
    new_entry = "%s,%.2f" % (current_time, datum)
    file.write(new_entry + "\n")
    file.close()
    print("wrote to %s: %s" % (filename, new_entry))
