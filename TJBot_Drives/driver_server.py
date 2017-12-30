#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2017 Paul G Crumley

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

Very simple web server to control Etekcity relays using a 433 MHz transmitter
connected to a Raspberry Pi pin.

Send a JSON dictionary with keys of:
  "address" (0-255)
  "unit" (1-5)
  "action" ("on"|"off")
  optional "pin" (valid board pin number)
The default pin number is 18.

try a curl command such as:
  curl -H 'Content-Type: application/json' -X POST -d '{"address":21, 
    "unit":1, "action": "on"}'  http://localhost:11111/

The server must run as root to have access to the GPIO pins.

"""

import argparse
import datetime
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from etekcity_controller import Transmitter

DEBUG = 0

DEFAULT_LISTEN_ADDRESS = '127.0.0.1' # responds to only requests from localhost
#DEFAULT_LISTEN_ADDRESS = '0.0.0.0'  # respond to request from any address
DEFAULT_LISTEN_PORT = 11111                 # IP port
DEFAULT_SERVER_ADDRESS = (DEFAULT_LISTEN_ADDRESS, DEFAULT_LISTEN_PORT)

USE_MESSAGE = ('send a JSON dictionary with keys of '
               '<UL>'
               '<LI>"address" (0-255)'
               '<LI>"unit" (1-5)'
               '<LI>"action" ("on"|"off")'
               '<LI>optional "pin" (valid board pin number)'
               '</UL>'
               )

DEFAULT_PIN = 18


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
            pin_num = DEFAULT_PIN
            if 'pin' in data:
                pin_num = data['pin']
            address_num = data['address']
            unit_num = data['unit']
            action = data['action']
        
            if DEBUG:
                print('pin:     {}'.format(pin_num), file=sys.stderr)
                print('address: {}'.format(address_num), file=sys.stderr)
                print('unit:    {}'.format(unit_num), file=sys.stderr)
                print('action:  {}'.format(action), file=sys.stderr)
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(bytes(USE_MESSAGE, 'utf8'))
            return

        
        ec = Transmitter(pin_num)    
        ec.transmit_action(address_num, unit_num, action)

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-Type','application/json')
        self.end_headers()

        result = {}
        result['status'] = 200
        result['pin'] = pin_num
        result['address'] = address_num
        result['unit'] = unit_num
        result['action'] = action

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
        description='REST server for Etekcity Outlet controller')
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

