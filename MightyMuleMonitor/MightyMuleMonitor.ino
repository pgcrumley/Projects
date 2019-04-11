/*
MIT License

Copyright (c) 2018, 2019 Paul G Crumley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: pgcrumley@gmail.com
 */

/*
This program monitors two signals from a modified Mighty Mule Driveway Alarm
and is able to send a pulse to the alarm to activate the RESET button on the
control box.

The two monitored signals are BATTERY LOW and VISITOR which are the signals
used to activate the corresponding LEDs.  Each time the VISITOR LED goes
active the code increments the visitor_counter then delays 5 seconds for
the Mighty Mule controller to finish the LED flashes and alarm tone.

After the 5 second delay a RESET pulse is sent to the controller so later
activations can be detected and added to the visitor_count.
To use a pin as an INPUT set the output HIGH.  There will be a weak pullup
on the pin so make sure input signals have a relatively low impedance.

The Low Battery LED is monitored at all times and if the LED is found on
that is remembered and reported (then cleared) on teh next "?" command.

The program also monitors the serial port for commands of:
  ` returns the version and name of the code as a string with a terminating \n
  ? returns a json dictionary with two fields of:  (an example)
        {"visitor_count":0, "low_battery":false}
    with a terminating \n where visitor_count is a decimal
    number of the visitors since the previous "?" command and
    battery_low is
    "true" if the BATTERY LOW LED is active.
    If not "true", battery_low is "false".

Everything else received is ignored.

Version
0       initial version

 */

#define DEBUG 0
#define SERIAL_BAUD_RATE 115200

#define BATTERY_LOW_PIN 2
#define VISITOR_PIN 3
#define RESET_PIN 4
#define FIRST_UNUSED_PIN 5
#define LAST_UNUSED_PIN 13

const char VERSION[] = "V0_MightyMuleMonitor";


/*
 Arduino setup function -- runs once at restart.
 */
void setup(void) {
	pinMode(VISITOR_PIN, INPUT_PULLUP);
	pinMode(BATTERY_LOW_PIN, INPUT_PULLUP);
	pinMode(RESET_PIN, OUTPUT);
	digitalWrite(RESET_PIN, HIGH);
	/* set unused pins to have pullup to reduce power */
	for (int i = FIRST_UNUSED_PIN; i <= LAST_UNUSED_PIN; i++) {
		pinMode(i, INPUT_PULLUP);
	}

	Serial.begin(SERIAL_BAUD_RATE);
	while (!Serial) {
		; // wait for serial port to connect. Needed for native USB port only
	}
}

/* used for state machine */
#define LED_OFF_STATE 0
#define LED_ON_STATE 1

unsigned long timer_end = 0L;
unsigned long visitor_count = 0L;
boolean low_battery = false;
int state = LED_OFF_STATE;

/*
 Run the state machine for counting visitors.
 */
void runStateMachine() {

  /* always check for low battery */
  low_battery |= (LOW == digitalRead(BATTERY_LOW_PIN));

	switch (state) {
	case LED_OFF_STATE:
		/* RESET pin must be high to allow alarm to occur */
		digitalWrite(RESET_PIN, HIGH);
		/* if VISITOR LED is active bump count */
		if (LOW == digitalRead(VISITOR_PIN)) {
			timer_end = millis() + 3500;  /* time needed to capture alarm */
			visitor_count++;
			state = LED_ON_STATE;
		}
		break;
	case LED_ON_STATE:
		if (millis() >= timer_end) {
			digitalWrite(RESET_PIN, LOW);
			delay(100L);
			digitalWrite(RESET_PIN, HIGH);
			state = LED_OFF_STATE;
		}
		break;
	default:
		/* something has gone wrong.  LED_OFF_STATE is most likely place to be. */
		timer_end = 0L;
    low_battery = false;
		state = LED_OFF_STATE;
	}
}

/*
 Arduion loop -- runs continually after setup().
 */
void loop(void) {
	/* run the state machine */
	runStateMachine();
	/* check for a command on the serial port and service if present */
	char c = Serial.read();
	if (-1 != c) {
		if (DEBUG) {
			Serial.print("Command: 0x");
			Serial.println(c, HEX);
		}

		if ('?' == c) {
      Serial.print("{\"visitor_count\":");
			Serial.print(visitor_count);
			Serial.print(", ");
			if (low_battery) {
				Serial.print("\"low_battery\":true");
			} else {
				Serial.print("\"low_battery\":false");
			}
      Serial.println('}');
      /* set to 0 before state machine can run */
      visitor_count = 0L;
      low_battery = false;
			return;
		}

		if ('`' == c) {
			Serial.println(VERSION);
			return;
		}

		if (DEBUG) {
			Serial.println("got unknown command");
		}
	}
} // loop()
