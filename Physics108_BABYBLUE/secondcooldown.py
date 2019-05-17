import visa
import time
import sys

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

identifier = 'SECONDCOOLDOWN'

magnet_constant = 0.10238 #field constant of magnet, T/A
magnet_ramp_rate = 0.03 #ramp rate of magnet, T/s
current_ramp_rate = magnet_ramp_rate/magnet_constant

fc_sense_resistor = 50.0

enable_5 = True		# Whether or not the magnet current source is connected
magnet_5_address = 'GPIB0::5::INSTR'  # magnet currnet source
enable_7 = True
fieldcoil_trigger_7_address = 'GPIB0::7::INSTR' 
enable_3 = True
fieldcoil_current_3_address = 'GPIB0::3::INSTR' 
enable_22 = True
nanovolt_22_address = 'GPIB0::22::INSTR'	# nanovolt meter


def print_out(counter):
	data_string = str(counter)        
	current_time = time.time() - start_time
	data_string += ','+str(current_time) 
	if enable_5:
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		data_string += ',' + str(curr) 
	else:
		data_string += ','
		
	if enable_7 and enable_3:
		curr = float(fieldcoil_current_3.query("MEAS:VOLT:DC?"))/fc_sense_resistor*1E3
		data_string += ',' + str(curr) 
	else:
		data_string += ','
		
	if enable_22:
		nanovolt_meter_22.write("INIT")
		nanovolt_meter_22.write("*TRG")
		data_string += ','+str(nanovolt_meter_22.query("FETC?").strip('\n')) 
	else:
		data_string += ','
		
	sys.stdout.write(data_string)
	sys.stdout.write('\r\r')
	sys.stdout.flush()
	data_string += '\n'		
	file.write(data_string)
	

def magnet():
	magnet_5.write("CONF:RAMP:RATE:CURR " + str(current_ramp_rate) + " A/s")
	print("ramp_rate: "+magnet_5.query("RAMP:RATE:CURR?"))
	#magnet_5.write("CONF:VOLT:LIM 5")
	print("Voltage Limit: "+magnet_5.query("VOLT:LIM?"))
	counter = 0
	
	#ramp up
	magnet_5.write("CONF:CURR:PROG 5.0") # we might want 1.5
	magnet_5.write("UP")
	curr = 0
	current_time = time.time() - start_time
	while(curr < 1.5):       
		print_out(counter)
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		time.sleep(0.1)
		counter += 1
	magnet_5.write("PAUSE")
	
	#ramp down
	magnet_5.write("CONF:CURR:PROG -5.0") # we might want zero
	magnet_5.write("DOWN") # we might want ZERO
	while(curr > 0):
		print_out(counter)
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		time.sleep(0.1)
		counter += 1
	magnet_5.write("ZERO")	
	return 0
		
		
def fieldcoil():
	counter = 0
	new_start_time = time.time()
	current_stage_time = time.time() - new_start_time
	
	fieldcoil_trigger_7.write("AMPL 1VP")
	data_string=''
	while float(current_stage_time) < 1:    
		print(current_stage_time)
		current_stage_time = time.time() - new_start_time
		print_out(counter)
		time.sleep(0.1)
		counter += 1
	
	fieldcoil_trigger_7.write("AMPL 0VP")	
	return 0
		
		
def nanovolt():
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
	
	counter = 0
	while(True):
		print_out(counter)
		counter += 1
		

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())
	
	global magnet_5
	global fieldcoil_trigger_7
	global fieldcoil_current_3
	global nanovolt_meter_22
	global filename
	global file
	global start_time

	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename = "C:/Users/Student/physics108/Physics108_BABYBLUE/data/" + identifier + timestamp + ".txt"
	file = open(filename, "w")

	column_label = 'Counter,'
	column_label += 'Time(s),'  
	column_label += 'Magnet Current(A),' 	
	column_label += 'Field Coil Current(mA),' 
	column_label += 'SQUID Voltage(uV),'
	if enable_5:
		magnet_5 = rm.open_resource(magnet_5_address)
	if enable_7:
		fieldcoil_trigger_7 = rm.open_resource(fieldcoil_trigger_7_address)
	if enable_3:
		fieldcoil_current_3 = rm.open_resource(fieldcoil_current_3_address)
	if enable_22:
		nanovolt_meter_22 = rm.open_resource(nanovolt_22_address)
	
		
	print(column_label)
	column_label += '\n'
	file.write(column_label)
	start_time = time.time()

	
	if enable_5:	
		magnet()
		file.write('\n')
	if enable_7 and enable_3:
		fieldcoil()
		file.write('\n')
	if enable_22:
		nanovolt()
		
		
	file.close()
	print(filename)
	
	if enable_5:
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