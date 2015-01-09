# Test Data: 01FA070000000000000000000000000000000000000000000000000000000000000000000000000009000000

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

import argparse

audit_categories = ["System Events", "Logon Events", "Object Access", "Privilege Use", "Process Tracking", "Policy Change", "Account Management", "Directory Service Access", "Account Logon Events"]

def print_header():
	print "%-28s %8s %8s" % ("Key", "Success", "Failure")
	print "-----------------------------------------------"

def pretty_print_line(key, value):
	success = False
	failure = False
	
	if value == "03": failure=success=True
	if value == "02": failure=True
	if value == "01": success=True
	
	print "%-28s%8r%8r" % (key, success, failure)

def remove_bytes(string, num):
	return string[2*num:]

def parse_key(poladtev):
	
	is_auditing = False
	
	# Determine if auditing is on:
	val = poladtev[:2]
	if val == "01" : is_auditing = True
	
	print "\n\n===================================="
	print "Auditing is %s" % (("OFF", "ON")[is_auditing])
	print "====================================\n"
	
	poladtev = remove_bytes(poladtev, 4)
	
	# Move on to the auditing categories
	print_header()
	
	for category in audit_categories:
		pretty_print_line(category,poladtev[:2])
		poladtev = remove_bytes(poladtev, 4)
	

def main():

	parser = argparse.ArgumentParser(description='Parse Audit Policy from Registry Key')
	
	parser.add_argument('key', type=str, help='The key to parse. Located in hklm\security\policy\poladtev (i.e. 01FA070000000000000000000000000000000000000000000000000000000000000000000000000009000000)')
	#parser.add_argument('--verbose', dest='verbose', action='store_true', help='Return verbose output')

	args=parser.parse_args()
	
	parse_key(args.key)

if __name__ == "__main__":
    main()