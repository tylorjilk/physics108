import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys

def sincurve(x, A, T, phi, a, b):
    return A*np.sin(2*np.pi/T*x+phi)+a*x+b

filename = ''
	
if len(sys.argv) == 2:
	filename = str(sys.argv[1])
else:
	sys.exit()
	
data = pd.read_csv(filename, delimiter=',')
#data = pd.read_csv(r'./data/3rd_cooldown/mod_coil_44-4uASQUID_sweep_185137.csv', delimiter=',')
modcoil_currents = np.absolute(np.array(pd.DataFrame(data, columns= ['MOD_CURR(A)']))/9.13E3*1E6)
pickup_voltages = np.absolute(np.array(pd.DataFrame(data, columns= ['SQUID_Volt(V)']))*1E6)
modcoil_currents = modcoil_currents[~pd.isnull(modcoil_currents)]
pickup_voltages = pickup_voltages[~pd.isnull(pickup_voltages)]

fig,ax = plt.subplots(figsize=(10, 8))  
ax.plot(modcoil_currents, pickup_voltages, '.')  
coeffs, covars = curve_fit(sincurve, modcoil_currents, pickup_voltages, \
      p0=[3, 150, 0, 0, 0])
print(coeffs)
ax.plot(np.linspace(15, 250), sincurve(np.linspace(15, 250), *coeffs) ,'-')

sensitivity = coeffs[0]*2*np.pi/coeffs[1]/(14E-12)*2.07E-15*1E6  #uV per flux quantum
sweetspot = -coeffs[2]*coeffs[1]/(2*np.pi)
while sweetspot < 0:
	sweetspot += coeffs[1]
while sweetspot > coeffs[1]:
	sweetspot -= coeffs[1]
	
plt.show()
			
print('Sweetspot = '+str(sweetspot)+'uA '+'Max Sensitivity = '+str(sensitivity)+'uV/Phi0')