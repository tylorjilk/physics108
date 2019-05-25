from subprocess import Popen, PIPE
import sys

process = Popen(['python', 'print_data.py'], stdout=PIPE, stderr=PIPE)

while True:
	line = process.stdout.readline()
	if not line:
		break
	sys.stdout.write(line)


"""
with subprocess.Popen(["print_data.py"], stdout=subprocess.PIPE) as proc:
	log.write(proc.stdout.read())
"""