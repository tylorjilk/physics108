import signal
import visa
import time
import sys, os
import msvcrt
import physics108 as p108

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	print('Goodbye')
	sys.exit(0)
	
def main():
	signal.signal(signal.SIGINT, signal_handler)
	rm = visa.ResourceManager()
	multimeter = rm.open_resource('GPIB0::3::INSTR')
	multimeter.write('*CLS')
	multimeter.write('*RST')
	multimeter.write('CONF:VOLT:DC')
	#multimeter.write('TRIG:COUN 2')# + str(SAMPLING_NUM_POINTS))
	multimeter.write('TRIG:SOUR EXT')
	multimeter.write('INIT')
	time.sleep(1)
	print(multimeter.query('FETC?'))
			
	"""
	multimeter_temperature		= p108.Device_34401A(	p108.TEMPERATURE_ADDRESS, 			p108.TEMPERATURE_COLUMN_HEADING,	rm,	True	)
	multimeter_temperature.configure(time.time())
	prev_data_time = time.time()
	time.sleep(1)
	print(multimeter_temperature.query('TRIG:COUN?'))
	while True:
		if time.time() - prev_data_time >= 2:
			sys.stdout.write('Measuring data...')
			print(multimeter_temperature.fetc_data())
			prev_data_time = time.time()
			multimeter_temperature.init(time.time())
			
			sys.stdout.write('\r')
			sys.stdout.flush()
			time.sleep(p108.INIT_TIME_DELAY)
	"""

if __name__ == "__main__":
    main()