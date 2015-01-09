# Author & Copyright : Skyler Onken 2015

#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import argparse
import subprocess

verbose = False

def convert_sid(raw_sid):

	sid = ["","",""]
	cur_sid_i = 2

	if verbose: print "[*] Raw Sid: " + raw_sid

	while len(raw_sid) > 0:
		sid[cur_sid_i] += raw_sid[-2:]
		
		raw_sid = raw_sid[:-2]

		if len(sid[cur_sid_i]) == 8:
			cur_sid_i -= 1
	if verbose: print "[*] Little Endian -> Big Endian : %s-%s-%s" % (sid[0], sid[1], sid[2])
	print "[*] Converted: %d-%d-%d" % (int(sid[0],16),int(sid[1],16),int(sid[2],16))
	
def determine_next_rid(reg_string):
	raw_rid = reg_string[144:148]
	if verbose: print "[*] Identified Unconverted Value: %s" % (raw_rid)
	
	hex_rid = raw_rid[-2:] + raw_rid[:-2]
	if verbose: print "[*] Little Endian -> Big Endian : %s" % (hex_rid)
	
	print "[*] Next RID: %d" % (int(hex_rid,16))
	
def main():

	parser = argparse.ArgumentParser(description='Convert Raw SID or determine next RID. If converting SID, provide the last 24 characters from HKEY_LOCAL_MACHINE\sam\sam\domains\account\V')
	
	parser.add_argument('raw', type=str, nargs='?', help='This is the value to convert.')
	parser.add_argument('--rid', dest='rid', action='store_true', help='Parse and calculate the next RID instead. Provide the entire value and only the value of "HKEY_LOCAL_MACHINE\sam\sam\domains\account\F"')
	parser.add_argument('--query', dest='query', action='store_true', help='Run req query on this machine to get the contents of HKEY_LOCAL_MACHINE\sam\sam\domains\account\'')
	parser.add_argument('--verbose', dest='verbose', action='store_true', help='Return verbose output')

	args=parser.parse_args()
	
	print '\n'
	
	if args.verbose is True:
		global verbose
		verbose = True
	
	if args.query:
		try:
			print subprocess.check_output(["reg","query","HKEY_LOCAL_MACHINE\sam\sam\domains\\account"])
		except:
			print "\n\n[!] FAILED - You probably don't have SYSTEM privileges"
			return 0
		
	if args.raw is None:
		parser.print_help()
		print "\n\n[!] Must provide a string to convert!"
		return 0
	
	if args.rid:
		determine_next_rid(args.raw)
		return 1
	
	if len(args.raw) != 24:
		parser.print_help()
		print "\n\n[!] You need 24 characters to calculate the SID!"
		return 0
	else:
		convert_sid(args.raw)
		return 1

if __name__ == "__main__":
    main()