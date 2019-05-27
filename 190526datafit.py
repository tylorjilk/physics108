import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def sincurve(x, A, T, phi, a, b):
    return A*np.sin(2*np.pi/T*x+phi)+a*x+b

data = pd.read_csv(r'./physics108/data/3rd_cooldown/mod_coil_0-75_hz_181616.csv', delimiter=',')
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
			
print('Sweetspot = '+str(sweetspot)+'uA '+'Max Sensitivity = '+str(sensitivity)+'uV/Phi0')