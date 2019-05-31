import visa
import time
import sys

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

identifier = 'comeback'

magnet_constant = 0.10238 #field constant of magnet, T/A
magnet_ramp_rate = 0.03 #ramp rate of magnet, T/s
current_ramp_rate = 0.3 #magnet_ramp_rate/magnet_constant*0.1
current_target = 1.5

fc_sense_resistor = 50.0
mod_sense_resistor = 9.13E3
mod_bfr_resistor = 15.0E3
pickup_sense_resistor = 101.5

init_enable_2 = True
temp_voltage_2_address = 'GPIB0::2::INSTR'		# temperature sensor
init_enable_5 = False		# Whether or not the magnet current source is connected
magnet_5_address = 'GPIB0::5::INSTR'  # magnet current source
init_enable_7 = False
fieldcoil_trigger_7_address = 'GPIB0::7::INSTR' 	# fieldcoil trigger
init_enable_3 = False
fieldcoil_current_3_address = 'GPIB0::3::INSTR' 	# fieldcoil current multimeter
init_enable_22 = True
nanovolt_22_address = 'GPIB0::22::INSTR'	# nanovolt meter
init_enable_8 = True
modcoil_trigger_8_address = 'GPIB0::8::INSTR' 		# modcoil trigger
init_enable_9 = True
modcoil_current_9_address = 'GPIB0::9::INSTR' 		# modcoil current multimeter
init_enable_4 = True
pickup_current_4_address = 'GPIB0::4::INSTR' 		# pickup loop current multimeter


option = 1	# 0: produce t-V	1: produce Imod - V
nanovolt_meas_time = 60*60*10
target_mod_cur = 47E-6 #87.82E-6			# option 0
max_target_mod_cur = 250.0E-6		# option 1
fitting = True	# produce Imod-V to sine curve



def print_out(file, counter):
	data_string = str(counter)        
	current_time = time.time() - start_time
	data_string += ','+str(current_time) 
	
	data_string += ','
	if enable_2:
		data_string += str(temp_voltage_2.query("MEAS:VOLT:DC?")).strip('\n')
	
	data_string += ','
	if enable_5:
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		data_string += str(curr) 
		
	data_string += ','
	if enable_3:
		curr = float(fieldcoil_current_3.query("MEAS:VOLT:DC?"))/fc_sense_resistor*1E3
		data_string += str(curr) 
		
	data_string += ','
	if enable_22:
		nanovolt_meter_22.write("INIT")
		nanovolt_meter_22.write("*TRG")
		data_string += str(float(nanovolt_meter_22.query("FETC?").strip('\n'))*1E6) 	
		
	data_string += ','	
	if enable_9: #and option==1:
		curr = float(modcoil_current_9.query("MEAS:VOLT:DC?"))/mod_sense_resistor*1E6
		data_string += str(curr) 
		
	data_string += ','
	if enable_4: #and option == 1:
		curr = float(pickup_current_4.query("MEAS:VOLT:DC?"))/pickup_sense_resistor*1E6
		data_string += str(curr) 
		
		
	sys.stdout.write(data_string)
	sys.stdout.write('\r\r')
	sys.stdout.flush()
	data_string += '\n'		
	file.write(data_string)
	

def magnet():
	counter = 0
	curr = 0
	current_time = time.time() - start_time
	
	#ramp up
	magnet_5.write("CONF:CURR:PROG "+str(current_target))
	magnet_5.write("RAMP")
	while(curr < current_target-1E-2):       
		print_out(file1, counter)
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		time.sleep(0.1)
		counter += 1
	#magnet_5.write("PAUSE")
	
	stage_time = time.time() 
	current_stage_time = time.time() - stage_time
	while(current_stage_time < 5):
		print_out(file1, counter)
		current_stage_time = time.time() - stage_time
		time.sleep(0.1)
		counter += 1
	
	#ramp down
	#magnet_5.write("CONF:CURR:PROG 0.0") 
	magnet_5.write("ZERO") # we might want ZERO
	while(curr > 1E-2):
		print_out(file1, counter)
		curr = float(magnet_5.query("CURR:MAG?").lstrip('\x00'))
		time.sleep(0.1)
		counter += 1
	#magnet_5.write("ZERO")	
	
	file1.write('commanded current ramp rate: '+str(current_ramp_rate)+' A/s\n')
	file1.write('commanded target current: '+str(current_target)+' A\n')
	return 0
		
		
