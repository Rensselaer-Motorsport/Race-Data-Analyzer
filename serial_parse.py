import serial
import math
import sensor_buffer

ser = serial.Serial(3)
ser.baudrate = 115200

beginPad = [1, 2, 3, 4, 5]
pads = [ord('\n'), 0]
endPad = 0

atEndPad = False


#waits for the begin pad
def isBeginPad(ser, beginPad):
    buffer = [0, 0, 0, 0, 0]
    while True:
        if buffer == beginPad:
            return True;
        else:
            for i in range(4):
                buffer[i] = buffer[i+1]
            buffer[4] = ord(ser.read())

def isEndPad(nextByte):
    if nextByte == endPad:
        return True
    else:
        return False

def isPad(nextByte):
    for p in pads:
        if nextByte == p:
            return True
    return False

def readData():
    global atEndPad
    #put data into list of bytes (will be in little endian order)
    byteLi = []
    nextByte = ord(ser.read())
    while not isPad(nextByte):
        byteLi.append(nextByte)
        nextByte = ord(ser.read())
    if isEndPad(nextByte):
        atEndPad = True
    #convert bytes back into integer form
    data = 0
    for i in range(0, len(byteLi)):
        data = data + byteLi[i] * math.pow(0x100, i)
    return data

if __name__ == '__main__':
    data = sensor_buffer.SensorBuffer()
    sensorNames = []
    data.addSensor('sensor0')
    sensorNames.append('sensor0')
    data.addSensor('sensor1')
    sensorNames.append('sensor1')
    while True:
        if isBeginPad(ser, beginPad):
            i = 0
            while True:
                ord(ser.read()) #throw out garbage byte
                value = readData()
                data.addSensorValue(sensorNames[i], value)
                print value
                i = i + 1
                if atEndPad:
                    atEndPad = False
                    break
