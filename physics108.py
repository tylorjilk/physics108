import numpy as np
import time
import visa

"""
List of constants
"""

TEST							= False

NANOVOLTMETER_ADDRESS			= 'GPIB0::22::INSTR'
SQUID_CURRENT_SENSE_ADDRESS		= 'GPIB0::4::INSTR'
TEMPERATURE_ADDRESS				= 'GPIB0::2::INSTR'
MOD_CURRENT_SENSE_ADDRESS		= 'GPIB0::9::INSTR'
MOD_CURRENT_SOURCE_ADDRESS		= 'GPIB0::8::INSTR'
FIELDCOIL_CURRENT_TRIG_ADDRESS	= 'GPIB0::7::INSTR'
FIELDCOIL_CURRENT_SEN_ADDRESS	= 'GPIB0::3::INSTR'
MAGNET_PROG_ADDRESS				= 'GPIB0::5::INSTR'
EXT_TRIGGER_ADDRESS				= 'GPIB0::6::INSTR'

NANOVOLTMETER_COLUMN_HEADING 	= 'SQUID_Volt(V)'
SQUID_CURR_SEN_COLUMN_HEADING 	= 'SQUID_Curr(A)'
TEMPERATURE_COLUMN_HEADING		= 'Temp(V)'
MOD_CURR_SEN_COLUMN_HEADING		= 'MOD_CURR(A)'
FC_CURR_SEN_COLUMN_HEADING		= 'FC_CURR(A)'
MAGNET_PROG_COLUMN_HEADING		= 'MAG_CURR(A)'

RUN_IDENTIFIER					= ''		# Set by user input
RUN_SELECTION_ID				= 0			# Set by user input
"""
	Options for RUN_SELECTION_ID are:
		(1) voltage-versus-time of squid
		(2) voltage-versus-mod coil current
		(3) magnet run with reset squid and nv measure
		(4) magnet run
		(5) reset squid
"""
SAMPLING_RATE 					= 5 		# Hz 
SAMPLING_TIMESTRETCH			= 5 		# seconds
SAMPLING_NUM_POINTS				= SAMPLING_RATE*SAMPLING_TIMESTRETCH
INIT_TIME_DELAY					= 0.2		# seconds
SAMPLING_DELAY_MAGNET			= 0.1		# seconds

MAGNET_FIELD_CONSTANT 			= 0.10238 	#field constant of magnet, T/A
MAGNET_FIELD_RAMP_RATE 			= 0.03		# ramp rate of magnet, T/s
MAGNET_CURRENT_RAMP_RATE 		= 0.3 		# 0.3 A/s  magnet_ramp_rate/magnet_constant*0.1
MAGNET_CURRENT_TARGET			= 1.5 		# 1.5 A
MAGNET_CURRENT_MARGIN			= 0.005		# A

FIELDCOIL_SENSE_RESISTOR 		= 50.0		# ohms
FIELDCOIL_TARGET_CURRENT		= 0.080		# A
FIELDCOIL_RESET_TIME			= 2			# seconds
FIELDCOIL_INIT_DELAY			= 1			# seconds, time before end of magnet ramp to start devices

MOD_SENSE_RESISTOR 				= 9.13E3	# ohms
MOD_BFR_RESISTOR 				= 15.0E3	# ohms
SQUID_CURR_SENSE_RESISTOR 		= 101.5		# ohms
MOD_CURR_OPTIMAL				= 102E-6	# A, current of mod coils at steepest part of curve
MOD_VOLT_OPTIMAL				= MOD_CURR_OPTIMAL*(MOD_BFR_RESISTOR + MOD_SENSE_RESISTOR)/2.0
MOD_CURR_TARGET_MAX				= 250.0E-6	# mA, maximum current in sweep
MOD_CURR_STEP					= 2.0E-6	# mA, the spacing between each mod coil current value
MOD_CURR_TIME_STEP				= 1.00		# seconds, time between each current step

FNGEN_ZERO_COMMAND 				= 'APPL:DC DEF, DEF, 0'
FNGEN_TRIG_COMMAND 				= 'APPL:SQU ' + str(SAMPLING_RATE) + ', 5, 2'
FNGEN_CURR_OPTIMAL_COMMAND		= 'OFFS ' + str(MOD_VOLT_OPTIMAL)


"""
==============================================================================
HP 34401A: MULTIMETER
==============================================================================
"""
class Device_34401A:
	def __init__(self, address, column, resourceManager, en):
		self.address = address
		self.column = column
		self.en = en
		self.rm = resourceManager
		self.data = {'timestamp':[],self.column:[]}
		self.prev_data_start_time = 0
		if self.en:
			self.connect()
	
	def enable(self): # Enables the device
		self.en = True
	
	def disable(self): # Disables the device
		self.en = False
		
	def isEnabled(self): # Returns the enabled status of device
		return self.en
		
	def connect(self): # Opens the pyvisa comms pathway to device
		if self.en:
			self.resource = self.rm.open_resource(self.address)
			self.write('*CLS')
			self.write('*RST')
	
	def configure(self):
		if self.en:
			self.write('CONF:VOLT:DC')
			self.write('TRIG:COUN ' + str(SAMPLING_NUM_POINTS))
			self.write('TRIG:SOUR EXT')
	
	def setResValue(self, res): # Sets the sense resistor value, in ohms
		self.resistorValue = res
		
	def getResVallue(self): # Returns the sense resistor value, in ohms
		return self.resistorValue
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
			
	def needs_init(self):
		return True
	
	def init(self, data_time):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = data_time
	
	def fetc_data(self):
		if self.en:
			try:
				newdata = (self.resource.query('FETC?').strip('\n')).split(',')
				end_time = self.prev_data_start_time + SAMPLING_TIMESTRETCH
				timepoints = np.linspace(self.prev_data_start_time, end_time, SAMPLING_NUM_POINTS)
				self.data['timestamp'].extend(timepoints)
				self.data[self.column].extend(newdata)
				return newdata
			except IOError:
				print("Error fetching data.")
		else:
			return None
			
	def get_complete_data(self):
		return self.data

