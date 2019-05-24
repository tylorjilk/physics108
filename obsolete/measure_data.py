import visa
import time
import sys

identifier = 'DATA'

enable_22 = True			# Whether or not the nanovolt meter is connected
enable_2 = True				# Whether or not the mod coil multimeter is connected
enable_3 = True					# Whether or not the squid pickup multimeter is connected
enable_4 = True					# Whether or not the temp probe multimeter is connected
mod_sense_resistor = 101.5 		# Value of mod coil sense resistor in ohms
squid_sense_resistor = 101.5 	# Value of squid pickup sense resister in ohms
fc_sense_resistor = ?
magnet_sense_resistor = ?

nanovolt_22_address = 'GPIB0::22::INSTR'	# nanovolt meter
multimeter_2_address = 'GPIB0::2::INSTR'	# mod coil multimeter
multimeter_3_address = 'GPIB0::3::INSTR'	# squid pickup multimeter
multimeter_4_address = 'GPIB0::4::INSTR'	# temp probe multimeter
multimeter_?_address = 'GPIB0::?::INSTR'    # field coil multimeter
multimeter_??_address = 'GPIB0::??::INSTR'  # magnet multimeter



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

	if enable_2:
		multimeter_2 = rm.open_resource(multimeter_2_address)
		#column_label += ', Mod Coil Voltage (V) '
		column_label += 'Mod Coil Current(uA),'
	
	if enable_3:
		multimeter_3 = rm.open_resource(multimeter_3_address)
		#column_label += ', SQUID Loop Voltage (V) '
		column_label += 'Pickup Loop Current(uA),'
		
	if enable_4:
		multimeter_4 = rm.open_resource(multimeter_4_address)
		column_label += 'Temp Probe Voltage(V),'
        
 	if enable_?:
		multimeter_? = rm.open_resource(multimeter_?_address)
		column_label += 'Field Coil Current(mA),'  
        
 	if enable_??:
		multimeter_?? = rm.open_resource(multimeter_??_address)
		column_label += 'Magnet Current(mA)'          

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
			nano_22_voltage = nanovolt_meter_22.query('MEAS:DIFF?')
			nano_22_voltage = float(nano_22_voltage) * 1E6            
			data_string += ',' + str(nano_22_voltage.strip('\n'))

		if enable_2:
			multi_2_voltage = multimeter_2.query('MEAS?')
			#data_string += ',' + str(multi_2_voltage.strip('\n'))
			multi_2_current = float(multi_2_voltage) / mod_sense_resistor * 1E6
			data_string += ',' + str(multi_2_current)
			
		if enable_3:
			multi_3_voltage = multimeter_3.query('MEAS?')
			#data_string += ',' + str(multi_3_voltage.strip('\n'))
			multi_3_current = float(multi_3_voltage) / squid_sense_resistor * 1E6
			data_string += ',' + str(multi_3_current)
		
		if enable_4:
			multi_4_voltage = multimeter_4.query('MEAS?')
			data_string += ',' + str(multi_4_voltage.strip('\n'))
            
		if enable_?:
			multi_?_voltage = multimeter_?.query('MEAS?')
			multi_?_current = float(multi_?_voltage) / fc_sense_resistor * 1E3        
			data_string += ',' + str(multi_?_current.strip('\n'))    
            
		if enable_??:
			multi_??_voltage = multimeter_??.query('MEAS?')
			multi_??_current = float(multi_??_voltage) / magnet_sense_resistor * 1E3        
			data_string += ',' + str(multi_??_current.strip('\n'))                
		
		sys.stdout.write(data_string)
		sys.stdout.write('\r\r')
		sys.stdout.flush()
		data_string += '\n'
		
		file.write(data_string)
		counter += 1
	
if __name__ == "__main__":
    main()