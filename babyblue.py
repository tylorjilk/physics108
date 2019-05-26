import physics108 as p108
import pandas as pd
import numpy as np
import visa
import time
import signal
import sys, os
import msvcrt

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	print('\nYou pressed ctrl c')
	print('Resetting devices.')
	clear_devices()
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
	#time.sleep(p108.INIT_TIME_DELAY) # Need at least 20ms delay for devices to initialize
	
def init_devices():
	time_now = time.time()
	for device in device_dict:
		if device_dict[device].needs_init():
			device_dict[device].init(time_now)

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
		if device_dict[device].data is not None and device_dict[device].isEnabled():
			df = pd.DataFrame.from_dict(device_dict[device].get_complete_data())
			df_list.append(df)
	for df in df_list:
		if df.empty:
			df_list.remove(df)
	df_final = pd.DataFrame()
	if len(df_list) > 1:
		df0 = df_list[0]
		df_final = df0
		df_list.remove(df0)
		while len(df_list) >= 1:
			df1 = df_list[0]
			df_final = pd.merge(df1,df_final,on=['timestamp'],how='outer')
			df_list.remove(df1)
	else:
		df_final = df_list[0]
	print('\n')
	print(df_final)
	df_final.to_csv(filename)

def clear_devices():
	for device in device_dict:
		if device_dict[device].needs_init():
			device_dict[device].write('*CLS')
			device_dict[device].write('*RST')
		if device is "ext_trig":
			device_dict[device].write(p108.FNGEN_ZERO_COMMAND)

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
	nanovoltmeter				= p108.Device_34420A(	p108.NANOVOLTMETER_ADDRESS, 		p108.NANOVOLTMETER_COLUMN_HEADING,	rm,	True	)
	multimeter_squid_curr_sense	= p108.Device_34401A(	p108.SQUID_CURRENT_SENSE_ADDRESS,	p108.SQUID_CURR_SEN_COLUMN_HEADING,	rm,	True	)
	multimeter_temperature		= p108.Device_34401A(	p108.TEMPERATURE_ADDRESS, 			p108.TEMPERATURE_COLUMN_HEADING,	rm,	False	)
	multimeter_mod_curr_sense 	= p108.Device_34401A(	p108.MOD_CURRENT_SENSE_ADDRESS,	 	p108.MOD_CURR_SEN_COLUMN_HEADING,	rm,	True	)
	fngen_mod_curr_source		= p108.Device_DS345(	p108.MOD_CURRENT_SOURCE_ADDRESS,										rm,	True	)
	fngen_fieldcoil_curr_trig	= p108.Device_DS345(	p108.FIELDCOIL_CURRENT_TRIG_ADDRESS,									rm, False	)
	multimeter_fieldcoil_sense	= p108.Device_34401A(	p108.FIELDCOIL_CURRENT_SEN_ADDRESS,	p108.FC_CURR_SEN_COLUMN_HEADING,	rm,	False	)
	magnet_programmer			= p108.Device_Model420(	p108.MAGNET_PROG_ADDRESS,			p108.MAGNET_PROG_COLUMN_HEADING	,	rm,	False	)
	fngen_ext_trigger 			= p108.Device_33120A(	p108.EXT_TRIGGER_ADDRESS,												rm,	True	)
	
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
		print("Setting mod coil current to " + str(p108.MOD_CURR_OPTIMAL) + " mA")
		fngen_mod_curr_source.set_optimal_current()
		init_devices()
		time.sleep(p108.INIT_TIME_DELAY)
		fngen_ext_trigger.write(p108.FNGEN_TRIG_COMMAND)
		prev_data_time = time.time()
		while True:
			if time.time() - prev_data_time >= p108.SAMPLING_TIMESTRETCH:
				sys.stdout.write('Measuring data...')
				multimeter_temperature.fetc_data()
				nanovoltmeter.fetc_data()
				multimeter_squid_curr_sense.fetc_data()
				multimeter_mod_curr_sense.fetc_data()
				#multimeter_fieldcoil_sense.fetc_data()
				prev_data_time = time.time()
				init_devices()
				
				sys.stdout.write('\r')
				sys.stdout.flush()
				time.sleep(p108.INIT_TIME_DELAY)

	# (2) voltage-versus-mod coil current
	elif p108.RUN_SELECTION_ID == 2:
		fngen_ext_trigger.write(p108.FNGEN_TRIG_COMMAND)
		curr_list = np.linspace(0, p108.MOD_CURR_TARGET_MAX, p108.MOD_CURR_TARGET_MAX/p108.MOD_CURR_STEP)
		fngen_mod_curr_source.set_current(0)
		step = 1
		prev_data_time = time.time()
		prev_curr_time = prev_data_time
		init_devices()
		while True:
			if time.time() - prev_data_time >= p108.SAMPLING_TIMESTRETCH:
				sys.stdout.write('Measuring data...')
				multimeter_temperature.fetc_data()
				nanovoltmeter.fetc_data()
				multimeter_mod_curr_sense.fetc_data()
				multimeter_squid_curr_sense.fetc_data()
				prev_data_time = time.time()
				init_devices()
				
				sys.stdout.write('\r')
				sys.stdout.flush()
				time.sleep(p108.INIT_TIME_DELAY)
			if time.time() - prev_curr_time >= p108.MOD_CURR_TIME_STEP:
				prev_curr_time = time.time()
				print(curr_list[step])
				fngen_mod_curr_source.set_current(curr_list[step])
				step += 1
			if step >= len(curr_list):
				break
		fngen_mod_curr_source.set_current(0)
		save_data()
	
	# (3) magnet run with reset squid and nv measure
	elif p108.RUN_SELECTION_ID == 3:
		init_devices()
		print("Are you sure you want to start the magnet?")
		while(True):
			mag = str(raw_input('(y/n) ')).strip('\n')
			if mag == 'y':
				print("Double check stability settings and voltage limit.")
				print("Then press space to start for real.")
				t_prev = time.time()
				while not msvcrt.kbhit() or msvcrt.getch() != " ":
					t_now = time.time()
					if t_now - t_prev >= 1:
						t_prev = t_now
						sys.stdout.write('.')
						sys.stdout.flush()
				clear_input()
				ramp_up_magnet()
				log_ramp_up()
				print("Press enter to start the rampdown and then field coils.")
				t_prev = time.time()
				while not msvcrt.kbhit() or msvcrt.getch() != "\r":
					t_now = time.time()
					if t_now - t_prev >= 1:
						t_prev = t_now
						sys.stdout.write('.')
						sys.stdout.flush()
				clear_input()
				ramp_down_magnet()
				log_ramp_down(True)
				break
			elif mag == 'n':
				print("NOT starting magnet.")
				break
			else:
				print("There are only two possible answers. Try again.")
		prev_data_time = time.time()
		while True:
			if time.time() - prev_data_time >= p108.SAMPLING_TIMESTRETCH:
				sys.stdout.write('Measuring data...' + str(prev_data_time) + '      ')
				multimeter_temperature.fetc_data()
				nanovoltmeter.fetc_data()
				prev_data_time = time.time()
				init_devices()
				
				sys.stdout.write('\r')
				sys.stdout.flush()
				time.sleep(p108.INIT_TIME_DELAY)
		save_data()
		
	# (4) magnet run
	elif p108.RUN_SELECTION_ID == 4:
		print("Are you sure you want to start the magnet?")
		while(True):
			mag = str(raw_input('(y/n) ')).strip('\n')
			if mag == 'y':
				print("Double check stability settings and voltage limit.")
				print("Then press space to start for real.")
				t_prev = time.time()
				while not msvcrt.kbhit() or msvcrt.getch() != " ":
					t_now = time.time()
					if t_now - t_prev >= 1:
						t_prev = t_now
						sys.stdout.write('.')
						sys.stdout.flush()
				clear_input()
				ramp_up_magnet()
				log_ramp_up()
				print("Press enter to start the rampdown.")
				t_prev = time.time()
				while not msvcrt.kbhit() or msvcrt.getch() != "\r":
					t_now = time.time()
					if t_now - t_prev >= 1:
						t_prev = t_now
						sys.stdout.write('.')
						sys.stdout.flush()
				clear_input()
				ramp_down_magnet()
				log_ramp_down(False)
				break
			elif mag == 'n':
				print("NOT starting magnet.")
				break
			else:
				print("There are only two possible answers. Try again.")
		save_data()

	# (5) reset squid
	elif p108.RUN_SELECTION_ID ==5:
		print("Starting field coils..."),
		fngen_fieldcoil_curr_trig.set_fc_current(p108.FIELDCOIL_TARGET_CURRENT)
		time_init = time.time()
		while True:
			if time.time() - time_init >= p108.FIELDCOIL_RESET_TIME:
				print("and done.")
				fngen_fieldcoil_curr_trig.set_fc_current(0)
				break
			
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
	print('\nRamping down magnet.')
	magnet = device_dict["magnet_prog"]
	while True:
		try:
			magnet.write('ZERO')
			break
		except IOError:
			print("error zero-ing magnet")
	
