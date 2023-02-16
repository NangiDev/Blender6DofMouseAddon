from time import sleep
import serial

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)
ser.close()
ser.open()
ser.flush()

while (True):
    data = ser.read(2)
    ser.read(2)
    result = int.from_bytes(data, byteorder='little')
    print(result)
