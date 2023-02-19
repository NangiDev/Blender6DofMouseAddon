from time import sleep
import serial

# Depends on com0com, https://sourceforge.net/projects/com0com/

ser = serial.Serial(port='COM11', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)
ser.close()
ser.open()
ser.flush()

while (True):
    for i in range(6):
        data = 100 + (i*100)
        ser.write(data.to_bytes(4, byteorder='little'))
