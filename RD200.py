import serial
import time

#don't touch this, from oscilloscope
#in ASCII this is literally "VALUE?"'
#the quotations are part of the message
#the RD200 will send back a string message in the format
GET_DATA = b'\x02\x56\x41\x4C\x55\x45\x3F\x0D\x0A'

def read_radon():
    #baud must be 19200 because that's what the RD200 takes
    ser = serial.Serial('/dev/ttyS0', 19200, timeout=5)

    ser.write(GET_DATA)
    message = b''
    
    while True:
        byte = ser.read()
        if not byte:
            break
        
        message += byte
    return message