#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2017, 2018 Paul G Crumley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: pgcrumley@gmail.com

Very simple web server to control a TOYDALOO RC dump truck.

The server only responds to JSON requests and there are two types of 
supported request.

The first sends a JSON list of (op, time) where op can be ony of:
  "stop", "halt", "forward", "backward", "right", "left", "cw", or "ccw" and
  time is in seconds.  After all ops are run the truck is stopped.
  
The second sends a JSON item with a single op from the above list and the 
device runs with that op till a new op is received.  

Both forms of request are sent as a map.  

Form 1:
    { "drive_ops" : [ ("op1", time1), ("op2", time2), ... ] }
Form 2:
    { "drive" : "op" }


try a curl command such as:
  curl -H 'Content-Type: application/json' -X POST -d '{"drive_ops": 
    [("forward", 2)", ("left", 0.5), ("backward", 1)]}'  http://localhost:9999/

The server must run as root to have access to the GPIO pins.
"""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from driver_controller import Controller

DEBUG = False

DEFAULT_LISTEN_ADDRESS = '127.0.0.1' # responds to only requests from localhost
#DEFAULT_LISTEN_ADDRESS = '0.0.0.0'  # respond to request from any address
DEFAULT_LISTEN_PORT = 9999                 # IP port
DEFAULT_SERVER_ADDRESS = (DEFAULT_LISTEN_ADDRESS, DEFAULT_LISTEN_PORT)

USE_MESSAGE = ('send a JSON dictionary with keys of '
               '<UL>'
               '<LI>{"drive_ops" : [ ("op", time in seconds), ...]}'
               '</UL>'
               '<P>or</P>'
               '<UL>'
               '<LI>{"drive" : "op"}'
               '</UL>'
               )

CONTROLLER = Controller()

class Simple_RequestHandler(BaseHTTPRequestHandler):
    '''
    A subclass of BaseHTTPRequestHandler for our work.
    '''

    def do_GET(self):
        '''
        handle the HTTP GET request
        '''        
        if DEBUG:
            print('got GET request', file=sys.stderr)

        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-Type','text/html')
        self.end_headers()

        # Write content as utf-8 data
        self.wfile.write(bytes(USE_MESSAGE, 'utf8'))
        return


    def do_POST(self):
        '''
        handle the HTTP POST request
        '''
        if DEBUG:
            print('got POST request', file=sys.stderr)
            print(self.headers, file=sys.stderr)
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len).decode('utf8')
        if DEBUG:
            print('post_body: "{}"'.format(post_body), file=sys.stderr)     
        data = json.loads(post_body)
        if DEBUG:
            print('post data: "{}"'.format(data), file=sys.stderr)

        try:
            keys = data.keys()
            if DEBUG:
                print('keys:     {}'.format(keys), file=sys.stderr)
            if 'drive' in keys:
                op = data['drive']
                CONTROLLER.drive(op)
            elif 'drive_ops' in keys:
                ops_list = data['drive_ops']
                CONTROLLER.drive_ops(ops_list)
            else:
                raise ValueError('keys of "{}" not known'.format(keys))
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(bytes(USE_MESSAGE, 'utf8'))
            return

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-Type','application/json')
        self.end_headers()

        result = {}
        result['status'] = 200

        self.wfile.write(bytes(json.dumps(result, indent=1), "utf8"))
        return
 
    def log_message(self, format, *args):
        """
        This quiets the annoying messages to STDOUT.
        
        Remove this if you want to see those lines.
        """
        return
 
 
if '__main__' == __name__:
    parser = argparse.ArgumentParser(
        description='REST server for TOYDALOO RC dump truck controller')
    parser.add_argument('-v', '--verbose', 
                        help='increase output verbosity',
                        action='store_true'
                        )
    parser.add_argument('--network_port',
                        default=DEFAULT_LISTEN_PORT,
                        help='network port for server 0-65535',
                        type=int
                        )
    parser.add_argument('--network_address',
                        default=DEFAULT_LISTEN_ADDRESS,
                        help='network address for server in form of "x.x.x.x"'
                        )
    args = parser.parse_args()
    
    if args.verbose:
        DEBUG = True
    
    if DEBUG:
        print('verbose:  {}'.format(args.verbose), file=sys.stderr)
        print('port:     {}'.format(args.network_port), file=sys.stderr)
        print('address:  {}'.format(args.network_address), file=sys.stderr)
    
    server_address = (args.network_address, args.network_port)
    if DEBUG:
        print('server_address: "{}"'.format(server_address), file=sys.stderr)
    
    try:
        httpd_server = HTTPServer(server_address, Simple_RequestHandler)
        print('running server listening on {}...'.format(server_address))
        httpd_server.serve_forever()
    except Exception as ex:
        print('caught "{}"'.format(ex))

