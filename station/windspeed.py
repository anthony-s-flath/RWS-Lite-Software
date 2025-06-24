import pigpio
import datetime
import time

PIN = 21

pi = pigpio.pi()
pi.set_mode(PIN, pigpio.INPUT)

numInterrupts = 0.0

def cb_func(gpio, level, tick):
    global numInterrupts
    numInterrupts += 1

cb = pi.callback(PIN, pigpio.RISING_EDGE, cb_func)

print("Sampling anenometer for 5 seconds...")

time.sleep(5)

datum = 2.4 * numInterrupts / 5.0
current_time = datetime.datetime.now()
filename = "rws-test/windspeed.csv"

file = open(filename, 'a+')
new_entry = "%s,%.2f" % (current_time, datum)
file.write(new_entry + "\n")
file.close()
print("wrote to %s: %s" % (filename, new_entry))
