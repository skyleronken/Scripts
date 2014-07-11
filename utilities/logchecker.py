#!/usr/bin/env python

import optparse
import mmap
import sys


def process_benchmark(input_file):

	lines = [line.rstrip('\n') for line in open(input_file)]

	return lines

def calculate_grade(positive_hits, bench_count):

	return "{:.0%}".format(positive_hits/bench_count)

def begin_parse(options):

	bench_list = process_benchmark(options.bench_file)

	bench_count = len(bench_list)
	positive_hits = 0

	if options.sequential:
		
		seq_pos = 0

		with open(options.log_file) as inF:
			for line in inF:
				if bench_list[seq_pos] in line:
					seq_pos += 1
					positive_hits += 1

	else:

		f = open(options.log_file)
		s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

		for entry in bench_list:
			if s.find(entry) != -1:
				positive_hits += 1

		s.close()
		f.close()

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

	if not options.log_file:   
		parser.error('Log file not given')

	if not options.bench_file:
		parser.error('Benchmark file not given')

	try:
		begin_parse(options)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise

if __name__ == "__main__":
    main()