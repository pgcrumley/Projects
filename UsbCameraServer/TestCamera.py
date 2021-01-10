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

Capture a PNG camera image from the first USB camera and write a PNG file.
"""

import argparse
import cv2
import datetime
import sys

DEBUG = None

DEFAULT_LOG_FILE_NAME = 'test.log'
DEFAULT_FILE_NAME = 'test.png'

DEFAULT_VIDEO_DEVICE_STRING = '0'
DEFAULT_VIDEO_DEVICE = 0
MINIMUM_VIDEO_DEVICE = 0
MAXIMUM_VIDEO_DEVICE = 99

DEFAULT_SAMPLES_STRING = '3'
DEFAULT_SAMPLES = int(DEFAULT_SAMPLES_STRING)
MINIMUM_SAMPLES = 1
MAXIMUM_SAMPLES = 10

def capture_image(video_device=0, samples = 1):
    '''
    create in-memory image from USB camera
    '''
    try:
        # allow testing on Windows
        if sys.platform.startswith('win') or sys.platform.startswith('cyg'):
            print('Running on "{}".  Dealing with it...'.format(sys.platform), 
              file=sys.stderr, flush=True)
            cap = cv2.VideoCapture(video_device, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(video_device)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if DEBUG:
            print('sampling {} times'.format(samples),
                  file=sys.stderr, flush=True)
        for s in range(samples):
            _, frame = cap.read()
        _, im_buf_arr = cv2.imencode('.png', frame)
        result = im_buf_arr.tobytes()
        if DEBUG:
            print('captured image of length {}'.format(len(result)),
                  file=sys.stderr, flush=True)
        return bytearray(result)
    finally:
        cap.release()

def make_timestamp():
    '''
    Reduce some clutter
    '''
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

        
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
    parser.add_argument('-v', '--video_device', 
                        help='video device to use', 
                        default=DEFAULT_VIDEO_DEVICE_STRING)
    parser.add_argument("-s", "--samples", 
                        help="number of image samples to calibrate brightness", 
                        default=DEFAULT_SAMPLES_STRING)
    args = parser.parse_args()

    if (args.debug):
        DEBUG = 1
        print('turned on DEBUG from command line.',
              file=sys.stderr, flush=True)

    log_filename = args.log_filename
    output_filename = args.output_filename

    try:
        video_device = int(args.video_device)
    except Exception as ex:
        print('video_device value of "{}" is not legal, setting to "{}"'.format(video_device, DEFAULT_VIDEO_DEVICE_STRING),
              file=sys.stderr, flush=True)
        video_device = int(DEFAULT_SAMPLES_STRING)
    if video_device < MINIMUM_VIDEO_DEVICE or video_device > MAXIMUM_VIDEO_DEVICE:
        print('video_device value of {} is not legal, setting to {}'.format(video_device, DEFAULT_VIDEO_DEVICE),
              file=sys.stderr, flush=True)
        video_device = DEFAULT_VIDEO_DEVICE
    
    try:
        samples = int(args.samples)
    except Exception as ex:
        print('samples value of "{}" is not legal, setting to "{}"'.format(samples, DEFAULT_SAMPLES_STRING),
              file=sys.stderr, flush=True)
        samples = int(DEFAULT_SAMPLES_STRING)
    if samples < MINIMUM_SAMPLES or samples > MAXIMUM_SAMPLES:
        print('samples value of {} is not legal, setting to {}'.format(samples, DEFAULT_SAMPLES),
              file=sys.stderr, flush=True)
        samples = DEFAULT_SAMPLES

    # open file to log pressure over time
    with open(log_filename, 'a+') as log_file:
        log_file.write('{}: STARTING TestCamera\n'.format(make_timestamp()))
        log_file.flush()

        if DEBUG:
            print('log_filename = {}'.format(log_filename),
                  file=sys.stderr, flush=True)
            print('output_filename = {}'.format(output_filename),
                  file=sys.stderr, flush=True)
    
        with open(output_filename, 'bw') as output_file:
            image = capture_image(video_device, samples)
            log_file.write('{}: Captured image from device {} using {} samples\n'.format(make_timestamp(), video_device, samples))
            output_file.write(image)
            log_file.write('{}: Wrote image of length {} bytes to "{}"\n'.format(make_timestamp(), len(image), output_filename))
            log_file.flush()

        log_file.write('{}: ENDING TestCamera\n'.format(make_timestamp()))
        log_file.flush()
    exit(0)
