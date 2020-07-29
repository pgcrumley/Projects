#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2019 Paul G Crumley

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

Very simple web server to provide a camera image from the Raspberry Pi camera

By default will accept GET from any address on port 5000
"""

import argparse
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import sys
from time import sleep

from picamera import PiCamera

DEBUG = None

DEFAULT_LISTEN_ADDRESS = '0.0.0.0'    # respond to request from any address
DEFAULT_LISTEN_PORT = '5000'            # IP port 5000

MINIMUM_PREVIEW_TIME_IN_SECONDS = 0.25

DEFAULT_ICON_FILE_NAME = '/opt/Projects/CameraServer/favicon.ico'
FAVICON = None

DEFAULT_LOG_FILE_NAME = '/opt/Projects/logs/CameraServer.log'
log_file = None


def emit_json_map(output, json_map):
    '''
    generate a time stamp in UTC for use in the output
    
    A 'when' entry with the time stamp is added to the json_map.
    '''
    when = datetime.datetime.now(datetime.timezone.utc)
    when_str = when.isoformat()
    json_map['when'] = when_str
    message = json.dumps(json_map)
    output.write('{}\n'.format(message))
    output.flush()


def emit_event(output, event_text):
    '''
    send a line with an event to the output with a time stamp
    '''
    item = {'event':event_text}
    emit_json_map(output, item)


def capture_image():
    '''
    create in memory image
    '''
    my_stream = io.BytesIO()
    with PiCamera() as camera:
        if DEBUG:
            print("camera.revision = {}".format(camera.revision))
            print("camera.MAX_RESOLUTION = {}".format(camera.MAX_RESOLUTION))
            print("default camera.resolution = {}".format(camera.resolution))
        # disable LED on camera
        camera.led = False
        camera.resolution = camera.MAX_RESOLUTION
        if DEBUG:
            print("camera.resolution = {}".format(camera.resolution))
        camera.start_preview()
        # Camera warm-up time
        sleep(MINIMUM_PREVIEW_TIME_IN_SECONDS)
        camera.capture(my_stream, 'jpeg', quality=100)
        camera.stop_preview()
        # get the data
        image = bytearray(my_stream.getvalue())
        if DEBUG:
            print("len(image) = {}".format(len(image)))

        return bytearray(image)

    
class Camera_HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    '''
    A subclass of BaseHTTPRequestHandler to provide camera output.
    '''

    def do_GET(self):
        '''
        handle the HTTP GET request
        '''
        global FAVICON
        global log_file

        if DEBUG:
            print('request path = "{}"'.format(self.path),
                  file=sys.stderr, flush=True)
        
        emit_event(log_file, 'request of "{}," from {}'.format(self.path,
                                                               self.client_address))
        # deal with site ICON 
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type','image/x-icon')
            self.end_headers()
            self.wfile.write(FAVICON)
            emit_event(log_file, 'done sending favicon.ico of length {}'.format(len(FAVICON)))
            return
        
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type','image/jpeg')
        self.end_headers()
        image=capture_image()
        self.wfile.write(image)
        emit_event(log_file, 'done sending image of length {}'.format(len(image)))
        return
    
    
    def log_message(self, format, *args):
        '''
        Silence output from server
        '''
        return

#
# main
#
if __name__ == '__main__':
   
    parser = argparse.ArgumentParser(description='web server to capture image from raspberry pi camera')
    parser.add_argument('-d', '--debug', 
                        help='turn on debugging', 
                        action='store_true')
    parser.add_argument('-a', '--address', 
                        help='v4 address for web server', 
                        default=DEFAULT_LISTEN_ADDRESS)
    parser.add_argument('-p', '--port', 
                        help='port number for web server', 
                        default=DEFAULT_LISTEN_PORT)
    parser.add_argument("-l", "--log_filename", 
                        help="file to log data, create or append", 
                        default=DEFAULT_LOG_FILE_NAME)
    args = parser.parse_args()

    if (args.debug):
        DEBUG = 1
        print('turned on DEBUG from command line.',
              file=sys.stderr, flush=True)

    log_filename = args.log_filename
    given_address = args.address
    given_port = int(args.port)

    server_address = (given_address, given_port)
    
    # open file to log pressure over time
    log_file = open(log_filename, 'a')
    emit_event(log_file, 'STARTING CameraServer')
    emit_event(log_file, 'address: {}'.format(server_address))
    
    with open(DEFAULT_ICON_FILE_NAME, 'rb') as icon_file:
        FAVICON = bytearray(icon_file.read())
    emit_event(log_file, 'read icon file of length = {}'.format(len(FAVICON)))
    if DEBUG:
        print('read icon file of length = {}'.format(len(FAVICON)),
              file=sys.stderr, flush=True)

    if DEBUG:
        print('log_filename = {}'.format(log_filename),
              file=sys.stderr, flush=True)
        print('server_address = {}'.format(server_address),
              file=sys.stderr, flush=True)

    httpd_server = HTTPServer(server_address,
                              Camera_HTTPServer_RequestHandler)
    
    if DEBUG:
        print('running server listening on {}...'.format(server_address),
              file=sys.stderr, flush=True)
    emit_event(log_file, 'entering httpd_server.serve_forever()')
    httpd_server.serve_forever()
