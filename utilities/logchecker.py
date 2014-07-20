#!/usr/bin/env python

#
# logchecker.py -
#
#  Will scrape a session log (i.e, 'screen -L' output) for various commands. Simply build an XML 'benchmark' indicating
#  what the commands should look like. Commands can be sorted and stored in XML 'list' entities and be tagged to be executed
#  'sequentially' or 'unsequentially'.
#
#	by Skyler Onken
#

import optparse
import mmap
import sys
import re
from lxml import objectify
from lxml.etree import XMLSyntaxError
import subprocess
from pipes import quote

positive_hits = 0
bench_count = 0
global_seq = False
logfile = None
is_verbose = False
clean_log_file = None

def instantiate_command_object(cmd):

	# take command XML Object and turn it into a dictionary

	cmd_obj = {}
	cmd_obj['flags'] = []
	cmd_obj['options'] = []
	cmd_obj['arguments'] = []

	for element in cmd.getchildren():
		
		if element.tag in "name":
			cmd_obj['name'] = element.text

		if element.tag in "flag":
			cmd_obj['flags'].append(element.text)

		if element.tag in "argument":
			cmd_obj['arguments'].append(element.text)

		if element.tag in "option":
			flag = element.find('flag')
			value = element.find('value')
			cmd_obj['options'].append((flag,value))

	return cmd_obj

def parse_element(element):

	global bench_count
	global global_seq

	enumerated_element = None

	if element.tag in "command":
		cmd_obj = instantiate_command_object(element)
		enumerated_element = cmd_obj
		bench_count += 1

	if element.tag in "list:":
		list_obj = []
		try:
			list_type = element.attrib['type']
			if list_type == "unsequential": 
				list_type = False
			else:
				list_type = True

		except AttributeError:
			# if the user fails to define the 'type' attribute within the XML, set it to whatever is passed via the -s switch.
			list_type = global_seq

		for sub_element in element.getchildren():
			# use recursion to parse lists
			parsed_sub_element = parse_element(sub_element)

			if is_verbose: print "\tAdding [%s] to benchmark" % sub_element.tag

			list_obj.append(parsed_sub_element)

		enumerated_element = (list_type,list_obj)

	return enumerated_element

def parse_benchmark(input_file):

	# Parse the benchmark xml data
	benchmark_root = []
	try:
		# Remove blank text from XML, do not parse comments, try to recover from badly formed XML.
		parser = objectify.makeparser(remove_blank_text=True,remove_comments=True,recover=True)
		benchmark_root = objectify.parse(input_file,parser).getroot()

	except XMLSyntaxError:
		print "Format error in Benchmark XML. Please Validate!!"
		exit()

	bench_list = parse_element(benchmark_root)

	return bench_list

def calculate_grade(positive_hits, bench_count):
	# calculate the percentile grade and return as string
	return "{:.0%}".format(float(positive_hits)/float(bench_count))

def check_command(command):
	# TODO
	name = command['name']

	return "\b%s\b" % name

