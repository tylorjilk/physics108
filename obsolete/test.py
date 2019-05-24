import physics108 as p108
import signal
import visa
import time
import sys

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	#print('Resetting devices...')
	#clear_devices()
	#print('Saving data...')
	#save_data()
	print(multimeter_temperature.get_complete_data())
	print('Goodbye')
	sys.exit(0)
	
def main():
	signal.signal(signal.SIGINT, signal_handler)
	rm = visa.ResourceManager()
	trigger_generator = p108.Device(p108.EXT_TRIGGER_ADDRESS, rm, True)
	global multimeter_temperature
	multimeter_temperature = p108.Device(p108.TEMPERATURE_ADDRESS, rm, True)
	trigger_generator.write(p108.FNGEN_ZERO_COMMAND)
	
	multimeter_temperature.write('CONF:VOLT')
	multimeter_temperature.write('TRIG:SOUR EXT')
	multimeter_temperature.write('TRIG:COUN 25')
	#multimeter_temperature.write('TRIG:DEL 0')
	multimeter_temperature.init()
	
	time.sleep(0.2)
	trigger_generator.write(p108.FNGEN_TRIG_COMMAND)
	init_time = time.time()
	prev_data_time = init_time
	time.sleep(5)
	multimeter_temperature.fetc_data()
	print(multimeter_temperature.get_complete_data())

	"""
	while(True):
		if time.time() - prev_data_time >= 2:
			trigger_generator.write(p108.FNGEN_ZERO_COMMAND)
			multimeter_temperature.fetc_data()
			multimeter_temperature.init()
			trigger_generator.write(p108.FNGEN_TRIG_COMMAND)
			prev_data_time = time.time()
			"""


if __name__ == "__main__":
    main()