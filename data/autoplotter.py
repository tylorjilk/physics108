import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys

filename = ''
	
if len(sys.argv) == 2:
	filename = str(sys.argv[1])
else:
	sys.exit()

data = pd.read_csv(filename, delimiter=',')
	
times = np.array(pd.DataFrame(data, columns= ['timestamp']))
pickup_voltages = np.absolute(np.array(pd.DataFrame(data, columns= ['SQUID_Volt(V)']))*1E6)
pickup_voltages = pickup_voltages[~pd.isnull(pickup_voltages)]

plt.plot(times[5:], pickup_voltages[5:], '.')
plt.xlabel('Time(s)')
plt.ylabel('SQUID Voltage(uV)')
plt.show()
