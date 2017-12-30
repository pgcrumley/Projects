#!/usr/bin/python3
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

Try to turn off all relays made by Etekcity using a 433 MHz transmitter
connected to a Raspberry Pi pin.

This assumes the 433 MHz transmitter is attached to the Raspberry Pi on pin 18.  
"""

import sys

from etekcity_controller import Transmitter

# change  if the transmitter connected to a different board pin
TRANSMIT_PIN = 18
# try increasing this if the relays never turn off
RETRY_COUNT = 6

if '__main__' == __name__:
    if len(sys.argv) > 1:
        print('usage: etekcity_all_off.py', file=sys.stderr)
        print('    Try to turn off all devices', file=sys.stderr)
        exit(1)
    
    ec = Transmitter(TRANSMIT_PIN, retries=RETRY_COUNT)
    ec.transmit_all_off()
