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

Exercise a set of relays made by Etekcity using a 433 MHz transmitter connected
to a Raspberry Pi pin in order to determine the device addr value.

This assumes the 433 MHz transmitter is attached to the Raspberry Pi on pin 18.  
"""

import sys
import time

from etekcity_controller import Transmitter

# change  if the transmitter connected to a different board pin
TRANSMIT_PIN = 18
# try increasing this if the relays never turn on
RETRY_COUNT = 3
# you can increase this if the tries go by too fast
DELAY_TIME_IN_SECONDS = 0.5
LONG_DELAY_TIME_IN_SECONDS = 3.0

# first valid address is also default start addr
FIRST_VALID_ADDR = Transmitter.FIRST_VALID_ADDRESS
# last valid address is also default end addr
LAST_VALID_ADDR = Transmitter.LAST_VALID_ADDRESS

if len(sys.argv) > 1:
    if sys.argv[1] == '-h' or sys.argv[1] == '-?' or sys.argv[1] == '--help':
        print('usage: etekcity_try_addrs.py [start_addr [end_addr]]', 
              file=sys.stderr)
        print('    start and end must be between {} and {}', 
              FIRST_VALID_ADDR,
              LAST_VALID_ADDR,
              file=sys.stderr
              )
        print('    start must be <= end', file=sys.stderr)
        print('    start and end default to {} and {}',
              FIRST_VALID_ADDR,
              LAST_VALID_ADDR,
              file=sys.stderr
              )
        print('    setting start addr slows down tests', file=sys.stderr)
        exit(1)

start = FIRST_VALID_ADDR
end = LAST_VALID_ADDR
delay = DELAY_TIME_IN_SECONDS

if len(sys.argv) > 1:
    try:
        start = int(sys.argv[1])
        delay = LONG_DELAY_TIME_IN_SECONDS
    except Exception as e:
        print('start_addr parameter of "{}" is not between {} to {}',
              sys.argv[1], 
              FIRST_VALID_ADDR,
              LAST_VALID_ADDR,
              file=sys.stderr
              )
        exit(2)
if len(sys.argv) > 2:
    try:
        end = int(sys.argv[2])
    except Exception as e:
        print('end_addr parameter of "{}" is not between {} to {}',
              sys.argv[2],
              FIRST_VALID_ADDR,
              LAST_VALID_ADDR,
              file=sys.stderr
              )
        exit(2)

if start < FIRST_VALID_ADDR or start > LAST_VALID_ADDR:
    print('start_addr of {} must be between {} and {} inclusive', 
          start,
          FIRST_VALID_ADDR,
          LAST_VALID_ADDR,
          file=sys.stderr
          )
    exit(2)

if end < FIRST_VALID_ADDR or end > LAST_VALID_ADDR:
    print('end_addr of {} must be between {} and {} inclusive', 
          end,
          FIRST_VALID_ADDR,
          LAST_VALID_ADDR,
          file=sys.stderr
          )
    exit(2)

if start > end:
    print('start_addr must be <= end_addr', file=sys.stderr)
    exit(2)


print('looking for addrs between {} and {}'.format(start, end))

ec = Transmitter(TRANSMIT_PIN, retries=RETRY_COUNT)
for addr in range(start, end+1):
    print('addr {}'.format(addr))
    for unit in [1, 2, 3, 4, 5]:
        if Transmitter.ALL_ADDRESS == addr and Transmitter.ALL_UNIT == unit:
            print('skipping address {} and unit {} as they are special'.format(
                Transmitter.ALL_ADDRESS, Transmitter.ALL_UNIT))
        else:
            ec.transmit_on(addr, unit)
    time.sleep(DELAY_TIME_IN_SECONDS)
    for unit in [1, 2, 3, 4, 5]:
        if Transmitter.ALL_ADDRESS == addr and Transmitter.ALL_UNIT == unit:
            print('skipping address {} and unit {} as they are special'.format(
                Transmitter.ALL_ADDRESS, Transmitter.ALL_UNIT))
        else:
            ec.transmit_off(addr, unit)
