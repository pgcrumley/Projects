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

#pip3 install -r requirements.txt

if [ "$EUID" -ne 0 ]
  then echo "Must run as root"
  exit
fi

LOG_FILE=/opt/Projects/logs/BootSnapSendShutdown.log
TO_ADDRESS_FILE=/opt/Projects/UsbCameraServer/SendToAddress.txt

apt update
apt install -y python3-opencv msmtp-mta mailutils

# make sure files are in proper states
mkdir -p /opt/Projects/logs
chmod +x /opt/Projects/UsbCameraServer/BootSnapSendShutdownService.sh
chmod +x /opt/Projects/UsbCameraServer/TestCamera.py
chmod 400 /opt/Projects/UsbCameraServer/BootSnapSendShutdownService.service

if [ -f $TO_ADDRESS_FILE ]; then
    echo found $TO_ADDRESS_FILE
else
    echo "Installing skeleton $TO_ADDRESS_FILE file..."
    cat <<- EOF > $TO_ADDRESS_FILE
your_target_id@site.com        
    EOF
    chmod 600 $TO_ADDRESS_FILE
    echo "Make sure to customize the $TO_ADDRESS_FILE file"
    echo " "    
fi
    
if [ -f /root/.msmtprc ]; then
    echo Not overwritting the existing /root/.msmtprc file.  Check configuration
else
    echo "Installing skeleton /root/.msmtprc file..."
    cat <<- EOF > /root/.msmtprc
account default
host smtp.gmail.com
port 587
tls on
tls_starttls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
tls_certcheck on
auth on
user YOUR_ID@SITE.COM
password "YOUR_PASSWORD"
logfile /root/.msmtp.log

EOF
    chmod 600 /root/.msmtprc
    echo " "
    echo "make sure to customize the /root/.msmtprc file"
    echo " "
fi

cp /opt/Projects/UsbCameraServer/BootSnapSendShutdownService.service /lib/systemd/system
systemctl enable BootSnapSendShutdownService
