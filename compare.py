#!/usr/local/bin/python3

import pexpect
import re
import sys

prompt = 'moira:  '
file = open("../2019-01-25-active_IPs.csv", "r") # Ask for file

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

for i, row in enumerate(MACtable):
	moira.sendline("qy ghid HWADDR " + row[2] )
	print(f"\r{row[2]} {i}/{len(MACtable)}: {conflicts} conflicts out of {matches} matches", file=sys.stderr, end='', flush=True)
	moira.expect(prompt)
	search = re.search('([\w-]+).MIT.EDU', moira.before)
	if search:
		matches += 1
		row += [search[0], search[1]]
		if row[1] != row[5]:
			conflicts += 1
			moira.sendline("qy ghus " + row[4])
			moira.expect(prompt)
			search = re.search('HOSTADDRESS, ([\d.]*)', moira.before)
			row[4] = search[1]

conflict_text = "\n"
agreement_text = "\nThe following hosts have MAC entries in Moira that agree with the ones in Netregadmin:\n"

MACtable = [row for row in MACtable if len(row) > 4]
for row in MACtable:
	if row[1] != row[5]:
		conflict_text += f"\n{row[2]}, network {row[3]}:\n"
		conflict_text += f"      Moira DHCP will offer {row[4]} ({row[5]}.mit.edu)\n"
		conflict_text += f"Netregadmin DHCP will offer {row[0]} ({row[1]}.mit.edu)\n"
	else:
		agreement_text += f"{row[0]} ({row[1]}.mit.edu)\n"

print("", file=sys.stderr)
print(f"\r{conflicts} conflicts out of {matches} matches                               ")
print(conflict_text)
print(agreement_text)
