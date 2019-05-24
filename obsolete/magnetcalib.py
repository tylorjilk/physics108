import visa
import time
import sys

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

identifier = 'TIMECONTROL'

enable_5 = True				# Whether or not the magnet current source is connected

magnet_5_address = 'GPIB0::5::INSTR'  # magnet currnet source

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())

	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/data/" + identifier + timestamp + ".txt"
	file = open(filename, "w")

	column_label = 'Counter,'
	column_label += 'Time(s),'   	

	start_time = time.time()
	current_time = time.time() - start_time
	
	if enable_5:
		magnet_5 = rm.open_resource(magnet_5_address)
		column_label += 'Magnet Current(A)'    
		magnet_5_voltage = magnet_5.write("VSET 0.1 V")
		
	# Write column labels in the log file
	print(column_label)
	column_label += '\n'
	file.write(column_label)

	counter = 0
	magnet_5_current = 0
	while(current_time < 3 and magnet_5_current < 1):
		data_string = str(counter)        
		current_time = time.time() - start_time
		data_string += ','+str(current_time)         
            
		if enable_5:
			magnet_5_current = float(magnet_5.query('IOUT?')[4:])
			data_string += ',' + str(magnet_5_current)                
		
		sys.stdout.write(data_string)
		sys.stdout.write('\r\r')
		sys.stdout.flush()
		data_string += '\n'
		
		file.write(data_string)
		counter += 1
		
	magnet_5_voltage = magnet_5.write("VSET 0 V")
	
	file.close()
	
	print(filename)
	df = pd.read_csv(filename, delimiter=',')
	counter = df['Counter']
	x_time = df['Time(s)']
	y_magnet_current = df['Magnet Current(A)']
	y_magnet_current = np.absolute(np.array(y_magnet_current))
	plt.plot(x_time, y_magnet_current, '.')
	plt.xlabel('Time (s)')
	plt.ylabel('Magnet Current(A)')
	
	#fit = np.polyfit(x_time, y_magnet_current, 1)
	#print('inductance = '+str(0.1/fit[0])+'H')
	#p = np.poly1d(fit)
	#plt.plot(x_time, p(x_time), '-')
	
	plt.show()
	
	
if __name__ == "__main__":
    main()