def fieldcoil():
	counter = 0
	new_start_time = time.time()
	current_stage_time = time.time() - new_start_time
	
	fieldcoil_trigger_7.write("OFFS 1")
	while float(current_stage_time) < 1:    
		current_stage_time = time.time() - new_start_time
		print_out(file1)
		time.sleep(0.1)
		counter += 1
	
	fieldcoil_trigger_7.write("OFFS 0")	
	return 0
		
		
def nanovolt():
	# option 0: not changing mod coil current (produce t-V graph)
	# option 1: change mod coil current (produce Imod-V graph)
	new_start_time = time.time()
	current_stage_time = time.time() - new_start_time
	
	counter = 0
	modcoil_trigger_8.write("OFFS 0")
	
	if option == 0:
		mod_vol = target_mod_cur*(mod_bfr_resistor + mod_sense_resistor)/2.0
		modcoil_trigger_8.write("OFFS "+str(mod_vol))
		while(float(current_stage_time) < nanovolt_meas_time):
			current_stage_time = time.time() - new_start_time
			print_out(file2, counter)
		if enable_9:
			modcur = float(modcoil_current_9.query("MEAS:VOLT:DC?"))/mod_sense_resistor*1E6
			file2.write('mod coil current: '+str(modcur)+' uA\n')
		if enable_4:
			pickupcur = float(pickup_current_4.query("MEAS:VOLT:DC?"))/pickup_sense_resistor*1E6
			file2.write('pickup loop current: '+str(pickupcur)+' uA\n')
		modcoil_trigger_8.write("OFFS 0")
		
			
	if option == 1:
		for mod_cur_now in np.arange(0, max_target_mod_cur, 2.0E-6):
			mod_vol = mod_cur_now*(mod_bfr_resistor + mod_sense_resistor)/2.0
			if mod_vol < 5:
				modcoil_trigger_8.write("OFFS "+str(mod_vol))
				print_out(file2, counter)
				#print_out(file2, counter) 
				#print_out(file2, counter) 		
				counter += 1
		modcoil_trigger_8.write("OFFS 0")
	return 0
		

