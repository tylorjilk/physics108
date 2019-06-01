import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, ntpath
import pandas as pd
import matplotlib.pyplot as plt

time_delay = 3 # seconds

def make_graph(x, y, x_label, y_label, title, dir):
	plt.plot(x,y)
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.savefig(dir + x_label + '_vs_' + y_label + '.svg')

class Watcher:
	DIRECTORY_TO_WATCH = "C:\\Users\\Student\\physics108\\data\\4th_cooldown\\"
	global make_graph

	def __init__(self):
		self.observer = Observer()

	def run(self):
		event_handler = Handler()
		self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
		self.observer.start()
		try:
			while True:
				time.sleep(5)
		except:
			self.observer.stop()
			print "Error"

		self.observer.join()


class Handler(FileSystemEventHandler):

	@staticmethod
	def on_any_event(event):
		if event.is_directory:
			return None

		elif event.event_type == 'created':
			if '.csv' in event.src_path:
				print "Received created event - %s." % event.src_path
				time.sleep(time_delay)
				data = pd.read_csv(event.src_path, delimiter=',')
				times = data['timestamp']
				squid_voltage = data['SQUID_Volt(V)']
				#squid_current = data['SQUID_Curr(A)']
				#temp = data['Temp(V)']
				#mod_current = data['MOD_CURR(A)']
				#fc_current = data['FC_CURR(A)']
				#magnet_current = data['MAG_CURR(A)']
				
				path = str(event.src_path).strip('.csv') + '\\'
				os.mkdir(path)

				make_graph(times, squid_voltage,'timestamp','SQUID_Volt(V)','Squid Voltage vs Time',path)
			
			

		elif event.event_type == 'modified':
			# Taken any action here when a file is modified.
			print "Received modified event - %s." % event.src_path

if __name__ == '__main__':
	w = Watcher()
	w.run()