# Data kept from interrupts on raspberry pi outside
# wind speed and rain and some mystery Pin 4

import datetime
import time
import pigpio
import rws.driver as driver
from rws.driver import CALLBACK_SLEEP, Datatype


PIN_RAIN = 20
PIN_WIND_SPEED = 21

wind_interrupts = 0
is_raining = False
rain_interrupts = 0


def _rain_callback(gpio, level, tick):
    global rain_interrupts
    rain_interrupts += 1
    time.sleep(CALLBACK_SLEEP)


def _wind_speed_callback(gpio, level, tick):
    global wind_interrupts
    wind_interrupts += 1
    time.sleep(CALLBACK_SLEEP)


def init():
    
    pi = pigpio.pi()



    if driver.OPTIONS[Datatype.IS_RAINING]:
        pi.set_mode(PIN_RAIN, pigpio.INPUT)
        pi.set_pull_up_down(PIN_RAIN, pigpio.PUD_DOWN)
        pi.callback(PIN_RAIN, pigpio.RISING_EDGE, _rain_callback)

    if driver.OPTIONS[Datatype.WIND_SPEED]:
        pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)
        pi.set_pull_up_down(PIN_WIND_SPEED, pigpio.PUD_OFF)
        pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, _wind_speed_callback)
    
    
    # what is this for?
    pi.set_mode(4, pigpio.INPUT)
    pi.set_pull_up_down(4, pigpio.PUD_UP)


