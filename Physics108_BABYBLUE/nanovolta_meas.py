import visa
import time

nanovolt_address = 'GPIB0::22::INSTR'
multimeter_address = 'GPIB0::2::INSTR'

rm = visa.ResourceManager()
print(rm.list_resources())

nanovolt_meter = rm.open_resource(nanovolt_address)
multimeter = rm.open_resource(multimeter_address)
print(nanovolt_meter.query('*IDN?'))
print(multimeter.query('*IDN?'))

file = open("testdata.txt", "w")

while(True):
	nano_voltage = nanovolt_meter.query('MEAS?')
	nano_voltage = nano_voltage.strip('\n')
	voltage = multimeter.query('MEAS?')
	current_time = time.time()

	data_string = str(current_time) + " , " + str(nano_voltage) + " , " + str(voltage)
	file.write(data_string)