import visa
import time
import sys

identifier = 'DATA'

enable_22 = True			# Whether or not the nanovolt meter is connected

nanovolt_22_address = 'GPIB0::22::INSTR'	# nanovolt meter



def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())

	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	file = open("C:/Users/Student/physics108/Physics108_BABYBLUE/data/" + identifier + timestamp + ".txt", "w")

	column_label = 'Counter,'
	column_label += 'Time(s),'

	if enable_22:
		nanovolt_meter_22 = rm.open_resource(nanovolt_22_address)
		column_label += 'SQUID Voltage(uV),'
		nanovolt_meter_22.write("*RST")
		nanovolt_meter_22.write("CONF:VOLT:DIFF")
		nanovolt_meter_22.write("SENS1:VOLT:NPLC 0.2")  #optimal value for max sampling rate & precision
		#nanovolt_meter_22.write("SENS1:VOLT:RES MIN")
		nanovolt_meter_22.write("SENS2:VOLT:NPLC 0.2")	# trigger rate 2.2Hz
		#nanovolt_meter_22.write("SENS2:VOLT:RES MIN")
		print('NPLC: '+str(nanovolt_meter_22.query("SENS1:VOLT:NPLC?")))
		print('RES: '+str(nanovolt_meter_22.query("SENS1:VOLT:RES?")))
		nanovolt_meter_22.write("TRIG:SOUR EXT")
		nanovolt_meter_22.write("TRIG:DEL 0")
		nanovolt_meter_22.write("SAMP:COUN 1")
		


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
		
		if enable_22:
			nanovolt_meter_22.write("INIT")
			nanovolt_meter_22.write("*TRG")
			data_string += ','+str(nanovolt_meter_22.query("FETC?").strip('\n'))
			
			#nano_22_voltage = nanovolt_meter_22.query('MEAS:DIFF?')
			#nano_22_voltage = float(nano_22_voltage) * 1E6            
			#data_string += ',' + str(nano_22_voltage.strip('\n'))             
		
		sys.stdout.write(data_string)
		sys.stdout.write('\r\r')
		sys.stdout.flush()
		data_string += '\n'
		
		file.write(data_string)
		counter += 1
	
if __name__ == "__main__":
    main()