#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2020 Paul G Crumley

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

Very simple web server to provide a PNG camera image from the first USB camera
and write a PNG file.
"""

import argparse
import cv2
import sys

DEBUG = None

DEFAULT_LOG_FILE_NAME = 'test.log'
DEFAULT_FILE_NAME = 'test.png'


def capture_image():
    '''
    create in-memory image from first USB camera
    '''
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        _, frame = cap.read()
        _, im_buf_arr = cv2.imencode('.png', frame)
        result = im_buf_arr.tobytes()
        if DEBUG:
            print('captured image of length {}'.format(len(result)),
                  file=sys.stderr, flush=True)
        return bytearray(result)
    finally:
        cap.release()
        
#
# main
#
if __name__ == '__main__':
   
    parser = argparse.ArgumentParser(description='web server to capture PNG image from first USB camera')
    parser.add_argument('-d', '--debug', 
                        help='turn on debugging', 
                        action='store_true')
    parser.add_argument('-o', '--output_filename', 
                        help='output PNG file name', 
                        default=DEFAULT_FILE_NAME)
    parser.add_argument("-l", "--log_filename", 
                        help="file to log data, create or append", 
                        default=DEFAULT_LOG_FILE_NAME)
    args = parser.parse_args()

    if (args.debug):
        DEBUG = 1
        print('turned on DEBUG from command line.',
              file=sys.stderr, flush=True)

    log_filename = args.log_filename
    output_filename = args.output_filename

    # open file to log pressure over time
    with open(log_filename, 'a+') as log_file:
        log_file.write('STARTING TestCamera\n')
        log_file.flush()

        if DEBUG:
            print('log_filename = {}'.format(log_filename),
                  file=sys.stderr, flush=True)
            print('output_filename = {}'.format(output_filename),
                  file=sys.stderr, flush=True)
    
        with open(output_filename, 'bw') as output_file:
            image = capture_image()
            output_file.write(image)
            log_file.write('wrote image of length {} bytes to "{}"\n'.format(len(image), output_filename))
            log_file.flush()

        log_file.write('ENDING TestCamera\n')
        log_file.flush()
    exit(0)
