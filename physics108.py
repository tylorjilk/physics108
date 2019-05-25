import numpy as np
import time

"""
List of constants
"""

TEST							= True

NANOVOLTMETER_ADDRESS			= 'GPIB0::22::INSTR'
SQUID_CURRENT_SENSE_ADDRESS		= 'GPIB0::4::INSTR'
TEMPERATURE_ADDRESS				= 'GPIB0::2::INSTR'
MOD_CURRENT_SENSE_ADDRESS		= 'GPIB0::9::INSTR'
MOD_CURRENT_SOURCE_ADDRESS		= 'GPIB0::8::INSTR'
FIELDCOIL_CURRENT_TRIG_ADDRESS	= 'GPIB0::7::INSTR'
MAGNET_PROG_ADDRESS				= 'GPIB0::5::INSTR'
EXT_TRIGGER_ADDRESS				= 'GPIB0::6::INSTR'

NANOVOLTMETER_COLUMN_HEADING 	= ''
SQUID_CURR_SEN_COLUMN_HEADING 	= ''
TEMPERATURE_COLUMN_HEADING		= ''
MOD_CURR_SEN_COLUMN_HEADING		= ''
MOD_CURR_SOUR_COLUMN_HEADING	= ''
FC_CURR_TRIG_COLUMN_HEADING		= ''
MAGNET_PROG_COLUMN_HEADING		= ''

RUN_IDENTIFIER					= ''
SAMPLING_RATE 					= 5 		# Hz
SAMPLING_TIMESTRETCH			= 5 		# seconds
SAMPLING_NUM_POINTS				= SAMPLING_RATE*SAMPLING_TIMESTRETCH
INIT_TIME_DELAY					= 0.2		# seconds
SAMPLING_DELAY_MAGNET			= 0.1		# seconds

MAGNET_FIELD_CONSTANT 			= 0.10238 	#field constant of magnet, T/A
MAGNET_FIELD_RAMP_RATE 			= 0.03		# ramp rate of magnet, T/s
MAGNET_CURRENT_RAMP_RATE 		= 0.3 		# 0.3 A/s  magnet_ramp_rate/magnet_constant*0.1
MAGNET_CURRENT_TARGET			= 1.5 		# 1.5 A
MAGNET_CURRENT_MARGIN			= 0.01		# A

FIELDCOIL_SENSE_RESISTOR 		= 50.0		# ohms
MOD_SENSE_RESISTOR 				= 9.13E3	# ohms
MOD_BFR_RESISTOR 				= 15.0E3	# ohms
SQUID_CURR_SENSE_RESISTOR 		= 101.5		# ohms

FNGEN_ZERO_COMMAND 				= 'APPL:DC DEF, DEF, 0'
FNGEN_TRIG_COMMAND 				= 'APPL:SQU ' + str(SAMPLING_RATE) + ', 5, 2.5'


"""
==============================================================================
HP 34401A: MULTIMETER
==============================================================================
"""
class Device_34401A:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.data = {}
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
	
	def init(self):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = time.time()
	
	def fetc_data(self):
		if self.en:
			try:
				newdata = (self.resource.query('FETC?').strip('\n')).split(',')
				end_time = self.prev_data_start_time + SAMPLING_TIMESTRETCH
				timepoints = np.linspace(self.prev_data_start_time, end_time, SAMPLING_NUM_POINTS)
				x = 0
				for datapoint in newdata:
					self.data[timepoints[x]] = datapoint
					x += 1
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
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.data = {}
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
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
	
	def init(self):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = time.time()
	
	def fetc_data(self):
		if self.en:
			try:
				newdata = (self.resource.query('FETC?').strip('\n')).split(',')
				end_time = self.prev_data_start_time + SAMPLING_TIMESTRETCH
				timepoints = np.linspace(self.prev_data_start_time, end_time, SAMPLING_NUM_POINTS)
				x = 0
				for datapoint in newdata:
					self.data[timepoints[x]] = datapoint
					x += 1
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
	
	def write(self, message): # Writes a message to the device
		if self.en:
			self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		if self.en:
			return self.resource.query(message)
		else:
			return None
	
	def init(self):
		if self.en:
			self.write('INIT')

"""
==============================================================================
AMI MODEL 420: POWER SUPPLY PROGRAMMER
==============================================================================
"""
class Device_Model420:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.data = {}
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
	
	def init(self):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = time.time()
	
	def fetc_data(self):
		if self.en:
			try:
				newdatapoint = float(self.resource.query("CURR:MAG?").lstrip('\x00'))
				timepoint = time.time()
				self.data[timepoint] = newdatapoint
				return newdatapoint
			except VI_Error_TMO:
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
		self.data = {}
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
	
	def init(self):
		if self.en:
			self.write('INIT')
			self.prev_data_start_time = time.time()
	
	def fetc_data(self):
		if self.en:
			try:
				newdata = (self.resource.query('FETC?').strip('\n')).split(',')
				end_time = self.prev_data_start_time + SAMPLING_TIMESTRETCH
				timepoints = np.linspace(self.prev_data_start_time, end_time, SAMPLING_NUM_POINTS)
				x = 0
				for datapoint in newdata:
					self.data[timepoints[x]] = datapoint
					x += 1
				return newdata
			except IOError:
				print("Error fetching data.")
		else:
			return None
			
	def get_complete_data(self):
		return self.data
