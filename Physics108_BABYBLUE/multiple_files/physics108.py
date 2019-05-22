"""
List of constants
"""
NANOVOLTMETER_ADDRESS			= 'GPIB0::22::INSTR'
SQUID_CURRENT_SENSE_ADDRESS		= 'GPIB0::4::INSTR'
TEMPERATURE_ADDRESS				= 'GPIB0::2::INSTR'
MOD_CURRENT_SENSE_ADDRESS		= 'GPIB0::9::INSTR'
MOD_CURRENT_SOURCE_ADDRESS		= 'GPIB0::8::INSTR'
FIELDCOIL_CURRENT_TRIG_ADDRESS	= 'GPIB0::7::INSTR'
MAGNET_PROG_ADDRESS				= 'GPIB0::5::INSTR'

RUN_IDENTIFIER = ''

MAGNET_FIELD_CONSTANT = 0.10238 	#field constant of magnet, T/A
MAGNET_FIELD_RAMP_RATE = 0.03		# ramp rate of magnet, T/s
MAGNET_CURRENT_RAMP_RATE = 0.3 		# A/s  magnet_ramp_rate/magnet_constant*0.1
MAGNET_MAX_CURRENT = 1.5 			# A

FIELDCOIL_SENSE_RESISTOR = 50.0		# ohms
MOD_SENSE_RESISTOR = 9.13E3			# ohms
MOD_BFR_RESISTOR = 15.0E3			# ohms
SQUID_CURR_SENSE_RESISTOR = 101.5	# ohms


"""
Device Class
"""
class Device:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
		self.data = []
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
		self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		return self.resource.query(message)
	
	def init(self):
		self.write('INIT')
	
	def fetc_data(self):
		newdata = (self.resource.query('FETC?').strip('\n')).split(',')
		self.data.extend(newdata)
		return newdata
	
	def get_complete_data(self):
		return self.data