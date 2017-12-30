# Etekcity Electric Outlet Controller

This software, when used with a
[433 MHz transmitter](https://www.amazon.com/gp/product/B017AYH5G0),
allows a Raspberry Pi to wirelessly control the
[Etekcity Outlet Switch](https://www.amazon.com/gp/product/B00DQELHBS/) 
devices.

In addition to the transmitter and device one also requires some 
[jumper wires](https://www.amazon.com/gp/product/B01LZF1ZSZ/)
to connect the parts.

If you purchase the parts using the above links you will have 5 sets of
transmitter / receiver boards (you only need one for the transmitter
boards) and you will have lots or jumper wires (you only need 3 to 
connect the transmitter to the Raspberry Pi and you may want to use an 
additional wire as an antenna.

The outlet switches are identified by two numbers.  First is a device
address which ranges from 0 to 255.  All outlet switches in a single 
package have the same address.

While the devices in a package share an address, each device has a unique unit 
number from 1 through 5.  With these two numbers software can use the
transmitter to send signals to turn the outlet switches on and off.

This arrangement allows a Raspberry Pi to control powered devices without
direct connections to hazardous voltages.

Once the parts are available one should be able to
a Raspberry Pi to a transmitter and configure
the software to control the outlets in under an hour.  The steps include:

* Install the software in the Raspberry Pi
* Configure the software 
* Plug in the outlet switches and make sure they work with the provided control.
* Attach the transmitter to the Raspberry Pi.
* Test the transmitter operation.
* Determine the address for the outlet switches.
* Use the controller command to turn devices on and off.
* (optional) Configure REST server which allows control via browser or REST.
* Enjoy!


### Install the software in the Raspberry Pi (5 minutes)

The software and scripts assume the software is installed in `/opt`, a
standard directory for "optional" software.  To install the software use

    sudo sh -c 'cd /opt ; git clone https://github.com/pgcrumley/Controllers.git'

This will place a copy of the software in `/opt` and leave behind
information that makes it easy to retrieve updates later if needed.

Next 

    cd /opt/Controllers/Etekcity/
    
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

### Plug in the outlet switches and make sure they work with the provided control. (5 minutes)

Unpack the outlet switches and install the battery in the included remote.
Plug one or more of the outlet switches in to a wall outlet and make sure 
the devices switch on and off when you use the remote control.

When the outlet switch is "on" a red light will illuminate as shown below:

![switch on image](./images/on.png)

When the outlet switch is "off" the red light is also off as shown below:

![switch off image](./images/off.png)

It would be a good idea to plug a lamp or other electric device in to the 
outlet switches to verify they operate correctly before proceeding.

When you are sure the outlets all work correctly it is time to let the 
Raspberry Pi control them.

Leave the outlet switches plugged in to a receptacle so you are ready to
determine the address and test them after the transmitter is attached to
the Raspberry Pi.

### Attach the transmitter to the Raspberry Pi. (10 minutes)

Three wires connect the transmitter to the Raspberry Pi.  The wires are

| Function | Color in picture | Raspberry Pi Pin Number | Pin Name |
| ---- | ---- | ----- | ----- | 
| 3.3 volt power | Orange | 17 | 3.3V PWR |
| Signal | Blue | 18 | GPIO 24 |
| Ground | Black | 20 | GND |

You can choose different colors for the wires but be sure the correct
pins are connected between the Raspberry Pi and the transmitter.

Power down your Rapsberry Pi before making the connections with the GUI or 
a command such as

    sudo shutdown --poweroff now

Wait a few second for the LED activity to stop then disconnect power from the
Raspberry Pi.

Connect the transmitter to the Raspbery Pi as shown:

![Connections](./images/connections_2.png)

Note that the pins on the connector start with 1 in the upper left position 
and pin 2 is in the upper right location.  The pins in the next row down are
3 and 4, then 5 and 6. This continues with the bottom left pin of 39 and the 
bottom right pin of 40.  Older boards only have only 28 pins.

An image of the pins with pin numbers and names is available
[here](https://github.com/DotNetToscana/IoTHelpers/wiki/Raspberry-Pi-2-and-3-Pinout).

Please note that many of the pins have names such as "GPIO 12" or "GPIO 17".
The number in the GPIO name tells how the pins are used by the hardware.
In this project we are using the 
pin numbers (not names) and the numbers simply refer to
the pins' location on the board, not what they do.  

For this project we connect the `DATA` pin on the transmitter (yes, the 
word `DATA` is written backwards on the transmitter board) to 
pin number 18.  Pin 18 has a name of `GPIO 24`.  

Check the connections twice to be sure before proceeding.

Please be careful to not let the transmitter board come in contact with 
the Raspberry Pi when the devices are powered.  There are voltages present
on both cards which can cause damage if the voltages come in contact with 
delicate parts.  It migth be a good idea to wrap the transmitter card with
some tape or other non-conductive material (e.g. light cardboard, plastic 
bag) to prevent damage.

### Test the transmitter operation. (5 minutes)

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

### Use the controller command to turn devices on and off. (2 minutes)

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

### (optional) Configure REST server which allows control via browser or REST. (5 minutes)

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

### Enjoy! 







