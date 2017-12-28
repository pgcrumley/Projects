# Annunciator

Tired of having people surprise you in your office or cubicle?  

This simple project uses a [HC-SR04](http://www.micropik.com/PDF/HCSR04.pdf)
and an Arduino to watch for visitors and will generate a
variety of patterns on a 24 LED Neopixel ring when something enters the 
range of the sensor.

I used an Arduino Nano with the ATmega 328 chip but a
normal Arduino will work too.  Since the Arduino can be powered by USB
one can simply plug in to one of the many USB ports available in one's 
office or cubicle.  The parts cost me less than $25 and the
24 LED ring is the most expense part so using a smaller or more basic LED 
could cut the price in half.

The program continually sends out pings from the HC-SR04 sensor
and "listens" for an echo response.  

A time threshold is set to a typical office cubicle door width 
-- about 1.2 meters.
Echos that come back longer than this distance are considered to be "long"
echos which result from the other side of the doorway, furniture, or simply
echos that never come back.

Short echos are probably an indication a visitor has entered the sensor 
area in the 1.2 meter range.

In order to avoid "false alarms" the code waits for 3 short echos in a row
before putting a pattern on the LEDs.

Once a visitor is detected the device waits 10 seconds before looking for echos
again.  You might want to make this longer or shorter to suit your 
preferences.

I power the Arduino with the USB connection so the USB to the Arduino is 
readily accessible allowing one to 
easily reprogram the device to add new modes for special uses.

You might need to adjust the echo threshold to account for wider or more
narrow doorways.
