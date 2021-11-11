import smbus2
import bme280
import datetime

port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

data = bme280.sample(bus, address, calibration_params)

def writeToFile(datum, filename, current_time):
	file = open(filename, 'a+')
	new_entry = "%s,%.2f" % (current_time, datum)
	file.write(new_entry + "\n")
	file.close()
	print("wrote to %s: %s" % (filename, new_entry))

current_time = datetime.datetime.now()
writeToFile(data.temperature, "rws-test/temp.csv", current_time)
writeToFile(data.pressure, "rws-test/pressure.csv", current_time)
writeToFile(data.humidity, "rws-test/humidity.csv", current_time)
