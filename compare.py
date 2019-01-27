#!/usr/local/bin/python3

import pexpect
import re
import sys

prompt = 'moira:  '
file = open("../2019-01-23-active_IPs.csv", "r") # Ask for file

MACtable = []
for line in file:
	if re.search('[0-9a-f]{12}', line):
		lineArray = line.split(',')
		MACtable += [lineArray[1:5]]

moira = pexpect.spawnu('ssh athena mrtest')
moira.expect(prompt)
moira.sendline("connect")
moira.expect(prompt)
moira.sendline("auth")
moira.expect(prompt)

matches = 0
conflicts = 0

for i, line in enumerate(MACtable):
	print(f"\r{line[2]} {i}/{len(MACtable)}: {conflicts} conflicts out of {matches} matches", file=sys.stderr, end='', flush=True)
	moira.sendline("qy ghid HWADDR " + line[2] )
	moira.expect(prompt)
	search = re.search('([\w-]+).MIT.EDU', moira.before)
	if search:
		matches += 1
		line += [search[0], search[1]]
		if line[1] != line[5]:
			conflicts += 1
			moira.sendline("qy ghus " + line[4])
			moira.expect(prompt)
			search = re.search('HOSTADDRESS, ([\d.]*)', moira.before)
			line[4] = search[1]

conflict_text = "\n"
agreement_text = "\nThe following hosts have MAC entries in Moira that agree with the ones in Netregadmin:\n"

MACtable = [line for line in MACtable if len(line) > 4]
for entry in MACtable:
	if entry[1] != entry[5]:
		conflict_text += f"\n{entry[2]}, network {entry[3]}:\n"
		conflict_text += f"      Moira DHCP will offer {entry[4]} ({entry[5]}.mit.edu)\n"
		conflict_text += f"Netregadmin DHCP will offer {entry[0]} ({entry[1]}.mit.edu)\n"
	else:
		agreement_text += f"{entry[0]} ({entry[1]}.mit.edu)\n"

print("", file=sys.stderr)
print(f"\r{conflicts} conflicts out of {matches} matches                               ")
print(conflict_text)
print(agreement_text)
