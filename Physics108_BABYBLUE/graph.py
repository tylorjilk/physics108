# To install matplotlib may have to use the following function:
# python -m pip install -U matplotlib

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import sys

def main():
	df = pd.read_csv(sys.argv[1])
	time = df['Time (s)']
	voltage = df['Mod Coil Voltage (V)']
	current = df['Calculated Mod Coil Current (A)']
	plt.plot(current, voltage, 'bo')
	plt.plot(np.unique(current), np.poly1d(np.polyfit(current, voltage, 1))(np.unique(current)))
	print(np.poly1d(np.polyfit(current, voltage, 1)))
	plt.text(-0.000018,-0.0000016, str(np.poly1d(np.polyfit(current, voltage, 1))))
	plt.xlabel('Current (A)')
	plt.ylabel('Voltage (V)')
	plt.title('V-I Curve of a Resistor Using 4-Terminal Measurement')
	plt.show()

if __name__ == "__main__":
    main()