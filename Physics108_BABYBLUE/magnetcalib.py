import visa
import time
import sys

identifier = 'TIMECONTROL'

enable_5 = True					# Whether or not the magnet current source is connected

magnet_5_address = 'GPIB0::5::INSTR'  # magnet currnet source
"VSET 5V"
"IOUT?"

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())

	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	file = open("C:/Users/Student/physics108/Physics108_BABYBLUE/data/" + identifier + timestamp + ".txt", "w")

	column_label = 'Counter,'
	column_label += 'Time(s),'

 	if enable_5:
		magnet_5 = rm.open_resource(magnet_5_address)
		column_label += 'Magnet Current(mA)'        

		magnet_5.write("TRIG:SOUR BUS")		

	# Write column labels in the log file
	print(column_label)
	column_label += '\n'
	file.write(column_label)

	start_time = time.time()

	counter = 0
	while(True):
		data_string = str(counter)        
		current_time = time.time() - start_time
		data_string += ','+str(current_time)         
            
		if enable_5:
			magnet_5_voltage = magnet_5.write("")
			multi_5_voltage = multimeter_5.query('MEAS?')
			multi_5_current = float(multi_5_voltage) / magnet_sense_resistor * 1E3        
			data_string += ',' + str(multi_5_current.strip('\n'))                
		
		sys.stdout.write(data_string)
		sys.stdout.write('\r\r')
		sys.stdout.flush()
		data_string += '\n'
		
		file.write(data_string)
		counter += 1
	
if __name__ == "__main__":
    main()