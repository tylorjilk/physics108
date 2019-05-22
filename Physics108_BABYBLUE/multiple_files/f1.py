import physics108 as p108
import pandas as pd
import visa
import time
import signal
import sys

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	print('Resetting devices...')
	clear_devices()
	print('Saving data...')
	save_data()
	print('Goodbye')
	sys.exit(0)

def main():
	p108.RUN_IDENTIFIER = str(raw_input("Identifier for this run?  "))
	signal.signal(signal.SIGINT, signal_handler)
	rm = visa.ResourceManager()
	
	global nanovoltmeter
	global multimeter_squid_curr_sense
	global multimeter_temperature
	global multimeter_mod_curr_sense
	global fngen_mod_curr_source
	global fngen_fieldcoil_curr_trig
	global magnet_programmer
	
	nanovoltmeter					= p108.Device( p108.NANOVOLTMETER_ADDRESS, 			rm, 	True)
	multimeter_squid_curr_sense		= p108.Device( p108.SQUID_CURRENT_SENSE_ADDRESS, 	rm, 	False)
	multimeter_temperature			= p108.Device( p108.TEMPERATURE_ADDRESS, 			rm, 	True)
	multimeter_mod_curr_sense 		= p108.Device( p108.MOD_CURRENT_SENSE_ADDRESS,	 	rm, 	False)
	fngen_mod_curr_source			= p108.Device( p108.MOD_CURRENT_SOURCE_ADDRESS,		rm, 	False)
	fngen_fieldcoil_curr_trig		= p108.Device( p108.FIELDCOIL_CURRENT_TRIG_ADDRESS,	rm, 	False)
	magnet_programmer				= p108.Device( p108.MAGNET_PROG_ADDRESS,			rm, 	False)
	
	global device_list
	device_list = [	nanovoltmeter, 
					multimeter_squid_curr_sense, 
					multimeter_temperature,
					multimeter_mod_curr_sense,
					fngen_mod_curr_source,
					fngen_fieldcoil_curr_trig]
	
	configure_devices()
	configure_data_constants()
	
	while(True):
		nanovoltmeter.init()
		multimeter_temperature.init()
		time.sleep(10)
		print("Nanovolt data:")
		print(nanovoltmeter.fetc_data())
		print("Temperature data:")
		print(multimeter_temperature.fetc_data())

def configure_devices():
	multimeter_temperature.write('CONF:VOLT:DC')
	multimeter_temperature.write('TRIG:SOUR EXT')
	multimeter_temperature.write('TRIG:COUN 50')
	
	nanovoltmeter.write('CONF:VOLT:DC:DIFF')
	nanovoltmeter.write('SENS:VOLT:DC:NPLC 2')
	nanovoltmeter.write('TRIG:SOUR EXT')
	nanovoltmeter.write('TRIG:COUN 50')
	nanovoltmeter.write('TRIG:DEL 0')

def save_data():
	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/testdata/" + str(p108.RUN_IDENTIFIER) + "_" + timestamp + ".txt"
	file = open(filename, "w")
	
	datalist = []
	for device in device_list:
		if device.isEnabled():
			data = device.get_complete_data()
			datalist.append(data)
	df = pd.DataFrame({	'A': datalist[0],
						'B': datalist[1]	})
	df.to_csv(filename)

def clear_devices():
	for device in device_list:
		if device.isEnabled():
			device.write('*CLS')
			device.write('*RST')
		
if __name__ == "__main__":
    main()