# To install matplotlib may have to use the following function:
# python -m pip install -U matplotlib

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import sys

def main():
	df = pd.read_csv(sys.argv[1])
	time = df['Time (s)']
	counter = df['Counter']
	squid_voltage = df['SQUID voltage (V)']	
	mod_current = df['Calculated Mod Coil Current (uA)']	
	squid_loop_current = df['Calculated Squid Current (uA)']
	temp_voltage = df['Temp Probe Voltage (V)']



	#squid_voltage = df['SQUID voltage (V)']
	#mod_voltage = df['Mod Coil Voltage (V)']
	#mod_current = df['Calculated Mod Coil Current (uA)']
	#squid_loop_voltage = df['SQUID Loop Voltage (V)']
	#squid_loop_current = df['Calculated Squid Current (uA)']
	#temp_voltage = df['Temp Probe Voltage (V)']
	
	plt.plot(mod_current, squid_voltage, 'bo')
	plt.xlabel('Mod Current (uA)')
	plt.ylabel('SQUID Voltage (V)')
	squid_avg_current = "{:.2E}".format(np.average(squid_loop_current))
	plt.title('Squid voltage vs mod current at ' + squid_avg_current + ' uA')
	plt.show()

if __name__ == "__main__":
    main()