"""
==============================================================================
AGILENT 34420A: NANO VOLT METER
==============================================================================
"""
class Device_34420A:
	def __init__(self, address, column, resourceManager, en):
		self.address = address
		self.column = column
		self.en = en
		self.rm = resourceManager
		self.data = {'timestamp':[],self.column:[]}
		self.prev_data_start_time = 0
		if self.en:
			self.connect()
	
	def enable(self): # Enables the device
		self.en = True
	
	def disable(self): # Disables the device
		self.en = False
		
	def isEnabled(self): # Returns the enabled status of device
		return self.en
		
	def connect(self): # Opens the pyvisa comms pathway to device
		if self.en:
			self.resource = self.rm.open_resource(self.address)
			self.write('*CLS')
			self.write('*RST')
	
	def configure(self):
		if self.en:
			self.write('CONF:VOLT:DC:DIFF')
			self.write('SENS:VOLT:DC:NPLC 2')
			self.write('TRIG:SOUR EXT')
			self.write('TRIG:COUN ' + str(SAMPLING_NUM_POINTS))
			self.write('TRIG:DEL 0')
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
	
	def needs_init(self):
		return True
	
	def init(self, data_time):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = data_time
	
	def fetc_data(self):
		if self.en:
			try:
				newdata = (self.resource.query('FETC?').strip('\n')).split(',')
				end_time = self.prev_data_start_time + SAMPLING_TIMESTRETCH
				timepoints = np.linspace(self.prev_data_start_time, end_time, SAMPLING_NUM_POINTS)
				self.data['timestamp'].extend(timepoints)
				self.data[self.column].extend(newdata)
				return newdata
			except IOError:
				print("Error fetching data.")
		else:
			return None
			
	def get_complete_data(self):
		return self.data

"""
==============================================================================
SRS DS345: SYNTHESIZED FUNCTION GENERATOR
==============================================================================
"""
class Device_DS345:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.prev_data_start_time = 0
		self.data = None
		if self.en:
			self.connect()
	
	def enable(self): # Enables the device
		self.en = True
	
	def disable(self): # Disables the device
		self.en = False
		
	def isEnabled(self): # Returns the enabled status of device
		return self.en
		
	def connect(self): # Opens the pyvisa comms pathway to device
		if self.en:
			self.resource = self.rm.open_resource(self.address)
	
	def configure(self):
		if self.en:
			self.write('OFFS 0')
			
	def needs_init(self):
		return False
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
	
	def set_optimal_current(self):
		if self.en:
			self.write(FNGEN_CURR_OPTIMAL_COMMAND)
	
	def set_current(self, curr):
		if self.en:
			v = curr*(MOD_BFR_RESISTOR + MOD_SENSE_RESISTOR)/2.0
			msg = 'OFFS ' + str(v)
			if curr <= MOD_CURR_TARGET_MAX:
				self.write(msg)
	
	def set_fc_current(self, curr):
		if self.en:
			v = curr*10/2
			msg = 'OFFS ' + str(v)
			if curr <= FIELDCOIL_TARGET_CURRENT:
				self.write(msg)
	
	def init(self):
		if self.en:
			self.write('INIT')

"""
==============================================================================
AMI MODEL 420: POWER SUPPLY PROGRAMMER
==============================================================================
"""
class Device_Model420:
	def __init__(self, address, column, resourceManager, en):
		self.address = address
		self.column = column
		self.en = en
		self.rm = resourceManager
		self.data = {'timestamp':[],self.column:[]}
		if self.en:
			self.connect()
	
	def enable(self): # Enables the device
		self.en = True
	
	def disable(self): # Disables the device
		self.en = False
		
	def isEnabled(self): # Returns the enabled status of device
		return self.en
		
	def connect(self): # Opens the pyvisa comms pathway to device
		if self.en:
			self.resource = self.rm.open_resource(self.address)

	def configure(self):
		if self.en:
			self.write("CONF:RAMP:RATE:CURR " + str(MAGNET_CURRENT_RAMP_RATE) + " A/s")
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
	
	def needs_init(self):
		return False
	
	def take_datapoint(self):
		if self.en:
			try:
				newdatapoint = float(self.resource.query("CURR:MAG?").lstrip('\x00'))
				timepoint = time.time()
				self.data['timestamp'].extend([timepoint])
				self.data[self.column].extend([newdatapoint])
				return newdatapoint
			except IOError:
				print("Error fetching magnet data.")
		else:
			return None
			
	def get_complete_data(self):
		return self.data

"""
==============================================================================
HP 33120A: ARBITRARY WAVEFORM GENERATOR
==============================================================================
"""
class Device_33120A:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.data = None
		self.prev_data_start_time = 0
		if self.en:
			self.connect()
	
	def enable(self): # Enables the device
		self.en = True
	
	def disable(self): # Disables the device
		self.en = False
		
	def isEnabled(self): # Returns the enabled status of device
		return self.en
		
	def connect(self): # Opens the pyvisa comms pathway to device
		if self.en:
			self.resource = self.rm.open_resource(self.address)
			self.write('*CLS')
			self.write('*RST')
	
	def configure(self):
		if self.en:
			self.write(FNGEN_ZERO_COMMAND)
	
	def needs_init(self):
		return False
		
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None