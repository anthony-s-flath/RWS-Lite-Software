import datetime
import board
import busio
import adafruit_veml6075

i2c = busio.I2C(board.SCL, board.SDA)

veml = adafruit_veml6075.VEML6075(i2c, integration_time=100)

datum = veml.uv_index
current_time = datetime.datetime.now()
filename = "rws-test/uv.csv"

file = open(filename, 'a+')
new_entry = "%s,%.2f" % (current_time, datum)
file.write(new_entry + "\n")
file.close()
print("wrote to %s: %s" % (filename, new_entry))
