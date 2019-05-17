

class constant_list(object):
	def __init__(self):
		self.nanovolt_address = 'GPIB0::22::INSTR'
		self.FC_sense_address = 'GPIB0::3::INSTR'
		self.FC_enable_address = 'GPIB0::7::INSTR'
		self.mod_sense_address = 'GPIB0::4::INSTR'
		self.mod_source_address = 'GPIB0::6::INSTR'
		self.magnet_source_address = 'GPIB0::5::INSTR'
		self.trigger_address = 'GPIB0::8::INSTR'
		self.squid_sense_address = 'GPIB0::2::INSTR'
	
	def get_nanovolt_address(self):
		return self.nanovolt_address