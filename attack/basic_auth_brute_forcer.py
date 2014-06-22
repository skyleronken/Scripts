#!/usr/bin/env python

import sys
import httplib2
import urllib2
import base64
import time
import string

url = sys.argv[1]
username = 'admin'
password = ''
pass_attempt = ''
alphabet_list = list(string.ascii_lowercase) + list(string.ascii_uppercase)

def send_timed_request(url, username = None, password = None):

	try:
		request = urllib2.Request(url)
		base64string = base64.encodestring('%s:%s' % (username,pass_attempt)).replace('\n','')
		request.add_header("Authorization", "Basic %s" % base64string)
		result = urllib2.urlopen(request)
		start = time.time()
		page = result.read()
		#end = time.time()
		#load_time = end - start
		return (load_time,result.getcode())
	except urllib2.HTTPError:
		print '401'
		end = time.time()

	load_time = end - start
	return (load_time,result.getcode())

print send_timed_request(url)