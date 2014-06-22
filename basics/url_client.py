#!/usr/bin/env python

import urllib2
import sys

url = sys.argv[1]

response = urllib2.urlopen(url)
html = response.read()
print html
