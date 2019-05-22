import visa
import time
import sys

multimeter_address = 'GPIB0::3::INSTR'
time_measure = 5 # measurement time in seconds
samples_per_sec = 5

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())
	
	multimeter = rm.open_resource(multimeter_address)
	multimeter.write("*RST")
	multimeter.write("CONF:VOLT:DC")
	multimeter.write("TRIG:SOUR BUS")
	multimeter.write("SAMP:COUN 10")# + str(time_measure*samples_per_sec))
	time_delay_trig = 1 / samples_per_sec
	multimeter.write("TRIG:DEL 0.1")# + str(time_delay_trig))
	multimeter.write("INIT")
	multimeter.write("*TRG")
	time.sleep(5)
	data = multimeter.query("FETC?").split(',')
	
	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename = "C:/Users/T$/Git/physics108/Physics108_BABYBLUE/multiple_files/" + timestamp + ".txt"
	file = open(filename, "w")
	
	for datapoint in data:
		file.write(datapoint + '\n')
	
if __name__ == "__main__":
    main()