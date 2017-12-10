/*
MIT License

Copyright (c) 2017 Paul G Crumley

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
 * Control two LEDs that flash in a few patterns.
 *
 * A button is monitored to move between modes of:
 *   Flash	  with period of 1 second
 *   On		  steady on
 *   Random	  flashes separated by 1/20th to 2 seconds
 *   Off	  steady off
 *
 * The two LED flashes are slightly staggered in their turn on times
 * as it seems to provide a more interesting effect.
 */

#include "Arduino.h"

// enable / disable debug information on serial port and to on-board LED
#define DEBUG 1
#define SERIAL_BAUD_RATE 9600

// pins used by project
#define BUTTON_PIN (2)  // this pin is able to activate interrupts
#define LED_1_PIN (11)
#define LED_2_PIN (12)
#define DEBUG_LED_PIN (LED_BUILTIN)

// Macros to make save typing and errors
#define TURN_LED_1_ON (digitalWrite(LED_1_PIN, LOW))
#define TURN_LED_1_OFF (digitalWrite(LED_1_PIN, HIGH))
#define TURN_LED_2_ON (digitalWrite(LED_2_PIN, LOW))
#define TURN_LED_2_OFF (digitalWrite(LED_2_PIN, HIGH))
#define TURN_DEBUG_LED_ON (digitalWrite(DEBUG_LED_PIN, HIGH))
#define TURN_DEBUG_LED_OFF (digitalWrite(DEBUG_LED_PIN, LOW))

// Keep track of button state to move from mode to mode
#define BUTTON_IS_UP (digitalRead(BUTTON_PIN))
#define BUTTON_IS_DOWN (!digitalRead(BUTTON_PIN))
volatile int ButtonPressDetected = 0;   // set by the ISR when the button
                                        //   is pressed
                                        // reset by the ISR when the button is
                                        //   seen released after it was pressed
volatile int ButtonReleaseDetected = 0; // set by the ISR when the button
                                        //   was released
                                        // reset in the "loop()" flow after
                                        //   the resulting action is done

// Keep track of the flash mode -- add more modes here ;-)
#define MODE_FLASH 0
#define MODE_ON 1
#define MODE_RANDOM 2
#define MODE_OFF 10
volatile int runMode = MODE_FLASH; // start flashing

// the setup function runs once when you press reset or power the board
void setup() {
    // initialize digital pin LED_BUILTIN as an output.
    pinMode(DEBUG_LED_PIN, OUTPUT);     // HIGH to turn on
    pinMode(LED_1_PIN, OUTPUT);         // LOW to turn on
    pinMode(LED_2_PIN, OUTPUT);         // LOW to turn on
    pinMode(BUTTON_PIN, INPUT_PULLUP);  // connect button between pin and ground

    // set initial state of LEDs
    digitalWrite(LED_BUILTIN, LOW);  // no need to turn this on
    TURN_LED_1_ON;
    TURN_LED_2_ON;
    TURN_DEBUG_LED_OFF;

    if (DEBUG) {
        Serial.begin(SERIAL_BAUD_RATE);
    }

    // connect the interrupt handler routine to button pin
    attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonHandler, CHANGE);

    // let system settle down before proceeding
    delay(1000);

    // initialize button state
    ButtonPressDetected = 0;
    ButtonReleaseDetected = 0;

    if (DEBUG) {
        Serial.println("started flasher");
    }
}

/*
 * ACK the button action was done so we can recognize a new button press.
 *
 * This must be called by the code that runs in the various modes after a
 * button press has been recognized and acted upon so more presses can be
 * recognized by the button interrupt handler.
 */
void ack_button_action_done() {
    ButtonReleaseDetected = 0; /* move from button state 3 to state 1 */
    if (DEBUG) {
        TURN_DEBUG_LED_OFF;
    }
}

/*
 * Normal thing to do, flash the LEDs once each second.
 */
void run_flash() {
    TURN_LED_1_ON;
    delay(25);
    TURN_LED_2_ON;
    delay(50);
    TURN_LED_1_OFF;
    delay(25);
    TURN_LED_2_OFF;
    delay(900);

    // Check that a button has been released (after being pressed ;-)
    // and if a button action as detected move to the next mode and
    // acknowledge the button action so more button presses can be detected.
    if (ButtonReleaseDetected) {
        runMode = MODE_ON;
        ack_button_action_done();
        if (DEBUG) {
            Serial.println("Change to MODE_ON");
        }
    }
}

/*
 * Solid ON
 */
void run_on() {
    TURN_LED_1_ON;
    TURN_LED_2_ON;
    delay(500);  // to debounce button

    // Check that a button has been released (after being pressed ;-)
    // and if a button action as detected move to the next mode and
    // acknowledge the button action so more button presses can be detected.
    if (ButtonReleaseDetected) {
        runMode = MODE_RANDOM;
        ack_button_action_done();
        if (DEBUG) {
            Serial.println("Change to MODE_RANDOM");
        }
    }
}

/*
 * Flash the LEDs with random times between flashes
 */
void run_random() {
    TURN_LED_1_ON;
    delay(25);
    TURN_LED_2_ON;
    delay(50);
    TURN_LED_1_OFF;
    delay(25);
    TURN_LED_2_OFF;
    delay(random(50, 2000));

    // Check that a button has been released (after being pressed ;-)
    // and if a button action as detected move to the next mode and
    // acknowledge the button action so more button presses can be detected.
    if (ButtonReleaseDetected) {
        runMode = MODE_OFF;
        ack_button_action_done();
        if (DEBUG) {
            Serial.println("Change to MODE_OFF");
        }
    }
}

/*
 * No blinky.
 */
void run_off() {
    TURN_LED_1_OFF;
    TURN_LED_2_OFF;
    delay(500);  // to debounce button

    // Check that a button has been released (after being pressed ;-)
    // and if a button action as detected move to the next mode and
    // acknowledge the button action so more button presses can be detected.
    if (ButtonReleaseDetected) {
        runMode = MODE_FLASH;
        ack_button_action_done();
        if (DEBUG) {
            Serial.println("Change to MODE_FLASH");
        }
    }
}

/*
 * The loop function runs over and over again... forever...
 */
void loop() {
    switch (runMode) {
    case MODE_FLASH:
        run_flash();
        break;
    case MODE_ON:
        run_on();
        break;
    case MODE_OFF:
        run_off();
        break;
    case MODE_RANDOM:
        run_random();
        break;
    default:
        // if we loose track of the mode set us to a quiet mode
        if (DEBUG) {
            Serial.println("Unknown mode detected.");
        }
        runMode = MODE_OFF;
    }
}

/*
 * Button code has three states:
 *   1.) Button not pressed and no action waiting to happen
 *       -- boots to this state
 *   2.) Button no action is pending and button has been seen as pressed
 *       -- button held down
 *   3.) Button was seen as pressed but it is no longer pressed
 *       -- action to be taken
 */

/*
 * Debounce button and set ButtonReleaseDetected so other code
 * knows what happened.
 *
 * Other code resets ButtonReleaseDetected.
 */
void buttonHandler() {
    if (!ButtonReleaseDetected) {
        /* in state 1 */
        if (BUTTON_IS_DOWN) {
            /* move from state 1 to state 2 */
            ButtonPressDetected = 1;
        } else {
            /* move from state 2 to state 3 */
            ButtonReleaseDetected = 1;
            ButtonPressDetected = 0;
            if (DEBUG) {
                TURN_DEBUG_LED_ON;
            }
        }
    } else {
        /* in state 3 so ignore button till action is taken */
    }
}
