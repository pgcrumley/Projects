# USB Camera Server

This software provides a very simple web server which will sample the
first USB attached camera and return a PNG stream.

### Attach the USB camera to the system (1 minute)

If you are using a USB camera just plug it in.  Some machines such as laptops
have built-in cameras which behave as an attached USB camera.

The default configuration assumes there are no built-in cameras and the first 
(only) USB camera is used.  This video device is numbered 0.

The optional parameter of 

	-v video_device #
	
can be used to capture a video device other than 0.  Look in /dev for video devices.

Edit the UsbCameraServer.service file to change the video_device to use.

### Configure the software (15 minutes -- longer if system is not up-to-date)

Become root for the next few operations:

    sudo su -
    
This will pull in many projects.  You can trim later if you like:

    cd /opt
    git clone https://github.com/pgcrumley/Projects.git
    cd Projects/UsbCameraServer
    
Install python3 using a command of:

    apt-get update
    apt-get -y install python3 python3-dev git
    
Install required python3 package(s) using a command of:

    pip3 install -r requirements.txt

Make sure `python3` works and CV2 is installed by typing:

    python3
    import cv2
    exit()

Your console should look like this:

    # python3
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import cv2
    >>> exit()
    #
    
The version numbers may vary but there should not be any messages after the
`import cv2` line.    

Exit root access

    exit

### Enable the service to start after reboot (optional)

Copy the service file to the systemd location:

    sudo su -
    cd /opt/Projects/USbCameraService
    ./InstallUsbCameraServer.sh
    
If the status is good look at the log file to make sure it was started and 
has access to write the log

Leave root access mode with 

    exit
    
### Test

Point your web browser to the port for the Raspbery Pi.  My Raspberry Pi
is at address 192.l68.1.227 so:

    http://192.168.1.227:6000/

After a couple seconds an image should be found in our browser.

Command line access with programs such as `wget` will also work.  For example:

    wget -qO- http://192.168.1.227:6000/ > image.png
    
### Enjoy! 

Congratulations!  You can now easily capture an image from the first attached
USB camera to be retrieved by other pieces of software or from your browser.  

Enjoy!
