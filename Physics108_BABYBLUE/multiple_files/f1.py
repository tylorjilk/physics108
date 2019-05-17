import physics108 as p108
import visa
import sys

def main():
	identifier = raw_input("Identifier for the run? ")
	
	rm = visa.ResourceManager()
	
	# Syntax is Device('address', visa.ResourceManager(), Enabled?)
	nanovolt_meter = p108.Device('GPIB0::22::INSTR', rm, True)
	
	fieldcoil_fnGen = p108.Device('GPIB0::7::INSTR', rm, True)
	fieldcoil_currMeas = p108.Device('GPIB0::3::INSTR', rm, True)
	fieldcoil_currMeas.setResValue(50.0)
	
	magnet_prog = p108.Device('GPIB0::5::INSTR', rm, True)
	squid_currMeas = p108.Devices('GPIB0::6::INSTR', rm, True) # Not the right address!!!!!!!!!!!!!!!!!!!!!!
	#squid_currMeas.setResValue(??)
	
	modcoil_fnGen = p108.Device('GPIB0::6::INSTR', rm, True)
	modcoil_currMeas = p108.Device('GPIB0::6::INSTR', rm, True)
	#modcoil_currMeas.setResValue(??)
	
	
	

if __name__ == "__main__":
    main()