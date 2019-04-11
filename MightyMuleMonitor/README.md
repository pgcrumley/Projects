# Mighty Mule Monitor

This software, when combined with a gently modified 
[Mighty Mule driveway alarm](https://www.mightymulestore.com/Mighty-Mule-Driveway-Alarm-p/fm231.htm),
allows a service to monitor when the alarm is activated.

The 
Since the Arduino gets power from the USB connection no
extra power supply is needed.  This arrangement allows the controlling
system to 
control powered devices with a less direct connection to hazardous voltages.

The use of USB allows relatively long distances
between the controlling system and the controlled device.  
(e.g. some USB extenders can 
reach 100 meters).  One may also have many GPIO ports on a single 
controlling system
by connecting many Arduinos (each supports 12 GPIO pins and 6 or more
analog signala) to USB ports.

The python code provides a simple interface to the functions, allowing one
to set a pin HIGH (which puts the pin in INPUT_PULLUP mode) or
LOW which (which sets OUTPUT mode with a value of LOW)

This use of a pullup for HIGH values allows pins to be used a inputs 
or outputs with minimal fuss or danger.

A command to save the current pin state to be used when the device is
reset is also provided as some devices need particular values at startup.

It is also possible to place a persistent name (16 characters) in to the 
Arduino so even if the USB ports get renamed over time you can keep track
of which Arduino is connected to various signals.

### Configure the software (15 minutes -- longer if system is not up-to-date)

This is for Raspberry Pi or Ubuntu Linux.  Setup on other systems varies.

Install python3 using a command of:

    sudo apt-get -y install python3 python3-dev git
    
Install a python serial library using a command of:

    pip3 install -r requirements.txt

Make sure `python3` works and RPi.GPIO is installed by typing:

    python3
    import serial
    exit()

Your console should look like this:

    $ python3
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import serial
    >>> exit()
    $

The version numbers may vary but there should not be any messages after the
`import serial` line.    

### Install the software in the Raspberry Pi (5 minutes)

The software and scripts assume the software is installed in `/opt`, a
standard directory for "optional" software.  To install the software use

    sudo sh -c 'cd /opt ; git clone https://github.com/pgcrumley/Controllers.git'

This will place a copy of the software in `/opt` and leave behind
information that makes it easy to retrieve updates later if needed.

Next 

    cd /opt/Controllers/SerialArduinoGpio/
    
and make sure there are a number of python programs and other scripts present.

### Attach Arduino to development system and program sketch. (15 minutes)

If you are new to Arduino you probably want to do some of the
[tutorials](https://www.arduino.cc/en/Tutorial/HomePage)

If you use a system other than your Raspberry Pi as your Arduino development
system you will need to get a copy of the `SerialArduinoGpio.ino` file
to the development system.  

Attach your Arduino to your development computer (which might be your 
Raspbery Pi) and download the sketch called `SerialArduinoGpio.ino`
using the normal Arduino tools.  

You can use the serial port of the IDE to try out the operation of the 
Arduino.  Remember to set the serial port speed to 115200.

You can read all the pin values with '?'  The version command '`' (that 
is back-tic) prints a version number.


 
### Enjoy! 






