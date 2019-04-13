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
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import sys
from time import sleep

from picamera import PiCamera

DEBUG = None

DEFAULT_LISTEN_ADDRESS = '0.0.0.0'    # respond to request from any address
DEFAULT_LISTEN_PORT = '5000'            # IP port 5000
DEFAULT_SERVER_ADDRESS = (DEFAULT_LISTEN_ADDRESS, DEFAULT_LISTEN_PORT)

MINIMUM_PREVIEW_TIME_IN_SECONDS = 2


class Camera_HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    '''
    A subclass of BaseHTTPRequestHandler to provide camera output.
    '''

    # can be set to request something other than MAX_RESOLUTION
    default_resolution = None
    
    def do_GET(self):
        '''
        handle the HTTP GET request
        '''
        # Create an in-memory stream for image
        my_stream = io.BytesIO()
        with PiCamera() as camera:
            if DEBUG:
                print("camera.revision = {}".format(camera.revision))
                print("camera.MAX_RESOLUTION = {}".format(camera.MAX_RESOLUTION))
                print("default camera.resolution = {}".format(camera.resolution))
            # disable LED on camera
            camera.led = False
            if Camera_HTTPServer_RequestHandler.default_resolution:
                camera.resolution = Camera_HTTPServer_RequestHandler.default_resolution
            else:
                camera.resolution = camera.MAX_RESOLUTION
            if DEBUG:
                print("camera.resolution = {}".format(camera.resolution))
            camera.start_preview()
            # Camera warm-up time
            sleep(MINIMUM_PREVIEW_TIME_IN_SECONDS)
            camera.capture(my_stream, 'jpeg')
            camera.stop_preview()

        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','image/jpeg')
        self.end_headers()
        image = my_stream.getvalue()
        if DEBUG:
            print("len(image) = {}".format(len(image)))
                  
        self.wfile.write(my_stream.getvalue())
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
    parser.add_argument('-p', '--port', 
                        help='port number for web server', 
                        default=DEFAULT_LISTEN_PORT)
    parser.add_argument('-r', '--resolution', 
                        help='resolution of image', 
                        default=None)
    args = parser.parse_args()

    if (args.debug):
        DEBUG = 1
        print('turned on DEBUG from command line.',
              file=sys.stderr, flush=True)

    given_port = int(args.port)
    resolution = args.resolution
    
    server_address = (DEFAULT_LISTEN_ADDRESS,given_port)

    if DEBUG:
        print('server_address = {}'.format(server_address),
              file=sys.stderr, flush=True)
        print('requested camera resolution = {}'.format(resolution),
              file=sys.stderr, flush=True)

    httpd_server = HTTPServer(server_address,
                              Camera_HTTPServer_RequestHandler)
    if resolution:
        Camera_HTTPServer_RequestHandler.default_resolution = resolution
    if DEBUG:
        print('running server listening on {}...'.format(DEFAULT_SERVER_ADDRESS),
              file=sys.stderr, flush=True)
    httpd_server.serve_forever()
