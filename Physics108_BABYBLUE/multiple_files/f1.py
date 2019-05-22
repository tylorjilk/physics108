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

	nanovoltmeter					= p108.Device( p108.NANOVOLTMETER_ADDRESS, 			rm, 	True)
	multimeter_squid_curr_sense		= p108.Device( p108.SQUID_CURRENT_SENSE_ADDRESS, 	rm, 	False)
	multimeter_temperature			= p108.Device( p108.TEMPERATURE_ADDRESS, 			rm, 	True)
	multimeter_mod_curr_sense 		= p108.Device( p108.MOD_CURRENT_SENSE_ADDRESS,	 	rm, 	False)
	fngen_mod_curr_source			= p108.Device( p108.MOD_CURRENT_SOURCE_ADDRESS,		rm, 	False)
	fngen_fieldcoil_curr_trig		= p108.Device( p108.FIELDCOIL_CURRENT_TRIG_ADDRESS,	rm, 	False)
	magnet_programmer				= p108.Device( p108.MAGNET_PROG_ADDRESS,			rm, 	False)
	
	global device_dict
	device_list = [	"nanovolt" : nanovoltmeter, 
					"squid_curr_sen" : multimeter_squid_curr_sense, 
					"temp" : multimeter_temperature,
					"mod_curr_sen" : multimeter_mod_curr_sense,
					"mod_curr_sour" : fngen_mod_curr_source,
					"fc_curr_sour" : fngen_fieldcoil_curr_trig,
					"magnet_prog": magnet_programmer]
	
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
	
	dataframe = retrieve_data()
	dataframe.to_csv(filename)

def clear_devices():
	for device in device_dict:
		if device_dict[device].isEnabled():
			device_dict[device].write('*CLS')
			device_dict[device].write('*RST')
			
def retrieve_data():
	for device in device_dict:
		if device_dict[device].isEnabled():
			data = device_dict[device].get_complete_data()
			datalist.append(data)
	return pd.DataFrame({	'A'	: datalist[0],
							'B': datalist[1]	})
		
if __name__ == "__main__":
    main()