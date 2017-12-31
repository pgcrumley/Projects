# TJBot Drives!

Sure, [TJBot](https://github.com/ibmtjbot/tjbot)
can't walk but there are other ways to be mobile.

This project will give TJBot the ability to control an RC truck to
provide mobility.  It uses an inexpensive RC vehicle because some hardware
{hacking} will be required and one might not want to open the covers on
an expense device.

A soldering iron and some basic electronic experience will help with this 
project but with care this can be done as a first experience with both.

#### Materials Needed:  

1. TJBot
2. A suitable RC vehicle (ones that use two 1.5 volt batteries are preferred)
3. Soldering iron and solder
4. Several proto-board jumpers (one end will be cut off)

Once you have the RC vehicle you will have a better understaning of what 
else is needed to conenct it to the Raspberry Pi in the TJBot.

## Construction

#### Install the software in the Raspberry Pi (5 minutes)

The software and scripts assume the software is installed in `/opt`, a
standard directory for "optional" software.  To install the software use

    sudo sh -c 'cd /opt ; git clone https://github.com/pgcrumley/Projects.git'

This will place a copy of the software in `/opt` and leave behind
information that makes it easy to retrieve updates later if needed.

Next 

    cd /opt/Controllers/TJBot_Drives/
    
and make sure there are
a number of python and other scripts present.

### Configure the software (15 minutes -- longer if system is not up-to-date)

Install python3 and the RPi.GPIO library using a command of:

    sudo apt-get -y install python3 python3-dev git python3-rpi.gpio

Make sure `python3` works and RPi.GPIO is installed by typing:

    python3
    import RPi.GPIO
    exit()

Your console should look like this:

    $ python3
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import RPi.GPIO
    >>> exit()
    $

The version numbers may vary but there should not be any messages after the
`import RPi.GPIO` line.    

#### Connect pigtails to the RC controller buttons (30 minutes)

This step will require soldering ability and you will void any warranty
on the RC device.  If you need help with solding I would refer you to some 
[soldering advice](http://www.instructables.com/id/How-to-Solder-Basic-Soldering-Guide/)
for more information.




#### Test the transmitter operation. (5 minutes)

Once the transmitter is connected power up your Raspberry Pi.  Login and 
return to `/opt/Controllers/Etekcity` 
with `cd /opt/Controllers/Etekcity`

Make sure the transmistter works by running the command:

    sudo ./etekcity_all_on.py

All the outlet switches should turn on and the LEDs should be glowing red.

If the switches do not turn on insert a jumper wire in to the hole on the 
transmitter board labelled `ANT` as shown in 
[this photo](./images/antenna.png).  The wire will provide more strength
to the transmitted signal improving the reliability and distance between
the transmitter and the devices.

    sudo ./etekcity_all_off.py

will turn all the devices off.

If the devices do not turn on and off with these commands check all the 
wiring.  If the wires look correct swap in one of the 4 other transmitter
boards and try again.

Turn off all the devices before proceeding.

### Determine the address for the outlet switches. (5 minutes)

This next command will cycle through all the addresses trying to turn each
device on then off before proceeding to the next address.

`sudo ./etekcity_try_addrs.py`

Watch the screen so you see the address that turned the devices on then off.

Please note that address 85 with unit 3 is special and will be skipped.

If you miss the exact address on which the devices respond you can run the 
command with parameters to set the first and last address to try.  Setting the 
start and end address also slows down the process so you have more time to 
see which address works for your devices.

    sudo ./etekcity_try_addrs.py [first_address last_address]

To make sure you have the right address try the command with that address for
both the `first_address` and the `last_address` to make sure the 
device responds.

#### Use the controller command to turn devices on and off. (2 minutes)

You can control devices with the the `etekcity_controller.py` command.
This command takes 4 parameters of the `transmitter pin`, 
`address`, `unit`, and `on` | `off`

This requires root authority so the program can control the hardware pins.
An example of a command to turn on a device is

    sudo ./etekcity_controller.py 18 21 2 on

which will turn on the device with an address of 21 and a unit number of 2.

You can control the devices with commands called from other programs or 
scripts.  If you want more flexibility you can run a REST server which allows
the devices to be controlled by a wide range of programs and commands. 

#### (optional) Configure REST server which allows control via browser or REST. (5 minutes)

If you want to use the REST server to control the devices you can have 
that server configured to start automatically each time the system is 
started.

To do this a configuration file is copied to the `/lib/systemd/system`
directory then the service is enabled to start automatically.  You can 
also start the service immediately without rebooting the system.

To set up the facility use

    sudo cp etekcity_rest_server.service /lib/systemd/system
    sudo systemctl enable etekcity_rest_server.service

You can start the service without rebooting by typing 

    sudo systemctl start etekcity_rest_server.service

Finally, you can check the status of the service with 

    sudo systemctl status -l etekcity_rest_server.service
    
This last command should provide out similar to 

    o etekcity_rest_server.service - Run REST server for Etekcity outlet controller
       Loaded: loaded (/lib/systemd/system/etekcity_rest_server.service; enabled)
       Active: active (running) since Thu 2017-12-07 22:41:08 EST; 8s ago
     Main PID: 2438 (python3)
       CGroup: /system.slice/etekcity_rest_server.service
               \- 2438 python3 /opt/Controllers/EtekcityOutlet/etekcity_rest_server.py
    
    Dec 07 22:41:08 rpi-214 systemd[1|: Started Run REST server for Etekcity outlet controller.

You can now control one of the devices with this command

    curl -H 'Content-Type: application/json' -X POST -d '{"address":21,  "unit":2, "action": "on"}'  http://localhost:11111/

The above command turns on the device with unit number of 2 at address 21.  
Use the address you determined above and select a unit number between 
1 and 5 for the device you want to control.  Change "on" to "off" to turn the
device off.

Notice the above command does not need the `sudo` command.  You do not need
root access to send the REST commands to the server.  This allows many
programs to share the devices.

By default the REST server only responds to requests which are sent from 
the same host but you can change the way the server is started by altering the 
`StartExec` line in the `.service` file so any host on your network
can send a REST command.  To do this add `--network_address 0.0.0.0`
to the end of the command and restart.

#### Enjoy! 







