import physics108 as p108
import pandas as pd
import visa
import time
import signal
import sys, os
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

def clear_input():
	while msvcrt.kbhit():
		msvcrt.getch()

def configure_devices():
	for device in device_dict:
		device_dict[device].configure()
	time.sleep(p108.INIT_TIME_DELAY) # Need at least 20ms delay for devices to initialize

def main():
	signal.signal(signal.SIGINT, signal_handler)
	
	# Print welcome message and wait to begin
	print('\n=========================\n  Physics 108: BabyBlue\n=========================')
	print("\nPress SPACE to begin")
	t_prev = time.time()
	while not msvcrt.kbhit() or msvcrt.getch() != " ":
		t_now = time.time()
		if t_now - t_prev >= 1:
			t_prev = t_now
			sys.stdout.write('.')
			sys.stdout.flush()
	clear_input()
	
	# Create an identifier for the run using user input
	p108.RUN_IDENTIFIER = str(raw_input("\nIdentifier for this run? ")).strip('\n')
	clear_input()
	
	# Create devices that the program will communicate with
	rm = visa.ResourceManager()
	nanovoltmeter				= p108.Device_34420A(	p108.NANOVOLTMETER_ADDRESS, 		rm,	False	)
	multimeter_squid_curr_sense	= p108.Device_34401A(	p108.SQUID_CURRENT_SENSE_ADDRESS,	rm,	False	)
	multimeter_temperature		= p108.Device_34401A(	p108.TEMPERATURE_ADDRESS, 			rm,	False	)
	multimeter_mod_curr_sense 	= p108.Device_34401A(	p108.MOD_CURRENT_SENSE_ADDRESS,	 	rm,	False	)
	fngen_mod_curr_source		= p108.Device_DS345(	p108.MOD_CURRENT_SOURCE_ADDRESS,	rm,	False	)
	fngen_fieldcoil_curr_trig	= p108.Device_DS345(	p108.FIELDCOIL_CURRENT_TRIG_ADDRESS,rm, False	)
	magnet_programmer			= p108.Device_Model420(	p108.MAGNET_PROG_ADDRESS,			rm,	False	)
	fngen_ext_trigger 			= p108.Device_33120A(	p108.EXT_TRIGGER_ADDRESS,			rm,	False	)
	
	# Create a global dictionary which contains all of the devices
	# This way other methods can use the dictionary
	global device_dict
	device_dict = {	"nanovolt" : nanovoltmeter, 
					"squid_curr_sen" : multimeter_squid_curr_sense, 
					"temp" : multimeter_temperature,
					"mod_curr_sen" : multimeter_mod_curr_sense,
					"mod_curr_sour" : fngen_mod_curr_source,
					"fc_curr_sour" : fngen_fieldcoil_curr_trig,
					"magnet_prog" : magnet_programmer,
					"ext_trig" : fngen_ext_trigger}
	
	# Using user input, select a program to run
	print("Select an option:")
	print("\t(1) voltage-versus-time of squid")
	print("\t(2) voltage-versus-mod coil current")
	print("\t(3) magnet run with reset squid and nv measure")
	print("\t(4) magnet run")
	print("\t(5) reset squid")
	while(True):
		try:
			val = int(raw_input('Selection: ').strip('\n'))
			clear_input()
			p108.RUN_SELECTION_ID = val
			if p108.RUN_SELECTION_ID > 0 and p108.RUN_SELECTION_ID <= 5:
				print("Running program ID: " + str(p108.RUN_SELECTION_ID)),
				print(" with identifier '" + p108.RUN_IDENTIFIER + "'")
				break;
			else:
				print("Invalid number.")
		except ValueError:
			print("Must enter a number")
	
	# Configure all of the devices
	configure_devices()

	# (1) voltage-versus-time of squid
	if p108.RUN_SELECTION_ID == 1:
		print("Setting mod coil current to " + p108.MOD_CURR_OPTIMAL + " mA")
		fngen_mod_curr_source.set_optimal_current()
		fngen_ext_trigger.write(p108.FNGEN_TRIG_COMMAND)
		init_time = time.time()
		prev_data_time = init_time
		while True:
			if time.time() - prev_data_time >= p108.SAMPLING_TIMESTRETCH:
				sys.stdout.write('Measuring data...')
				multimeter_temperature.fetc_data()
				nanovoltmeter.fetc_data()
				multimeter_temperature.init()
				nanovoltmeter.init()
				prev_data_time = time.time()
				
				sys.stdout.write('\r')
				sys.stdout.flush()
				time.sleep(p108.INIT_TIME_DELAY)

	# (2) voltage-versus-mod coil current
	elif p108.RUN_SELECTION_ID == 2:
	
		fngen_mod_curr_source.set_current(##)
	
	# (3) magnet run with reset squid and nv measure
	elif p108.RUN_SELECTION_ID == 3:
		print("Are you sure you want to start the magnet?")
		while(True):
			mag = str(raw_input('(y/n) ')).strip('\n')
			if mag == 'y'
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
		
	# (4) magnet run
	elif p108.RUN_SELECTION_ID == 4:
		
	# (5) reset squid
	elif p108.RUN_SELECTION_ID ==5:
		
	
	
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

def save_data():
	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	if p108.TEST:
		filename = os.getcwd() + '\\data\\test\\' + str(p108.RUN_IDENTIFIER) + "_" + timestamp + ".csv"
	else:
		filename = os.getcwd() + '\\data\\3rd_cooldown\\' + str(p108.RUN_IDENTIFIER) + "_" + timestamp + ".csv"
	file = open(filename, "w")
	
	df_list = []
	for device in device_dict:
		if device_dict[device].data is not None:
			df_list.append(pd.DataFrame.from_dict(device_dict[device].get_complete_data(), orient='index'))
			
	#pd.DataFrame.from_dict(device_dict["nanovolt"].get_complete_data(), orient='index').to_csv(filename, header=False)


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