#!/bin/bash
# MIT License
#
# Copyright (c) 2021 Paul G Crumley
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @author: pgcrumley@gmail.com
#
#
# This script will take a picture, send it to the e-mail address found in
# /opt/Projects/UsbCameraServer/SendToAddress.txt, and if 
# /boot/shutdown_after_send exists it will shutdown the system.

LOG_FILE=/opt/Projects/logs/BootSnapSendShutdown.log
TO_ADDRESS_FILE=/opt/Projects/UsbCameraServer/SendToAddress.txt
SHUTDOWN_FILE=/boot/shutdown_after_send
MAIL_FILE=/tmp/$$.mail
IMAGE_FILE=/tmp/$$.png

# take a picture and send it if possible
if [ -f $TO_ADDRESS_FILE ]; then
    /opt/Projects/UsbCameraServer/TestCamera.py -o $IMAGE_FILE
    # USE THIS RATHER THAN ABOVE COMMAND IF RUNNING A UsbCameraServer LOCALLY
    # wget -O $IMAGE_FILE http://127.0.0.1:4000/capture-devices/0
    date > $MAIL_FILE
    if [ -f $SHUTDOWN_FILE ]; then
        ls -l $SHUTDOWN_FILE >> $MAIL_FILE
    else
        echo $SHUTDOWN_FILE not present >> $MAIL_FILE
    fi
    mailx -s "captured image" -A $IMAGE_FILE $( cat $TO_ADDRESS_FILE ) < $MAIL_FILE
    echo "mailx ended with status of $?" >> $LOG_FILE
else
   echo "File $TO_ADDRESS_FILE does not exist." >> $LOG_FILE
fi

# shutdown?
if [ -f $SHUTDOWN_FILE ]; then
    sync
    shutdown now
    echo "shuting down system" >> $LOG_FILE
fi

#clean up
rm $MAIL_FILE $IMAGE_FILE
