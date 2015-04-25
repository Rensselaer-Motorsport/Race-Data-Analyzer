# Rensselaer Motorsports 2014/2015

# Author : Mitchell Mellone
# Version : 0.7.1
# Most Recent Edits : 2/20/15
# Description : A datastructure that will read sensor data from a text file generated
# from the sensor_buffer and hold it for display on the GUI

import numpy as np

class DataBase:
    def __init__(self):
        #The first entry in sensors will be a tuple of the elapsed time values (starting at 1)
        #After that each key is a sensor name, its value will be a tuple with each value
        self.sensors = {}
        self.sensors['time'] = ()

        #The key is the sensor (or time), and the corresponding value is a tuple with the lowest (at [0]) and highest (at [1]) sensor values
        self.sensor_extremes = {}

        #the date and time will be the date and time of the first sensor reading
        self.date = "2000-01-31"
        self.time = "00:00:00.000000"

    #parses a file created by the sensor_buffer class
    def parse_file(self, file_name):
        #open the input file
        f = open(file_name, 'r')

        #read in the names of all the sensors and input into dictionary
        sensorLine = f.readline()
        sensorList = sensorLine.split() #create a list holding all of the sensors
        for sensor in sensorList:
            self.sensors[sensor] = ()
            self.sensor_extremes[sensor] = 'first'

        #read in all sensor data
        prev_time =0
        total_time = 0
        for line in f:
            valueList = line.split() #parse the values
            if prev_time == 0:
                self.date = valueList[0] #set the date of the database
                self.time = valueList[1] #set the time of the database
                prev_time = valueList[1] #set the first previous time to be the first time listed
            total_time += self.elapsed_time(prev_time, valueList[1]) #update the total time elapsed
            self.sensors['time'] += (total_time, ) #add the total time elapsed to the dictionary
            prev_time = valueList[1]
            for i in range(2, len(valueList)):
                val = float(valueList[i])
                self.sensors[sensorList[i-2]] += (val, ) #add the value to the sensor
                if self.sensor_extremes[sensorList[i-2]] == 'first':
                    self.sensor_extremes[sensorList[i-2]] = [val, val] #if this is the first value then just add it to the sensor_extremes
                else:
                    curr_min = self.sensor_extremes[sensorList[i-2]][0]
                    curr_max = self.sensor_extremes[sensorList[i-2]][1]
                    if val < curr_min:
                        self.sensor_extremes[sensorList[i-2]][0] = val #if the value is less than current min, make it the min
                    if val > curr_max:
                        self.sensor_extremes[sensorList[i-2]][1] = val #if the value is more than the current max, make it the max
            self.sensor_extremes['time'] = [0, total_time]

    #calculate the elapsed time between prev_time and current_time
    def elapsed_time(self, prev_time, current_time):
        prev_time_in_sec = float(prev_time[0:2])*3600 + float(prev_time[3:5])*60 + float(prev_time[6:])
        current_time_in_sec = float(current_time[0:2])*3600 + float(current_time[3:5])*60 + float(current_time[6:])
        return current_time_in_sec - prev_time_in_sec

    #return the array of elapsed times
    def get_elapsed_times(self):
        return np.array(self.sensors['time'])

    #return the 2 dimensional array of sensors and their corresponding values
    def get_sensor_values(self, sensor_name):
        return np.array(self.sensors[sensor_name])

    def get_min_sensor_value(self, sensor_name):
        return self.sensor_extremes[sensor_name][0]

    def get_max_sensor_value(self, sensor_name):
        return self.sensor_extremes[sensor_name][1]

    def get_list_of_sensors(self):
        sens_list = []
        for sen in self.sensors.keys():
            if sen != 'time':
                sens_list.append(sen)
        return sens_list

    #binary search for the index for an actual data points time closest to the given time (x)
    def normalize_time(self, x):
        t = self.sensors['time']
        low = 0
        mid = len(t)/2
        hi = len(t)-1
        if (x <= t[low]):
            return 0
        if (x >= t[hi]):
            return len(t)-1
        while low != mid and hi !=mid:
            if (x < t[mid]):
                hi = mid
                mid = (hi+low)/2
            elif (x > t[mid]):
                low = mid
                mid = (hi+low)/2
            else:
                return mid
        return mid
