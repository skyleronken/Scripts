#!/usr/bin/env python

import httplib
import sys

http_server = sys.argv[1]

conn = httplib.HTTPConnection(http_server)

while 1:
    cmd = raw_input('input command (ex. GET index.html): ')
    cmd = cmd.split()

    if cmd[0] == 'exit':
        break

    conn.request(cmd[0], cmd[1])
    
    rsp = conn.getresponse()

    print(rsp.status, rsp.reason)
    data_received = rsp.read()
    print(data_received)

conn.close()
