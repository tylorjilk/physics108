class Device:
	def __init__(self, address, resourceManager, en):
		self.address = address
		self.en = en
		self.rm = resourceManager
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
		self.resource.write(message)
	
	def query(self, message): # Queries a message to the device and returns the response
		return self.resource.query(message)
	
class 