def main():
	rm = visa.ResourceManager()
	print(rm.list_resources())
	
	global temp_voltage_2
	global magnet_5
	global fieldcoil_trigger_7
	global fieldcoil_current_3
	global nanovolt_meter_22
	global modcoil_trigger_8
	global modcoil_current_9
	global pickup_current_4
	global file1, file2
	global filename1, filename2
	global start_time
	global enable_2, enable_5, enable_7, enable_3, enable_22, enable_8, enable_9, enable_4
	
	enable_2 = init_enable_2
	enable_5 = init_enable_5
	enable_7 = init_enable_7
	enable_3 = init_enable_3
	enable_22 = init_enable_22
	enable_8 = init_enable_8
	enable_9 = init_enable_9
	enable_4 = init_enable_4

	# Make a new log file with time appended to name
	init_time = time.localtime()
	timestamp = str(init_time.tm_hour) + str(init_time.tm_min) + str(init_time.tm_sec)
	filename1 = "C:/Users/Student/physics108/data/" + identifier + '_prelim' + timestamp + ".txt"		# ~ field coil heating
	filename2 = "C:/Users/Student/physics108/data/" + identifier + '_data' + timestamp + ".txt"		# only voltage measurement
	file1 = open(filename1, "w")
	file2 = open(filename2, "w")

	column_label = 'Counter,'
	column_label += 'Time(s),'  
	column_label += 'Temperature Voltage(V),'
	column_label += 'Magnet Current(A),' 	
	column_label += 'Field Coil Current(mA),' 
	column_label += 'SQUID Voltage(uV),'
	column_label += 'Mod Current(uA),'
	column_label += 'Pickup Loop Current(uA),'
	
	if init_enable_2:
		temp_voltage_2 = rm.open_resource(temp_voltage_2_address)
	if init_enable_5:
		magnet_5 = rm.open_resource(magnet_5_address)
		magnet_5.write("CONF:RAMP:RATE:CURR " + str(current_ramp_rate) + " A/s")
		
		print("ramp_rate: "+magnet_5.query("RAMP:RATE:CURR?"))
		#magnet_5.write("CONF:VOLT:LIM 5")
		print("Voltage Limit: "+magnet_5.query("VOLT:LIM?")+" V")
	if init_enable_7:
		fieldcoil_trigger_7 = rm.open_resource(fieldcoil_trigger_7_address)
	if init_enable_3:
		fieldcoil_current_3 = rm.open_resource(fieldcoil_current_3_address)
	if init_enable_22:
		nanovolt_meter_22 = rm.open_resource(nanovolt_22_address)
		nanovolt_meter_22.write("*RST")
		nanovolt_meter_22.write("CONF:VOLT:DIFF")
		#nanovolt_meter_22.write("SENS1:VOLT:NPLC 0.2")  #optimal value for max sampling rate & precision
		##nanovolt_meter_22.write("SENS1:VOLT:RES MIN")
		#nanovolt_meter_22.write("SENS2:VOLT:NPLC 0.2")	# trigger rate 2.2Hz
		##nanovolt_meter_22.write("SENS2:VOLT:RES MIN")
		print('NPLC: '+str(nanovolt_meter_22.query("SENS1:VOLT:NPLC?")))
		print('RES: '+str(nanovolt_meter_22.query("SENS1:VOLT:RES?")))
		#nanovolt_meter_22.write("TRIG:SOUR EXT")
		#nanovolt_meter_22.write("TRIG:DEL 0")
		#nanovolt_meter_22.write("SAMP:COUN 1")	
	if init_enable_8:
		modcoil_trigger_8 = rm.open_resource(modcoil_trigger_8_address)
	if init_enable_9:
		modcoil_current_9 = rm.open_resource(modcoil_current_9_address)
	if init_enable_4:
		pickup_current_4 = rm.open_resource(pickup_current_4_address)
	
		
	print(column_label)
	column_label += '\n'
	file1.write(column_label)
	file2.write(column_label)
	start_time = time.time()

	
	if enable_5:	
		magnet()
		file1.write('\n')
		
	if option == 1: enable_5 = False
	if enable_7 and enable_3:
		fieldcoil()

	file1.close()
	print(filename1)
		
	if option == 1: enable_3 = False
	if init_enable_22:
		nanovolt()
		
		
	file2.close()
	print(filename2)
	
	df1 = pd.read_csv(filename1, delimiter=',')
	df2 = pd.read_csv(filename2, delimiter=',')
	if init_enable_5:
		x_time = df1['Time(s)']
		y_magnet_current = df1['Magnet Current(A)']
		y_magnet_current = np.absolute(np.array(y_magnet_current))
		plt.plot(x_time, y_magnet_current, '.')
		plt.xlabel('Time(s)')
		plt.ylabel('Magnet Current(A)')
		plt.title('commanded current ramp rate: '+str(current_ramp_rate)+'A/s, commanded target current: '+str(current_ramp_rate)+'A')
		plt.show()
	
	if init_enable_22 and option == 0:
		x_time = df2['Time(s)']
		y_nanovolt = df2['SQUID Voltage(uV)']
		y_nanovolt = np.absolute(np.array(y_nanovolt))
		plt.plot(x_time, y_nanovolt, '.')
		plt.xlabel('Time(s)')
		plt.ylabel('SQUID Voltage(uV)')
		plt.show()
		
	elif init_enable_22 and option == 1:
		x_modcur = df2['Mod Current(uA)']
		x_modcur = np.absolute(np.array(x_modcur))
		y_nanovolt = df2['SQUID Voltage(uV)']
		y_nanovolt = np.absolute(np.array(y_nanovolt))
		
		plt.plot(x_modcur, y_nanovolt, '.')
		plt.xlabel('Mod Current(uA)')
		plt.ylabel('SQUID Voltage(uV)')
		
		if fitting:
			def sincurve(x, A, T, phi, b):
				return A*np.sin(2*np.pi/T*x+phi)+b
				
			x_axis = np.linspace(0, max_target_mod_cur*1E6)
			coeff, covar = curve_fit(sincurve, x_modcur, y_nanovolt, p0=[4, 140, 0, 0])
			plt.plot(x_axis, sincurve(x_axis, coeff[0], coeff[1], coeff[2], coeff[3]) ,'-')
		
			sensitivity = coeff[0]*2*np.pi/coeff[1]/(14E-12)*2.07E-15*1E6  #uV per flux quantum
			sweetspot = -coeff[2]*coeff[1]/(2*np.pi)
			while sweetspot < 0:
				sweetspot += coeff[1]
			while sweetspot > coeff[1]:
				sweetspot -= coeff[1]
			
			print('Sweetspot = '+str(sweetspot)+'uA '+'Max Sensitivity = '+str(sensitivity)+'uV/Phi0')
		
		plt.show()
		

			

if __name__ == "__main__":
    main()