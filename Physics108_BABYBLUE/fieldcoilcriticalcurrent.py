import visa
import time
import sys

identifier = 'FIELDCOILCRITICALCURRENT'

fc_sense_resistor = 50.0
pickup_sense_resistor = 101.5
enable_3 = True
fieldcoil_current_3_address = 'GPIB0::3::INSTR' 	# fieldcoil current multimeter
enable_9 = True
fieldcoil_voltage_9_address = 'GPIB0::9::INSTR' 	# fieldcoil votlage multimeter
enable_22 = True
nanovolt_22_address = 'GPIB0::22::INSTR'	# nanovolt meter
enable_4 = True
pickup_4_address = 'GPIB0::22::INSTR'	# nanovolt meter

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/data/" + identifier + timestamp + ".txt"
	file = open(filename, "w")
	
	column_label = 'Counter,'
	column_label += 'Time(s),' 
	column_label += 'Field Coil Current(mA),'
	column_label += 'Field Coil Voltage(mV),'
	column_label += 'SQUID Voltage(uV),'
	column_label += 'Pickup Loop Current(uA),'
	column_label += '\n'
	file.write(column_label)
	
	if enable_3:
		fieldcoil_current_3 = rm.open_resource(fieldcoil_current_3_address)	
	if enable_9:
		fieldcoil_voltage_9 = rm.open_resource(fieldcoil_voltage_9_address)
	if enable_22:
		nanovolt_meter_22 = rm.open_resource(nanovolt_22_address)		
		nanovolt_meter_22.write("*RST")
		nanovolt_meter_22.write("CONF:VOLT:DIFF")
	if enable_4:
		pickup_current_4 = rm.open_resource(pickup_4_address)
		
	counter = 0
	start_time = time.time()
	while(True):
		data_string = str(counter)        
		current_time = time.time() - start_time
		data_string += ','+str(current_time) 
		
		data_string += ','
		if enable_3:
			curr = float(fieldcoil_current_3.query("MEAS:VOLT:DC?"))/fc_sense_resistor*1E3
			data_string += str(curr) 
		
		data_string += ','
		if enable_9:
			volt = float(fieldcoil_voltage_9.query("MEAS:VOLT:DC?"))*1E3
			data_string += str(volt) 	
			
		data_string += ','
		if enable_22:
			nanovolt_meter_22.write("INIT")
			nanovolt_meter_22.write("*TRG")
			data_string += str(float(nanovolt_meter_22.query("FETC?").strip('\n'))*1E6) 
		
		data_string += ','	
		if enable_4:
			curr = float(pickup_current_4.query("MEAS:VOLT:DC?"))/pickup_sense_resistor*1E6
			data_string += str(curr) 
			
		sys.stdout.write(data_string)
		sys.stdout.write('\r\r')
		sys.stdout.flush()
		data_string += '\n'		
		file.write(data_string)
		
		counter += 1
		
	file.close()
	
	df = pd.read_csv(filename, delimiter=',')
	x_cur = df['Field Coil Current(mA)']
	y_vol = df['Field Coil Voltage(mV)']
	x_cur = np.absolute(np.array(x_cur))
	y_vol = np.absolute(np.array(y_vol))
	plt.plot(x_cur, y_vol, '.')
	plt.xlabel('Field Coil Current(mA)')
	plt.ylabel('Field Coil Voltage(mV)')
	plt.show()
	
if __name__ == "__main__":
    main()			
		
			
			
			
			
			
			
	
		
	