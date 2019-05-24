# To install matplotlib may have to use the following function:
# python -m pip install -U matplotlib

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

def sincurve(x, A, T, phi, b):
    return A*np.sin(2*np.pi/T*x+phi)+b

def main():
	df = pd.read_csv(sys.argv[1])
	if len(sys.argv > 2):
        option = sys.argv[2]
        
	counter = df['Counter,']
	time = df['Time(s),']
	squid_voltage = df['SQUID Voltage(V),']
	mod_current = df['Mod Coil Current(uA),']
	pickup_loop_current = df['Pickup Loop Current(uA),']
	temp_voltage = df['Temp Probe Voltage(V),']
	field_coil_current = df['Field Coil Current(mA),']
	magnet_current = df['Magnet Current(mA)']
    
	squid_voltage = np.absolute(np.array(squid_voltage))
	mod_current = np.absolute(np.array(mod_current))
	
	plt.plot(mod_current, squid_voltage, '.')
	plt.xlabel('Mod Current (uA)')
	plt.ylabel('SQUID Voltage (V)')
	mean_pickup_loop_current = "{:.2E}".format(np.average(pickup_loop_current))
	mean_temp_voltage = "{:.4E}".format(np.average(temp_voltage))
	plt.title('Squid Voltage vs Mod Current at pickup loop current ' \
           + mean_pickup_loop_current + 'uA, temperature voltage ' + mean_temp_voltage +'V')
    
    x_axis = np.linspace(0, np.max(mod_current))
    if option=='fit':
        coeff, covar = curve_fit(sincurve, mod_current, squid_voltage, p0=[4, 140, 0, 0])
        plt.plot(x_axis, sincurve(x_axis, coeff) ,'-')
        
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