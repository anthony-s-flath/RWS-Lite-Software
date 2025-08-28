# Data kept from interrupts on raspberry pi outside
# wind speed and rain and some mystery Pin 4

import datetime
import time
import pigpio
from driver.config import CALLBACK_SLEEP


PIN_RAIN = 20
PIN_WIND_SPEED = 21

wind_interrupts = 0
is_raining = False
rain_interrupts = 0

def rain_callback(gpio, level, tick):
    global rain_interrupts
    rain_interrupts += 1
    time.sleep(CALLBACK_SLEEP)

def wind_speed_callback(gpio, level, tick):
    global wind_interrupts
    wind_interrupts += 1
    time.sleep(CALLBACK_SLEEP)


def init():
    pi = pigpio.pi()
    pi.set_mode(PIN_RAIN, pigpio.INPUT)
    pi.set_pull_up_down(PIN_RAIN, pigpio.PUD_DOWN)

    pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)
    pi.set_pull_up_down(PIN_WIND_SPEED, pigpio.PUD_OFF)

    # what is this for?
    pi.set_mode(4, pigpio.INPUT)
    pi.set_pull_up_down(4, pigpio.PUD_UP)

    pi.callback(PIN_RAIN, pigpio.RISING_EDGE, rain_callback)
    pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, wind_speed_callback)
