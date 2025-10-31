"""DS18B20"""

import datetime


def read_soil_temp() -> float | None:
    """Reads soil tempature, returns None on failure."""
    from w1thermsensor import W1ThermSensor

    try:
        sensor = W1ThermSensor()
        return sensor.get_temperature()
    except Exception as e:
        print(f"Could not read soil temperature: {e}")
        return None


def write_soil_temp():
    from w1thermsensor import W1ThermSensor

    sensor = W1ThermSensor()
    datum = sensor.get_temperature()
    current_time = datetime.datetime.now()
    filename = "rws-test/soiltemp.csv"

    file = open(filename, 'a+')
    new_entry = "%s,%.2f" % (current_time, datum)
    file.write(new_entry + "\n")
    file.close()
    print("wrote to %s: %s" % (filename, new_entry))
