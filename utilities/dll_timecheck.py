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
import subprocess
import os
import time

line_size = 120
M_IND = 1
A_IND = 2
C_IND = 3
FILE_IND = 0

def sort_list(dlls, cat, is_reversed):
	index = -1
	if cat == "M": index = M_IND
	if cat == "A": index = A_IND
	if cat == "C": index = C_IND
	list = sorted(dlls, key=lambda x: x[index], reverse = is_reversed)
	return list

def print_header():
	print "\n"
	print "-" * line_size
	print " %-30s | %-30s | %-30s || %-30s" % ("Modified","Access","Created","DLL")
	print "-" * line_size

def add_timestamps(dlls):
	
	new_dlls = []
	
	for dll in dlls:
		mod_time=acc_time=cre_time=0.0
		
		try:
			mod_time = os.path.getmtime(dll)
			acc_time = os.path.getatime(dll)
			cre_time = os.path.getctime(dll)
		except:
			pass
			
		new_dlls.append([dll, mod_time, acc_time, cre_time])
		
	return new_dlls
		
	
def print_dlls_info(dlls):
	
	print_header()
	
	# convert timestamps into strings
	for dll in dlls:
		if dll[M_IND] == 0.0: 
			m_time=a_time=c_time="UNAVAILABLE"
		else:
			m_time = time.ctime(dll[M_IND])
			a_time = time.ctime(dll[A_IND])
			c_time = time.ctime(dll[C_IND])
		
		print " %-30s | %-30s | %-30s || %-30s" % (m_time,a_time,c_time,dll[FILE_IND])
	
def get_dlls_from_pid(pid):

	# run listdlls
	try:
		results = subprocess.check_output(["listdlls",pid], shell=True)
	except:
		print "[!] Issues with running 'listdlls', make sure the tool is installed correctly!"
		exit()
	
	# split the output into a list, remove the listdlls header.
	line_list = results.split(os.linesep)
	line_list = filter(None, line_list)
	line_list = line_list[4:]
	
	# check for data
	if len(line_list) < 1:
		print "[!] No DLLS were found! Check your PID or ensure that you are running with appropriate privileges"
		exit()
	# trim the headers upon successful listdlls
	line_list = line_list[3:]
	
	# Parse and remove everything except the DLL paths
	data = [line.split(' ',3)[3].lstrip() for line in line_list]
	
	return data

def main():

	parser = argparse.ArgumentParser(description='List MAC Information for DLLs associated with a PID. Requires "listdlls" to be installed')
	
	parser.add_argument('pid', type=str, help='The PID to check')
	parser.add_argument('-s', '--sort', type=str, choices=['M','A','C'], help="Sort by Modified, Access or Created On Timestamps")
	parser.add_argument('-r', '--reverse', dest='reverse', action='store_true',help='Sort in reverse order')
	#parser.add_argument('--verbose', dest='verbose', action='store_true', help='Return verbose output')

	args=parser.parse_args()
	
	dlls_list = get_dlls_from_pid(args.pid)
	
	dlls_list = add_timestamps(dlls_list)
	
	is_reversed = False
	if args.reverse is True:
		is_reversed = True
	
	if args.sort:
		dlls_list = sort_list(dlls_list, args.sort, is_reversed)
	
	print_dlls_info(dlls_list)
	

if __name__ == "__main__":
    main()