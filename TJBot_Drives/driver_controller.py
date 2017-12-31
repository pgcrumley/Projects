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


The basic control operation is:
  drive(op, time_in_seconds)
    where op is "idle", "forward", "backward", "left", "right", "cw", or "ccw"
    time_in_seconds is how long to do the operation
    
    "op" values are recognized for any case of the parameter, e.g. "CW" or "cw"
"""

import sys
import time
import RPi.GPIO as GPIO

DEBUG = True

class Controller:
    """
    Create a controller for operations.  
    
    Pin numbers are Raspberry Pi board numbers, not GPIO numbers.
    """
    _VALID_PINS = [3, 5, 7, 8, 10, 
                   11, 12, 13, 15, 16, 18, 19, 
                   21, 22, 23, 24, 26, 29, 
                   31, 32, 33, 35, 36, 37, 38, 40]

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
        Mark controller as dead, turn off motors, and release resources.
        """
        
        self.__alive = False
        # turn off all motor signals
        self.set_motor_signals(False, False, False, False)
        # make sure we can't set signals anymore
        self._RIGHT_FORWARD_PIN = None
        self._RIGHT_BACKWARD_PIN = None
        self._LEFT_FORWARD_PIN = None
        self._LEFT_BACKWARD_PIN = None
        # let other processes use the GPIO pins
        GPIO.cleanup()
            
    def set_motor_signals(self, rf, rb, lf, lb):
        """
        Transmit a signal for the given motor pattern.
        rf, rb, lf, lb are right forward / backward and left forward / backward
        """
        if DEBUG:
            print('entering __transmit:',
                  file=sys.stderr)
            print('  rf, rb, lf, lb:  {} {} {} {}'.format(rf, rb, lf, lb),
                  file=sys.stderr)
        
        # set appropriate pins LOW
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
        
        if DEBUG:
            print('leaving __transmit:',
                  file=sys.stderr)


    def drive(self, op, time_in_seconds):
        """
        Send the proper signals on the GPIO pins 

        op is "idle", "forward", "backward", "left", "right", "cw", or "ccw"
        time_in_seconds is how long to do the operation
    
        "op" values are recognized for any case of the parameter.
        """

        if DEBUG:
            print('entering drive:',
                  file=sys.stderr)
            print('  op =              "{}"'.format(op), file=sys.stderr)
            print('  time_in_seconds = {}'.format(time_in_seconds),
                  file=sys.stderr)
        
        if not self.__alive:
            raise RuntimeError('Controller has been closed')
        
        # ignore case of op parameter
        lc_op = op.lower()
        
        # special case for 0 time_in_seconds
        if (time_in_seconds <= 0):
            return

        try:
            # now send the appropriate signals
            if 'forward' == lc_op:
                self.set_motor_signals(True, False, True, False)
            elif 'backward' == lc_op:
                self.set_motor_signals(False, True, False, True)
            elif 'right' == lc_op:
                self.set_motor_signals(False, False, True, False)
            elif 'left' == lc_op:
                self.set_motor_signals(True, False, False, False)
            elif 'cw' == lc_op:
                self.set_motor_signals(False, True, True, False)
            elif 'ccw' == lc_op:
                self.set_motor_signals(True, False, False, True)
            elif 'idle' == lc_op:
                self.set_motor_signals(False, False, False, False)
            else:
                raise ValueError('op of "{}" is not defined'.format(op))
    
            # drive for indicated amount of time
            time.sleep(time_in_seconds)
        finally:
            # always turn off motors
            self.set_motor_signals(False, False, False, False)

        if DEBUG:
            print('leaving drive:',
                  file=sys.stderr)

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
    
    controller = Controller()
    controller.drive(op, speed, duration)
    
    controller.close()
    