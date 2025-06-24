import station.chirp as chirp
import datetime

# These values needs to be calibrated for the percentage to work!
# The highest and lowest value the individual sensor outputs.
min_moist = 262
max_moist = 592

# Initialize the sensor.
chirp = chirp.Chirp(address=0x20,
                    read_moist=True,
                    read_temp=True,
                    read_light=True,
                    min_moist=min_moist,
                    max_moist=max_moist,
                    temp_scale='celsius',
                    temp_offset=0)

chirp.trigger()
datum = chirp.moist_percent
filename = "rws-test/soilmoist.csv"
current_time = datetime.datetime.now()

file = open(filename, 'a+')
new_entry = "%s,%.2f" % (current_time, datum)
file.write(new_entry + "\n")
file.close()
print("wrote to %s: %s" % (filename, new_entry))
