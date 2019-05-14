import visa
import time
import sys

command = bytes([0x20+31, 0x20+3, 0x20+4, 0x08, 0x20+31])

interval_in_ms = 500
number_of_readings = 10

multimeter_3_address = 'GPIB0::3::INSTR'	# squid pickup multimeter
multimeter_4_address = 'GPIB0::4::INSTR'	# temp probe multimeter
interface_address = 'GPIB0::INTFC'
"""
unl_Byte = 63
talk_Listen_Bytes = [0,0,0]
talk_Listen_Bytes[0] = 32 + 3
talk_Listen_Bytes[1] = 32 + 4
talk_Listen_Bytes[2] = 64 + 0
get_Byte = 8
"""
rm = visa.ResourceManager()

intf = rm.open_resource(interface_address)
#intf.send_ifc()
multimeter_3 = rm.open_resource(multimeter_3_address)
multimeter_4 = rm.open_resource(multimeter_4_address)

multimeter_3.write("*RST")
multimeter_3.write("CONF:VOLT:DC")
multimeter_3.write("TRIG:SOUR BUS")
multimeter_3.write("INIT")

multimeter_4.write("*RST")
multimeter_4.write("CONF:VOLT:DC")
multimeter_4.write("TRIG:SOUR BUS")
multimeter_4.write("INIT")

#intf.Command(unl_Byte, 1)
#intf.Command(talk_Listen_Bytes, 2)
#intf.Command(get_Byte, 1)

#response = intf.visalib.gpib_command(intf.session, bytes([0x08]))

#intf.send_command([0x20+31, 0x20+3, 0x20+4, 0x08, 0x20+31])
intf.group_execute_trigger(multimeter_3, multimeter_4)

#intf.send_command("*TRG")
#multimeter_3.write("*TRG")
#print(multimeter_3.query("FETC?"))