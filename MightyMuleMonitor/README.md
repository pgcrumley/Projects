# Mighty Mule Monitor

This software, when combined with a gently modified 
[Mighty Mule driveway alarm](https://www.mightymulestore.com/Mighty-Mule-Driveway-Alarm-p/fm231.htm),
allows a service to monitor when the alarm is activated.

Since the Arduino gets power from the USB connection no
extra power supply is needed.  This arrangement allows the monitoring
system to interact with powered
devices with a less direct connection to hazardous voltages.

The code provides a simple program which checks the state of the 
VISITOR and LOW BATTERY LEDs on the Mighty Mule Driveway Alarm control box
every 15 seconds and when some change is detected the change is logged to 
a file and for the VISITOR LED, the LED is RESET so additional visitors
can be detected.

By default the JSON log file is stored in 
/opt/Projects/logs/MightMuleMonitor.log

### Configure the software (15 minutes -- longer if system is not up-to-date)

This is for Raspberry Pi or Ubuntu Linux.  Setup on other systems varies.

Become root for the next few operations:

    sudo su -
    
This will pull in many projects.  You can trim later if you like:

    cd /opt
    git clone https://github.com/pgcrumley/Projects.git
    cd Projects/MightyMuleMonitor

Install python3 using a command of:

    apt-get update
    apt-get -y install python3 python3-dev git
    
Install a python serial library using a command of:

    pip3 install -r requirements.txt

Make sure `python3` works and RPi.GPIO is installed by typing:

    python3
    import serial
    exit()

Your console should look like this:

    # python3
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import serial
    >>> exit()
    #
    
The version numbers may vary but there should not be any messages after the
`import serial` line.    

Exit root access

    exit

### Attach Arduino to development system and program sketch. (15 minutes)

If you are new to Arduino you probably want to do some of the
[tutorials](https://www.arduino.cc/en/Tutorial/HomePage)

If you use a system other than your Raspberry Pi as your Arduino development
system you will need to get a copy of the `MightyMuleMonitor.ino` file
to the development system.  

Attach your Arduino to your development computer (which might be your 
Raspbery Pi) and download the sketch called `MightyMuleMonitor.ino`
using the normal Arduino tools.  

You can use the serial port of the IDE to try out the operation of the 
Arduino.  Remember to set the serial port speed to 115200.

You can read the state of the LEDs with the '?' command.  
The version command '`' (that 
is back-tic) prints the version of the image loaded in the Arduino.

### Assemble the interface card

This card allows the Arudino to safely monitor the LEDs and activate the 
RESET button on the Mighty Mule Driveway Arlarm control box.

## Assembly details will be posted soon

### Connect the Arduino to your system and run the monitor program

In this example a Raspberry Pi is used to run the monitor.  
Before connecting the device to a USB port run the command

    ls /dev/tty*
    
This gives the "before" list of serial port.  Now connect the Arduino to a 
USB port on the Raspberry Pi then look for the port with 

    ls /dev/tty*
    
You should see a new serial port has appeared.
If the name is `/dev/ttyUSB0` your port is the same as the default.  If
some other name is new you will need that value soon.

Run the monitor program to ensure the device is operating as expected.
If your USB port is different substitute that name for `USB0`.

    sudo su -
    cd /opt/Projects/MightyMuleMonitor
    ./MightyMuleMonitor -d -p /dev/ttyUSB0
    
You should see messages that the device is found.  Try to active the driveway 
alarm and make sure it sees the visitor.  Kill this program with `^C`

Check to make sure the log is being written with 

    cat /opt/Projects/logs/MightMuleMonitor.log
    
If all looks good you may create a service to run the monitor without 
intervention with the `MightyMuleMonitor.service`.

    
If your serial port name was not `/dev/ttyUSB0` you will need to change
the default value in the file.  Use your favorite editor to change the
value in `/lib/systemd/system/MightMuleMonitor.service`.

Now enable the service to start after reboot with

    systemctl enable MightMuleMonitor

You can start the monitor now and check its status with 

    systemctl start MightMuleMonitor
    systemctl status MightMuleMonitor
    
If the status is good look at the log file to make sure it was started and 
has access to write the log

Leave root access mode with 

    exit
    
### Enjoy! 

Congratulations!  Your system is now monitoring your driveway.

You can add new actions to the monitor program to do things like send an SMS
or update a web page when the alarm detects a visitor.

If you have an interesting action for the alarm I would love to learn what you
have done.

Enjoy!