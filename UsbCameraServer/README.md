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

Run the __FindCaptureDevices.py__ command to determine what devices are found.

### Configure the software (15 minutes -- longer if system is not up-to-date)

Become root for the next few operations:

    sudo su -
    
Install git python3 modules using a command of:

    apt-get update
    apt-get -y install git python3 python3-dev python3-opencv 
    
This will pull in many projects.  You can trim later if you like:

    cd /opt
    git clone https://github.com/pgcrumley/Projects.git
    cd Projects/UsbCameraServer
    
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

    http://192.168.1.227:4000/

After a couple seconds an image should be found in our browser.

Command line access with programs such as `wget` will also work.  For example:

    wget -qO- http://192.168.1.227:4000/ > image.png
    
### Resources

The server responds to the following URLs:

* /                    returns PNG image for default device
* /capture-devices/N   returns PNG image if N is a valid device
* /capture-devices     returns JSON list of URLs for valid capture-device/N (note, no trailing /)
* /favicon.ico         returns image in ICO format

### Boot Snap Send Shutdown

The **BootSnapSendShutdown.sh** script and service will take a 
picture and send it
to an e-mail address when the system is booted.  
The script will also optionally
shutdown the system (if the file **/boot/shutdown\_after\_send** is present)

This allows the system to be connected to a motion detector socket and when
the detector powers on the socket the system will boot, then take a picture,
send it, then do an orderly shutdown to protect the file system so the system
is more likely to reboot properly the next time it is started.

The file that controls the shutdown is kept on the **/boot** file system to make
it easier to disable the shutdown for debug purposes as the **/boot** 
file system can often be mounted on other systems for changes.

When **InstallBootSnapSendShutdownService.sh** is run 
(as **root**) it will install
the needed packages and if the file is not already present, 
install a skeleton **.msmtprc** file in **/root**.

The **BootSnapSendShutdown.sh** script defaults to running the 
**TestCamera.py** program
to retrieve a photo but it can also fetch the image from a local web server.  
See the file to make the change. 

### Enjoy! 

Congratulations!  You can now easily capture an image from the first attached
USB camera to be retrieved by other pieces of software or from your browser.  
