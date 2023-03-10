from time import sleep
import serial

#
# This is a simulator for reading from the Arduino
# So you don't have to start Blender and the add-on to develop the mouse
#

port = 'COM10'
baudrate = 115200
ser = serial.Serial(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)
ser.close()
ser.open()
ser.flush()

while (True):
    data = ser.read(2)
    ser.read(2)
    result = int.from_bytes(data, byteorder='little')
    print(result)
