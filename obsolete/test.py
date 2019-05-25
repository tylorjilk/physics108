import signal
import visa
import time
import sys, os
import msvcrt

# Capture Ctl-C, Save Data, and Clear Devices
def signal_handler(sig, frame):
	print('Goodbye')
	sys.exit(0)

def clear_input():
	while msvcrt.kbhit():
		msvcrt.getch()
	
def main():
	signal.signal(signal.SIGINT, signal_handler)
	
	print(os.getcwd() + '\\test')

if __name__ == "__main__":
    main()