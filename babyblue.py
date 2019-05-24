import physics108 as p108
import pandas as pd
import visa
import time
import signal
import sys
import msvcrt

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	print('\nYou pressed ctrl c')
	print('Resetting devices.')
	#clear_devices()
	print('Saving data...'),
	save_data()
	print('goodbye.')
	sys.exit(0)

def main():
	print("Press space to begin.")
	while not msvcrt.kbhit() or msvcrt.getch() != " ":
		sys.stdout.write('.')
		time.sleep(1)

	clear_input()
	
	
	p108.RUN_IDENTIFIER = str(raw_input("\nIdentifier for this run?  ")).strip('\n')
	
	clear_input()
	
	signal.signal(signal.SIGINT, signal_handler)
	rm = visa.ResourceManager()
	
	nanovoltmeter					= p108.Device( p108.NANOVOLTMETER_ADDRESS, 			rm, 	True	)
	multimeter_squid_curr_sense		= p108.Device( p108.SQUID_CURRENT_SENSE_ADDRESS, 	rm, 	False	)
	multimeter_temperature			= p108.Device( p108.TEMPERATURE_ADDRESS, 			rm, 	False	)
	multimeter_mod_curr_sense 		= p108.Device( p108.MOD_CURRENT_SENSE_ADDRESS,	 	rm, 	False	)
	fngen_mod_curr_source			= p108.Device( p108.MOD_CURRENT_SOURCE_ADDRESS,		rm, 	False	)
	fngen_fieldcoil_curr_trig		= p108.Device( p108.FIELDCOIL_CURRENT_TRIG_ADDRESS,	rm, 	True	)
	magnet_programmer				= p108.Device( p108.MAGNET_PROG_ADDRESS,			rm, 	True	)
	fngen_ext_trigger 				= p108.Device( p108.EXT_TRIGGER_ADDRESS,			rm,		True	)
	
	global device_dict
	device_dict = {	"nanovolt" : nanovoltmeter, 
					"squid_curr_sen" : multimeter_squid_curr_sense, 
					"temp" : multimeter_temperature,
					"mod_curr_sen" : multimeter_mod_curr_sense,
					"mod_curr_sour" : fngen_mod_curr_source,
					"fc_curr_sour" : fngen_fieldcoil_curr_trig,
					"magnet_prog" : magnet_programmer,
					"ext_trig" : fngen_ext_trigger}
	
	configure_devices()
	time.sleep(p108.INIT_TIME_DELAY)	

	fngen_ext_trigger.write(p108.FNGEN_TRIG_COMMAND)
	init_time = time.time()
	prev_data_time = init_time
	
	while(True):
		while not msvcrt.kbhit() or msvcrt.getch() != "m":
			if time.time() - prev_data_time >= p108.SAMPLING_TIMESTRETCH:
				sys.stdout.write('Measuring data...')
				multimeter_temperature.fetc_data() # Want to measure right away after the magnet though
				nanovoltmeter.fetc_data()
				multimeter_temperature.init()
				nanovoltmeter.init()
				prev_data_time = time.time()
				sys.stdout.write('\r')
				sys.stdout.flush()
				time.sleep(p108.INIT_TIME_DELAY)
		clear_input()
		print("Data capture paused.")
		print("Are you sure you want to start the magnet?")
		while(True):
			mag = str(raw_input('(y/n)  ')).strip('\n')
			if mag == 'y':
				ramp_up_magnet()
				log_ramp_up()
				time.sleep(5)
				ramp_down_magnet()
				log_ramp_down()
				drive_field_coil()
				break
			elif mag == 'n':
				print("NOT starting magnet.")
				break
			else:
				print("There are only two possible answers. Try again.")

