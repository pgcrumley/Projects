#!/usr/bin/python3
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

Control an RC vehicle with a Raspberry Pi via GPIO pins.

The vehicle is a TOYDALOO dump truck.

Operation  L motor  R motor  Description
  Idle       -        -      No motion
  Forward    F        F      Travel forward
  Backward   B        B      Travel backward
  Right      F        -      Turn right
  Left       -        F      Turn left
  CW         F        B      Spin clockwise
  CCW        B        F      Spin counter-clockwise

There are 10 speeds from 1-10.  10 is maximum speed and 1 is a 10% duty cycle.

A speed of 0 for any of the above operations results in no motion.  
The "idle" operation at any speed results in no motion.

The basic control operation is:
  drive(op, speed, time_in_seconds)
    where op is "idle", "forward", "backward", "left", "right", "cw", or "ccw"
    speed is a number between 0 and 10, inclusive.  0 is no motion
    time_in_seconds is how long to do the operation
    
    "op" values are recognized for any case of the parameter.
"""

import sys
import time
import RPi.GPIO as GPIO
from msilib import _Unspecified

DEBUG = False

class Controller:
    """
    Create a controller for operations.  
    
    Pin numbers are Raspberry Pi board numbers, not GPIO numbers.
    """
    _RIGHT_FORWARD_PIN = 0
    _RIGHT_BACKWARD_PIN = 0
    _LEFT_FORWARD_PIN = 0
    _LEFT_BACKWARD_PIN = 0
    
    _VALID_PINS = [3, 5, 7, 8, 10, 
                   11, 12, 13, 15, 16, 18, 19, 
                   21, 22, 23, 24, 26, 29, 
                   31, 32, 33, 35, 36, 37, 38, 40]

    _PERIOD_IN_SECONDS = 0.1  # each signal is 100 milliseconds in length


    def __init__(self, 
                 right_forward_pin = 24,
                 right_backward_pin = 26,
                 left_forward_pin = 29,
                 left_backward_pin = 31):
        """
        Create a controller and set up the IO parameters.
        """
        if right_forward_pin not in Controller._VALID_PINS:
            raise ValueError('right_forward_pin of {} must be in {}'.format(
                right_forward_pin,
                Controller._VALID_PINS
                )
            )
        self._RIGHT_FORWARD_PIN = right_forward_pin

        if right_backward_pin not in Controller._VALID_PINS:
            raise ValueError('right_backward_pin of {} must be in {}'.format(
                right_backward_pin,
                Controller._VALID_PINS
                )
            )
        self._RIGHT_BACKWARD_PIN = right_backward_pin

        if left_forward_pin not in Controller._VALID_PINS:
            raise ValueError('left_forward_pin of {} must be in {}'.format(
                left_forward_pin,
                Controller._VALID_PINS
                )
            )
        self._LEFT_FORWARD_PIN = left_forward_pin

        if left_backward_pin not in Controller._VALID_PINS:
            raise ValueError('leftt_backward_pin of {} must be in {}'.format(
                left_backward_pin,
                Controller._VALID_PINS
                )
            )
        self._LEFT_BACKWARD_PIN = left_backward_pin

        # make sure there are 4 unique pins specified
        pin_set = set()
        pin_set.add(self._RIGHT_FORWARD_PIN)
        pin_set.add(self._RIGHT_BACKWARD_PIN)
        pin_set.add(self._LEFT_FORWARD_PIN)
        pin_set.add(self._LEFT_BACKWARD_PIN)
        if 4 != len(pin_set):
            raise ValueError('the specified pins were not all unique')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._RIGHT_FORWARD_PIN, GPIO.OUT)
        GPIO.output(self._RIGHT_FORWARD_PIN, GPIO.HIGH)
        GPIO.setup(self._RIGHT_BACKWARD_PIN, GPIO.OUT)
        GPIO.output(self._RIGHT_BACKWARD_PIN, GPIO.HIGH)
        GPIO.setup(self._LEFT_FORWARD_PIN, GPIO.OUT)
        GPIO.output(self._LEFT_FORWARD_PIN, GPIO.HIGH)
        GPIO.setup(self._LEFT_BACKWARD_PIN, GPIO.OUT)
        GPIO.output(self._LEFT_BACKWARD_PIN, GPIO.HIGH)

        self.__alive = True

    def close(self):
        """
        Release resources and mark controller as dead
        """
        self.__alive = False
        self._RIGHT_FORWARD_PIN = None
        self._RIGHT_BACKWARD_PIN = None
        self._LEFT_FORWARD_PIN = None
        self._LEFT_BACKWARD_PIN = None
        GPIO.cleanup()
            
    def __transmit_(self, rf, rb, lf, lb, duty_cycle, count):
        """
        Transmit a number of signal sequences with a given duty cycle.
        rf, rb, lf, lb are right forward / backward and left forward / backward
        duty_cycle is a number between 1 and 10, inclusive.
        count is the number of time periods to send.  
        
        Each cycle of _PERIOD_IN_SECONDS long and the duty cycle sent is 
        duty_cycle * _PERIOD_IN_SECONDS / 10.
        """
        
        if (count < 0):
            raise ValueError('count of {} was not >= to 0'.format(count))
        
        # special case for 0 duty_cycle
        if (0 == duty_cycle):
            time.sleep(count * Controller._PERIOD_IN_SECONDS)
        
        if duty_cycle not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            raise ValueError('duty_cycle of {} is not an integer between 1 and 10 inclusive'.format(duty_cycle))
        
        low_time = (duty_cycle * Controller._PERIOD_IN_SECONDS) / 10
        high_time = ((10 - duty_cycle) * Controller._PERIOD_IN_SECONDS) / 10
        for c in range(count):
            # set appropriate pins LOW
            GPIO.output()
            if rf:
                GPIO.output(self._RIGHT_FORWARD_PIN, GPIO.LOW)
            else:
                GPIO.output(self._RIGHT_FORWARD_PIN, GPIO.HIGH)
            if rb:
                GPIO.output(self._RIGHT_BACKWARD_PIN, GPIO.LOW)
            else:
                GPIO.output(self._RIGHT_BACKWARD_PIN, GPIO.HIGH)
            if lf:
                GPIO.output(self._LEFT_FORWARD_PIN, GPIO.LOW)
            else:
                GPIO.output(self._LEFT_FORWARD_PIN, GPIO.HIGH)
            if lb:
                GPIO.output(self._LEFT_BACKWARD_PIN, GPIO.LOW)
            else:
                GPIO.output(self._LEFT_BACKWARD_PIN, GPIO.HIGH)
            time.sleep(low_time)

            # turn off motors
            GPIO.output(self._RIGHT_FORWARD_PIN, GPIO.HIGH)
            GPIO.output(self._RIGHT_BACKWARD_PIN, GPIO.HIGH)
            GPIO.output(self._LEFT_FORWARD_PIN, GPIO.HIGH)
            GPIO.output(self._LEFT_BACKWARD_PIN, GPIO.HIGH)
            time.sleep(low_time)



    def drive(self, op, speed, time_in_seconds):
        """
        Send the proper signals on the GPIO pins 

        op is "idle", "forward", "backward", "left", "right", "cw", or "ccw"
        speed is a number between 0 and 10, inclusive.  0 is no motion
        time_in_seconds is how long to do the operation
    
        "op" values are recognized for any case of the parameter.
        """
        
        if not self.__alive:
            raise RuntimeError('Controller has been closed')
        
        # ignore case of op parameter
        lc_op = op.lower()

        # special case for 0 speed parameter or "idle" op
        if (0 == speed or 'idle' == lc_op):
            time.sleep(time_in_seconds)
            return
        
        # special case for 0 time_in_seconds
        if (time_in_seconds <= 0):
            return

        # determine when to be done
        done_time = time.time() + time_in_seconds

        # if not 0, make sure this is a value speed number
        if duty_cycle not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            raise ValueError('speed of {} is not an integer between 1 and 10 inclusive'.format(speed))
        
        # determine how many cycles of signal to send -- round down
        count = int(time_in_seconds / Controller._PERIOD_IN_SECONDS)

        # now send the appropriate signals
        if 'forward' == lc_op:
            self.__transmit_(True, False, True, False, speed, count)
        elif 'backward' == lc_op:
            self.__transmit_(False, True, False, True, speed, count)
        elif 'right' == lc_op:
            self.__transmit_(False, False, True, False, speed, count)
        elif 'left' == lc_op:
            self.__transmit_(True, False, False, False, speed, count)
        elif 'cw' == lc_op:
            self.__transmit_(False, True, True, False, speed, count)
        elif 'ccw' == lc_op:
            self.__transmit_(True, False, False, True, speed, count)
        else:
            raise ValueError('op of "{}" is not defined'.format(op))
        
        # don't be done too soon
        delay_time = done_time - time.time()
        if delay_time > 0:
            time.sleep(delay_time)

    #
    # end of class Controller        
    #
    
def usage():
    print('usage:  driver_controller.py op speed, duration',
          file=sys.stderr)    
    print('          op is "forward", "backward", "right", "left", "cw", "ccw"',
          file=sys.stderr)    
    print('          speed is an integer between 1 and 10 inclusive',
          file=sys.stderr)    
    print('          duration is time for operation in seconds',
          file=sys.stderr)    
    exit(1)

if '__main__' == __name__ :
    """
    Simple command to drive.
    """
    
    ## normal case
    if 4 != len(sys.argv):
        print('len(sys.argv) is {}'.format(len(sys.argv)), file=sys.stderr)
        usage()

    op = sys.argv[1]
    speed = int(sys.argv[2])
    duration = float(sys.argv[3])

    if DEBUG:
        print('op:        "{}"'.format(op), file=sys.stderr)
        print('speed:     {}'.format(speed), file=sys.stderr)
        print('duration:  {}'.format(duration), file=sys.stderr)
    
    controller = Controller(board_pin)
    controller.drive(op, speed, duration)
    
    controller.close()
    