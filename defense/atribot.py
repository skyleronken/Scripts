#!/usr/bin/env python

import dpkt, pcap
import re
import sys
import optparse

def print_status(msg):

	print "[*] " + msg

def print_error(msg):

	print "[!] " + msg

def print_data(msg):

	print "[+] " + msg

def process_packet(ts,pkt):

	print 'packet'

def start_capture(interface):

	pc = pcap.pcap(name=interface,immediate=True)

	try:
		print_status('listening on %s' % (pc.name))
		pc.loop(0,process_packet)

	except KeyboardInterrupt:
		nrecv, ndrop, nifdrop = pc.stats()
		print_status('%d packets received by filter' % nrecv)
		print_status('%d packets dropped by kernel' % ndrop)
		exit()

	except:
		print "Unexpected error:", sys.exc_info()[0]
    	raise

def main():

	parser = optparse.OptionParser("usage %prog -i <interface>")
 	parser.add_option('-i', dest='interface', type='string',help='specify interface to listen on')

 	(options, args) = parser.parse_args()
	
	if options.interface == None:
		print parser.usage
 		exit(0)
 	else:
 		interface = options.interface

 	start_capture(interface)

if __name__ == "__main__":
    main()