from time import sleep
import serial
import random

#
# This is a simulator for writing to a virtual comport
# So you don't have to connect the mouse to develop the Blender add-on
#

# For Windows you need a third party application to virtualize the serial port
# Example com0com, https://sourceforge.net/projects/com0com/

port = 'COM10'
baudrate = 115200
ser = serial.Serial(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)
ser.close()
ser.open()
ser.flush()

while (True):
    for i in range(6):
        data = random.randint(0, 1023)
        data = 110 + 100*i
        ser.write(data.to_bytes(4, byteorder='little'))