def check_bench(bench_e, is_seq, log_context):
	# checks, and returns the position of found command, or -1 if not found

	global logfile

	# this is to check for 'lists'
	if type(bench_e) is tuple:
		sub_is_seq, sub_list = bench_e

		for sub_element in sub_list:
			# notate start position within the log file mmap. This enables unsequential searching of sublists.
			start_position = logfile.tell()
			# recursion for searching lists within lists
			result = check_bench(sub_element,sub_is_seq, log_context)

			# if the searched list (NOT the calling list; the one extracted at after the type() check) is sequential, tke action.
			if sub_is_seq:
				if result < 0:
					if is_verbose: print '\t\t[-] Failed to match next item in sequence. Breaking from sequence!'

					# This returns a failure to the parent list because the cuurent sequential list did not have
					# every instruction completed to specification. If the parent list is sequential, it will
					# therefor stop executing since this instruction (which happens to be another sequentia list)
					# did not execute accurately. Consider implementing a 'strict' value on sequential lists to
					# decide whether to enforce this functionality or not. 
					if is_seq: log_context = result
					break
				else:
					# if it worked, store the location it was found at to be returned to the calling function for storage in start_location
					log_context = result
			else:
				# if the list is not sequential, regardless of the result, move the mmap back to the start position.
				logfile.seek(start_position)

		# return line for reference and success check. Note: the log_context does not dictate search position. its a reference.
		return log_context

	# this is to check for 'commands'
	elif type(bench_e) is dict:
		global positive_hits
		if is_verbose: print '\tChecking for: %-25s Sequentially: [%r]' % (bench_e['name'], is_seq,), # trialing ',' remove newline. Not Py3 compatible.

		# get starting position in overall mmap
		start_position = logfile.tell()

		# iterate over logfile line by line, looking for command without its parameters
		for line in iter(logfile.readline, ""):

			# do stuff for positive match. This is not a full implementation. Just a filler.
			if re.search(r'\b%s\b' % bench_e['name'], line, re.X) is not None:
				if is_verbose: print '............Found!'
				positive_hits += 1
				return logfile.tell()

		if is_verbose: print "............NOT Found!"
		#print "Moving logfile back to start position: %d" % logfile.tell()
		logfile.seek(start_position)
		return -1

	# this is to check for 'output' elicited by an arbitrary command
	elif type(bench_e) is str:
		pass


def begin_check(options):

	# get a list of benchmarks to check for
	try:
		print "[*] Start Parsing Benchmark"
		bench = parse_benchmark(options.bench_file)

		# create mmap of file so we dont store the entire thing in memory
		global logfile
		f = open(clean_log_file)
		logfile = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

		print "[*] Start Checking Log File"
		check_bench(bench,global_seq, 0)

		logfile.close()
		f.close()

		# print results
		print '[*] Results:'
		print '\tFound %s out of %s' % (str(positive_hits),str(bench_count))
		print '\tScore: %s' % (str(calculate_grade(positive_hits, bench_count)))

	except (IOError, ValueError) as e:
		# catch any issues with the files
		print "Error with reading your files! Check to make sure read permissions are set and the file is closed!"
		exit()


def main():

	parser = optparse.OptionParser("usage: %prog -l LOG_FILE -b BENCHMARK_FILE")

	parser.add_option("-l", "--log", dest="log_file",
                  help="Logfile to check", metavar="LOG_FILE")

	parser.add_option("-b", "--benchmark", dest="bench_file",
                  help="File with the commands/strings to look for", metavar="BENCHMARK_FILE")

	parser.add_option("-s", action="store_true", dest="sequential",
                  help="Search sequentially through 'list' objects when not explicitly noted in the benchmark XML", metavar="SEQUENTIAL")

	parser.add_option("-v", action="store_true", dest="verbose",
                  help="Verbose output", metavar="SEQUENTIAL")

	(options, args) = parser.parse_args()

	# make the -l and -b arguments required
	if not options.log_file:   
		parser.error('Log file not given')

	if not options.bench_file:
		parser.error('Benchmark file not given')

	if options.sequential:
		global global_seq
		global_seq = True

	if options.verbose:
		global is_verbose
		is_verbose = True

	try:
		# clean the log file to clear it of backspaces, deleted characters, etc
		global clean_log_file
		# use quote() to prevent command injection
		subprocess.check_call(['cat {} | perl -pe \'s/\e([^\[\]]|\[.*?[a-zA-Z]|\].*?\a)//g\' | col -b > {}.clean'.format(quote(options.log_file), quote(options.log_file))], shell=True)
		clean_log_file = "%s.clean" % options.log_file
	except:
		print "Failed to prep the script file! It may contain bad characters that will skew the results!"

	try:
		begin_check(options)
		# delete the temp cleaned version of the log file
		subprocess.call(['rm','%s.clean' % options.log_file])

	except:
		#print "Unexpected error:", sys.exc_info()[0] #DEBUG ONLY
		#raise
		print "Error! Make sure all files are closed, paths are accurate and options are set correctly!"
		exit()

if __name__ == "__main__": main()