def configure_devices():
	multimeter_temperature = device_dict["temp"]
	multimeter_temperature.write('CONF:VOLT:DC')
	multimeter_temperature.write('TRIG:SOUR EXT')
	multimeter_temperature.write('TRIG:COUN ' + str(p108.SAMPLING_NUM_POINTS))
	multimeter_temperature.init()
	
	nanovoltmeter = device_dict["nanovolt"]
	nanovoltmeter.write('CONF:VOLT:DC:DIFF')
	nanovoltmeter.write('SENS:VOLT:DC:NPLC 2')
	nanovoltmeter.write('TRIG:SOUR EXT')
	nanovoltmeter.write('TRIG:COUN ' + str(p108.SAMPLING_NUM_POINTS))
	nanovoltmeter.write('TRIG:DEL 0')
	nanovoltmeter.init()
	
	magnet = device_dict["magnet_prog"]
	magnet.write("CONF:RAMP:RATE:CURR " + str(p108.MAGNET_CURRENT_RAMP_RATE) + " A/s")
	
	fngen_ext_trigger = device_dict["ext_trig"]
	fngen_ext_trigger.write(p108.FNGEN_ZERO_COMMAND)	

def save_data():
	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	if p108.TEST:
	filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/data/test/" + str(p108.RUN_IDENTIFIER) + "_" + timestamp + ".csv"
	else:
		filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/data/3rd_cooldown/" + str(p108.RUN_IDENTIFIER) + "_" + timestamp + ".csv"
	file = open(filename, "w")
	
	pd.DataFrame.from_dict(device_dict["nanovolt"].get_complete_data(), orient='index').to_csv(filename, header=False)
	

	
	#dataframe = retrieve_data()
	#dataframe.to_csv(filename)

def clear_devices():
	for device in device_dict:
		if device is not "magnet_prog":
			if device_dict[device].isEnabled():
				device_dict[device].write('*CLS')
				device_dict[device].write('*RST')
			
def retrieve_data():
	datalist = []
	for device in device_dict:
		if device_dict[device].isEnabled():
			data = device_dict[device].get_complete_data()
			datalist.append(data)
	return pd.DataFrame({	'A'	: datalist[0],
							'B': datalist[1]	})

def clear_input():
	while msvcrt.kbhit():
		msvcrt.getch()

def ramp_up_magnet():
	print("Starting magnet ramp up.")
	magnet = device_dict["magnet_prog"]
	magnet.write("CONF:CURR:PROG "+str(p108.MAGNET_CURRENT_TARGET))
	magnet.write("RAMP")

def ramp_down_magnet():
	print('Ramping down magnet.')
	magnet = device_dict["magnet_prog"]
	magnet.write('ZERO')
	
def log_ramp_up():
	magnet = device_dict["magnet_prog"]
	current = 0
	while current < p108.MAGNET_CURRENT_TARGET - p108.MAGNET_CURRENT_MARGIN:
		current = magnet.fetc_data_magnet()
		sys.stdout.write('Ramping magnet: ' + str(current) + ' A   ')
		sys.stdout.write('\r')
		sys.stdout.flush()
		time.sleep(p108.SAMPLING_DELAY_MAGNET)
	print('\nTarget current of ' + str(p108.MAGNET_CURRENT_TARGET) + ' A achieved.')
	
def log_ramp_down():
	magnet = device_dict["magnet_prog"]
	current = magnet.fetc_data_magnet()
	while current > p108.MAGNET_CURRENT_MARGIN:
		current = magnet.fetc_data_magnet()
		sys.stdout.write('Ramping magnet: ' + str(current) + ' A   ')
		sys.stdout.write('\r')
		sys.stdout.flush()
		time.sleep(p108.SAMPLING_DELAY_MAGNET)
	print('\nMagnet successfully ramped down.')
	
def drive_field_coil():
	print("Starting field coils..."),
	fngen_fieldcoil_curr_trig = device_dict["fc_curr_sour"]
	fngen_fieldcoil_curr_trig.write("OFFS 1 VP")
	time.sleep(1)
	fngen_fieldcoil_curr_trig.write('OFFS 0 VP')
	print(" done.")
		
if __name__ == "__main__":
    main()