#!/usr/bin/env python

import optparse
import mmap
import sys


def process_benchmark(input_file):

	# read in lines of benchmark file into memory. Consider revising if benchmark files become too large.
	# strip out the newline characters in the process.
	lines = [line.rstrip('\n') for line in open(input_file)]

	return lines

def calculate_grade(positive_hits, bench_count):

	# calculate the percentile grade and return as string
	return "{:.0%}".format(positive_hits/bench_count)

def begin_parse(options):

	# get a list of benchmarks to check for
	bench_list = process_benchmark(options.bench_file)

	positive_hits = 0

	if options.sequential:
		
		seq_pos = 0

		# read the log file line by line
		with open(options.log_file) as inF:
			for line in inF:
				# if the log file contains the current benchmark, iterate to the next benchmark and add a hit
				if bench_list[seq_pos] in line:
					seq_pos += 1
					positive_hits += 1

			inF.close()

	else:

		# since we are not searching sequentially, open up the file in mmap. This uses the file itself
		# rather than loading the entire contents into memory.
		f = open(options.log_file)
		s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

		# use s.find instead of 'in' for anything after 2.7.
		for entry in bench_list:
			if s.find(entry) != -1:
				positive_hits += 1

		# clean up. Probably not necessary but good habit.
		s.close()
		f.close()


	bench_count = len(bench_list)

	# print results
	print 'Results:'
	print '\t Found %s out of %s' % (str(positive_hits),str(bench_count))
	print '\t Score: %s' % (str(calculate_grade(positive_hits, bench_count)))


def main():

	parser = optparse.OptionParser("usage: %prog -l LOG_FILE -b BENCHMARK_FILE")

	parser.add_option("-l", "--log", dest="log_file",
                  help="Logfile to check", metavar="LOG_FILE")

	parser.add_option("-b", "--benchmark", dest="bench_file",
                  help="File with the commands/strings to look for", metavar="BENCHMARK_FILE")

	parser.add_option("-s", action="store_true", dest="sequential",
                  help="Search for benchmarks sequentially", metavar="SEQUENTIAL")

	(options, args) = parser.parse_args()

	# make the -l and -b arguments required
	if not options.log_file:   
		parser.error('Log file not given')

	if not options.bench_file:
		parser.error('Benchmark file not given')

	try:
		begin_parse(options)

	except (IOError, ValueError) as e:
		# catch any issues with the files
		print "Error with reading your files! Check to make sure read permissions are set and the file is closed!"
		exit()

	except:
		#print "Unexpected error:", sys.exc_info()[0] DEBUG ONLY
		#raise
		print "Error! Make sure all files are closed, paths are accurate and options are set correctly!"
		exit()

if __name__ == "__main__":
    main()