#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2017, 2019 Paul G Crumley

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

Periodically query a the state of a Mighty Mule Drive Alarm which is
connected, via an Arduino, to a serial port.

lines of JSON are sent to the log file when a visitor is detected or
when the LOW_BATTERY LED changes state.
                
"""

import argparse
import datetime
import json
import serial
import sys
import time

DEBUG = 0

PORT_SPEED = 115200
TIMEOUT_IN_SEC = 2.0
RESET_TIME_IN_SEC = 3.0

NL = '\n'.encode('UTF-8')
READ_STATUS_COMMAND = '?'.encode('UTF-8')
READ_VERSION_COMMAND = '`'.encode('UTF-8')

DEFAULT_SAMPLE_INTERVAL_IN_SECONDS = 15
DEFAULT_LOG_FILE_NAME = '/opt/Projects/logs/MightyMuleMonitor.log'


def emit_json_map(output, json_map):
    '''
    generate a time stamp in UTC for use in the output
    
    A 'time' entry with the time stamp is added to the json_map.
    '''
    when = datetime.datetime.now(datetime.timezone.utc)
    when_str = when.isoformat()
    json_map['time'] = when_str
    output.write('{}\n'.format(json.dumps(json_map)))
    output.flush()


def emit_event(output, event_text):
    '''
    send a line with an event to the output with a time stamp
    '''
    item = {'event':event_text}
    emit_json_map(output, item)

    
def emit_sample(output, controller_name, data_map):
    '''
    send a line with data_map to the output with a time stamp
    '''
    data_map['name'] = controller_name
    emit_json_map(output, data_map)

    
#
# main
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture and log GPIO pin data from an Arduino attached via a serial port.")
    parser.add_argument("-d", "--debug", 
                        help="turn on debugging", 
                        action="store_true")
    parser.add_argument("-l", "--log_filename", 
                        help="file to log data, create or append", 
                        default=DEFAULT_LOG_FILE_NAME)
    parser.add_argument("-p", "--port", 
                        help="port to which Arduino is connected", 
                        default=None)
    parser.add_argument("-i", "--interval", 
                        help="how often to sample sensors in seconds", 
                        default=DEFAULT_SAMPLE_INTERVAL_IN_SECONDS)
    args = parser.parse_args()

    if (args.debug):
        DEBUG = 1
        print('turned on DEBUG from command line.',
              file=sys.stderr, flush=True)

    log_filename = args.log_filename
    sample_interval = int(args.interval)
    given_port = args.port
    
    if DEBUG:
        print('log_filename = {}'.format(log_filename),
              file=sys.stderr, flush=True)
        print('sample_interval = {}'.format(sample_interval),
              file=sys.stderr, flush=True)
        print('given_port = {}'.format(given_port),
              file=sys.stderr, flush=True)

    if sample_interval < 0:
        sample_interval = 0
        if DEBUG:
            print('negative sample interval set to 0',
                  file=sys.stderr, flush=True)

    if not given_port:
        print('port must be specified',
              file=sys.stderr, flush=True)
        exit(1)

    # holds connection to controller
    controller = None
    
    # open file to log pressure over time
    with open(log_filename, 'a') as output_file:

        emit_event(output_file, 'STARTING MightyMuleMonitor')

        # Look for changes in low_battery state
        previous_low_battery_state = False
    
        next_sample_time = time.time()
        while True:

            # if controller is None we'll try to re-connect
            if controller is None:
                try:
                    # get serial port access for each serial device
                    controller = serial.Serial(given_port, 
                                               PORT_SPEED, 
                                               timeout=TIMEOUT_IN_SEC)
                    # give Arduino time to reset after serial open causes a reset
                    time.sleep(RESET_TIME_IN_SEC)  
                    v='<TBD>'
                    try:
                        controller.write(READ_VERSION_COMMAND)
                        controller.flush()
                        v = controller.readline().decode('UTF-8').strip()
                    except:
                        v = None
                        raise RuntimeError('invalid version of "{}" received from device'.format(v))
                    if DEBUG:
                        print('created SerialArduinoGpioController for "{}"'.format(given_port),
                              file=sys.stderr, flush=True)
                        print('found version of {}'.format(v),
                              file=sys.stderr, flush=True)
    
                    emit_event(output_file, 'connected on port {} found {}'.format(given_port, v))
                except:
                    # if needed clean up
                    if controller:
                        controller.close()
                    controller = None  # just to be sure

            # only try to read a sample if the controller is available
            if controller is not None:
                # try to get and process a sample
                try:
                    controller.write(READ_STATUS_COMMAND)
                    controller.flush()
                    line = controller.readline().decode('UTF-8').strip()
                    if DEBUG:
                        print('line from controller is "{}"'.format(line),
                              file=sys.stderr, flush=True)
                    data = json.loads(line)
                    if DEBUG:
                        print('data from controller is "{}"'.format(data),
                              file=sys.stderr, flush=True)
                    if 'visitor_count' in data:
                        if data['visitor_count'] > 0:
                            emit_sample(output_file, given_port, {'visitor_count':data['visitor_count']} )
                    if 'low_battery' in data:
                        if previous_low_battery_state != data['low_battery']:
                            this_low_battery = data['low_battery']
                            emit_sample(output_file, given_port, {'low_battery':this_low_battery})
                            previous_low_battery_state = this_low_battery
                except Exception as e:
                    event_text = 'While reading controller {} caught exception of {}.  removing'.format(given_port, e)
                    emit_event(output_file, event_text)
                    controller.close()
                    controller = None
                    if DEBUG:
                        print(event_text.format(),
                              file=sys.stderr, flush=True)
                    
            # wait till next sample time            
            next_sample_time = next_sample_time + sample_interval
            delay_time = next_sample_time - time.time()
            if DEBUG:
                print('delay_time = {}'.format(delay_time),
                      file=sys.stderr, flush=True)
        
            if 0 < delay_time:  # don't sleep if already past next sample time
                time.sleep(delay_time)
