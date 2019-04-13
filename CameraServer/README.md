# Camera Server

This software provides a very simple web server which will sample a 
Raspberry Pi camera and return a JPEG stream.


### Configure the software (15 minutes -- longer if system is not up-to-date)

Become root for the next few operations:

    sudo su -
    
This will pull in many projects.  You can trim later if you like:

    cd /opt
    git clone https://github.com/pgcrumley/Projects.git
    cd Projects/CameraServer
    
Install python3 using a command of:

    apt-get update
    apt-get -y install python3 python3-dev git
    
Install a python serial library using a command of:

    pip3 install -r requirements.txt

Make sure `python3` works and RPi.GPIO is installed by typing:

    python3
    import picamera
    exit()

Your console should look like this:

    # python3
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import picamera
    >>> exit()
    #
    
The version numbers may vary but there should not be any messages after the
`import picamera` line.    

Exit root access

    exit

### Attach the Raspberry Pi camera to the system

There are many tutorials on how to attach the Raspberry Pi camera to your 
system.  Here is one I refer to:  
[installation tutorial](https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera)

### Enable the service to start after reboot (optional)

Copy the service file to the systemd location:

    sudo su -
    cd /opt/Projects/CameraService
    cp CameraService.service /lib/systemd/system
    
Enable the service to start after reboots:

    systemctl enable CameraService

You can start the monitor now and check its status:

    systemctl start CameraService
    systemctl status CameraService
    
If the status is good look at the log file to make sure it was started and 
has access to write the log

Leave root access mode with 

    exit
    
### Test

Point your web browser to the port for the Raspbery Pi.  My Raspberry Pi
is at address 192.l68.1.227 so:

    http://192.168.1.227:5000/

After a couple seconds an image should be found in our browser.

Command line access with programs such as `wget` will also work.  For example:

    wget -qO- http://192.168.1.227:5000/ > image.jpeg
    
### Enjoy! 

Congratulations!  You can now easily capture an image from the camera from 
other pieces of software or from your browser.  

Enjoy!