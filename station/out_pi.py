# Data kept from interrupts on raspberry pi outside
# wind speed and rain and some mystery Pin 4

import datetime
import time
import pigpio
from driver.config import CALLBACK_SLEEP
from driver import config
from driver.globals import Datatype


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
    if (config.DEBUG 
        or not config.options[Datatype.WIND_SPEED]
        or not config.options[Datatype.IS_RAINING]):
        return
    
    pi = pigpio.pi()


    # what is this for?
    #pi.set_mode(4, pigpio.INPUT)
    #pi.set_pull_up_down(4, pigpio.PUD_UP)

    if config.options[Datatype.IS_RAINING]:
        pi.set_mode(PIN_RAIN, pigpio.INPUT)
        pi.set_pull_up_down(PIN_RAIN, pigpio.PUD_DOWN)
        pi.callback(PIN_RAIN, pigpio.RISING_EDGE, rain_callback)

    if config.options[Datatype.WIND_SPEED]:
        pi.set_mode(PIN_WIND_SPEED, pigpio.INPUT)
        pi.set_pull_up_down(PIN_WIND_SPEED, pigpio.PUD_OFF)
        pi.callback(PIN_WIND_SPEED, pigpio.RISING_EDGE, wind_speed_callback)


