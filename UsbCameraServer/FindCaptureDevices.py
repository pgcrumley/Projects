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

look for cameras in the range of 0-99

Run with root authority.
"""

import os
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'  # work around for OpenCV warning issue
import cv2

LAST_DEVICE_TO_TRY = 99

def find_capture_devices():
    '''
    return a list of the available capture devices
    '''
    result = list()
    for dev in range(0,LAST_DEVICE_TO_TRY+1):
        try:
            cap = cv2.VideoCapture(dev)
            if cap.isOpened():
                result.append(dev)
        finally:
            cap.release()
    return result        
        
#
# main
#
if __name__ == '__main__':
    print('Searching for capture devices...')
    available_devices = find_capture_devices()
    print('Available devices: {}'.format(available_devices))
    