def log_ramp_up():
	magnet = device_dict["magnet_prog"]
	current = 0
	while current < p108.MAGNET_CURRENT_TARGET - p108.MAGNET_CURRENT_MARGIN:
		current = magnet.take_datapoint()
		sys.stdout.write('Ramping magnet: ' + str(current) + ' A   ')
		sys.stdout.write('\r')
		sys.stdout.flush()
		time.sleep(p108.SAMPLING_DELAY_MAGNET)
	print('\nTarget current of ' + str(p108.MAGNET_CURRENT_TARGET) + ' A achieved.')
	
def log_ramp_down(fieldcoil_bool):
	magnet = device_dict["magnet_prog"]
	fngen_fieldcoil_curr_trig = device_dict["fc_curr_sour"]
	fngen_fieldcoil_curr_trig = device_dict["fc_curr_sour"]
	fngen_ext_trigger = device_dict["ext_trig"]
	nanovoltmeter = device_dict["nanovolt"]
	current = magnet.take_datapoint()
	time_prev = time.time()
	fieldcoils_high = False
	ext_trig_on = False
	while current > p108.MAGNET_CURRENT_MARGIN:
		if time.time() - time_prev >= p108.SAMPLING_DELAY_MAGNET:
			time_prev = time.time()
			current = magnet.take_datapoint()
			sys.stdout.write('Ramping magnet: ' + str(current) + ' A   ')
			sys.stdout.write('\r')
			sys.stdout.flush()
		if current / p108.MAGNET_CURRENT_RAMP_RATE <= p108.FIELDCOIL_RESET_TIME and fieldcoil_bool and not fieldcoils_high:
			fieldcoils_high = True
			print("Driving field coils high")
			fngen_fieldcoil_curr_trig.set_fc_current(p108.FIELDCOIL_TARGET_CURRENT)
		if current / p108.MAGNET_CURRENT_RAMP_RATE <= p108.FIELDCOIL_INIT_DELAY and fieldcoil_bool and not ext_trig_on:
			ext_trig_on = True
			print("\nTurning on external trigger")
			start_time = time.time()
			for device in device_dict:
				if device_dict[device].needs_init():
					device_dict[device].prev_data_start_time = start_time
			fngen_ext_trigger.write(p108.FNGEN_TRIG_COMMAND)
	if fieldcoil_bool:
		print("Driving field coils low")
		fngen_fieldcoil_curr_trig.set_fc_current(0)
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