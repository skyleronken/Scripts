#!/usr/bin/env python

import sys
import socket

host = sys.argv[1]

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "socket created"
except socket.error as err:
    print "socket failed"
    exit()

port = 80

s.connect((host,port))

while 1:
    
    cmd = raw_input('> ')

    if cmd == 'exit':
        break

    fileobj = s.makefile('r',0)

    try:
        fileobj.write(cmd)
        print 'command sent'
    except socket.error as err:
        print 'failed to send'

    try:   
        data = fileobj.readlines()
        print 'data received'
    except socket.error as err:
        print 'data failed to receive'
    
    for line in data:
        print line

s.close()
