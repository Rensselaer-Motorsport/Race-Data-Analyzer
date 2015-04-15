import datetime

class SensorBuffer:

	#initializes the class.
	def __init__(self):
		#sensor_dict is a dictionary holding other dictionarys of seperate sensors
		self.sensor_dict = {}

	#adds a new sensor to the end of the dictionary
	#param sensor_name is the key for the sensor
	def addSensor (self, sensor_name):
		for key in self.sensor_dict.keys():
			if sensor_name == key:
				print "Sensor already added"
				return
		self.sensor_dict[sensor_name] = []

	#adds a value to the end of a specified sensor
	#param sensor_name is the name of sensor/dictionary key
	#param new value is the value to be added
	def addSensorValue (self, sensor_name, new_value):
		found = False
		for key in self.sensor_dict.keys():
			if sensor_name == key:
				found = True
				break
		if found:
			self.sensor_dict[sensor_name].append(new_value)
		else:
			print "Sensor does not exist"


	#prints the last value from each sensor to a file with a time stamp, appending the file
	#does NOT erase the last value from the sensor
	#the format is...
	#yyyy-mm-dd hh:mm:ss.ssssss sensorAvalue sensorBvalue sensorCvalue etc.
	def getValues (self, file_name):
		f = open(file_name, 'a')
		f.write (str(datetime.datetime.now()) + " ")
		for sensor_name in self.sensor_dict.keys():
			lastIndex = len(self.sensor_dict[sensor_name]) - 1
			if lastIndex >= 0:
				f.write(str(self.sensor_dict[sensor_name][lastIndex]) + ' ')
		f.write('\n')
		f.close()

	#prints all of the sensor names in the order they are in the dictionary
	def getSensors (self, file_name):
		f = open(file_name, 'a')
		for sensor_name in self.sensor_dict.keys():
			f.write(sensor_name + ' ')
		f.write('\n')
		f.close()
