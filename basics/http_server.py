import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

HandlerClass = SimpleHTTPRequestHandler
ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"

port = 8080

server_address = ('127.0.0.1',port)

print "starting..."
HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address,HandlerClass)

sa = httpd.socket.getsockname
print "Serving HTTP..."
httpd.serve_forever()
