#!/usr/local/bin/python3

import re
import subprocess

file = open("2019-01-23-active_IPs.csv", "r")

lines = []

for line in file:
	if re.search('[0-9a-f]{12}', line):
		lineArray = line.split(',')
		lines += [[lineArray[2],lineArray[3]]]

command = "\""

for line in lines[1000:2000]: # in batches of 1000 otherwise it gets too long for bash or ssh
	command += "$(qy get_host_by_identifier HWADDR " + line[1] + " |head -n1 |sed  's/name: *//g' |sed 's/.MIT.EDU//')," + line[0] + "|"

result = subprocess.check_output(["ssh", "athena", "printf", command + "\""]).decode();

result = result.split("|")

for line in result:
	splitLine = line.split(',')
	if splitLine[0]:
		print (splitLine[0], splitLine[1])