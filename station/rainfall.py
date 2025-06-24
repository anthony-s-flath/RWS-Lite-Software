import pigpio
import datetime
import time

PIN = 20

pi = pigpio.pi()
pi.set_mode(PIN, pigpio.INPUT)
filename = "rws-test/rainfall.csv"

prev_time = datetime.datetime.now()

def cb_func(gpio, level, tick):
    global prev_time
    current_time = datetime.datetime.now()
    if current_time > prev_time + datetime.timedelta(seconds=1): # debounce
        file = open(filename, 'a+')
        file.write(str(current_time) + "\n")
        file.close()
        print("wrote %s to %s" % (str(current_time), filename))
        prev_time = current_time

cb = pi.callback(PIN, pigpio.RISING_EDGE, cb_func)

while True:
    time.sleep(300)
