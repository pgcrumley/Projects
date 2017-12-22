/*
  MIT License

  Copyright (c)2017 Paul G Crumley

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

#include <Adafruit_NeoPixel.h>

// enable / disable debug information on serial port
#define DEBUG 4
#define SERIAL_BAUD_RATE 115200

//
// THIS CHANGES TO ACCOMODATE DOOR WIDTH
//
// about 2.6 meters round trip -> 1.3 meters one way
#define DISTANCE_THRESHOLD 7500

// these lines tell what Arduino pins the various devices connect to
#define RING_PIN 7    // plug the 24 LED ring in to Arduino GPIO pin 7
#define TRIGGER_PIN 8 // HC-SR04 Trigger pin
#define ECHO_PIN 9    // HC-SR04 Echo pin

// Have not found a device that hangs longer than 200 mSec
#define MAX_TIME 200000

// devices from NeoPixel library to make it easier to control these LED devices
Adafruit_NeoPixel ring = Adafruit_NeoPixel(24, RING_PIN, NEO_GRB + NEO_KHZ800);

//
// this function is done once, when power is applied to the device
//
void setup() {
  if (DEBUG) {
    Serial.begin(SERIAL_BAUD_RATE);
    Serial.println("entered Annunciator setup()");
  }

  pinMode(TRIGGER_PIN, OUTPUT);
  digitalWrite(TRIGGER_PIN, LOW);
  pinMode(ECHO_PIN, INPUT);

  ring.begin();
  ring.show(); // Initialize all pixels to 'off'

  if (DEBUG) {
    Serial.println("done with setup");
  }
}

//
// this function executes over and over and ....
//
void loop() {
  if (DEBUG > 5) {
    Serial.println("entered loop");
  }
  if (DEBUG > 10) {
    // special case to see patterns
    showPatterns();
  } else {
    // normal code
    int32_t echo_time = measureEchoDelay();
    // if echo time is < time to traverse door width do something
    if (echo_time < DISTANCE_THRESHOLD) {
      doSomething();
    }
  }
} // void loop() {

/*
   Make a echo and return the time in uSec for the return or device timeout.
*/
int32_t measureEchoDelay() {
  if (digitalRead(ECHO_PIN)) {
    Serial.println("ECHO pin is HIGH");
    while (digitalRead(ECHO_PIN))
      ;
    Serial.println("ECHO pin now LOW");
  }

  // give some setup time
  digitalWrite(TRIGGER_PIN, LOW);
  delay(1);

  // start process
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  uint32_t pulse_width = 0;

  while (LOW == digitalRead(ECHO_PIN))
    ;

  uint32_t start_time = micros();

  // wait to go LOW
  while (HIGH == digitalRead(ECHO_PIN)) {
    pulse_width = micros() - start_time; // should wrap properly
    if (MAX_TIME < pulse_width) {
      if (DEBUG) {
        Serial.println("measureEchoDelay: ECHO stuck HIGH");
      }
    }
  }

  return pulse_width;
} // int32_t measureEchoDelay()

/*
    colors of the rainbow to cycle through
*/
uint32_t rainboxColors[] = {
  ring.Color(  0,   0,   0), //  0 black
  ring.Color( 60,   0,   0),
  ring.Color(120,   0,   0),
  ring.Color(180,   0,   0),
  ring.Color(240,   0,   0), //  4 red
  ring.Color(240,  60,   0),
  ring.Color(240, 120,   0),
  ring.Color(240, 180,   0),
  ring.Color(240, 240,   0), //  8 yellow
  ring.Color(180, 240,   0),
  ring.Color(120, 240,   0),
  ring.Color( 60, 240,   0),
  ring.Color(  0, 240,   0), // 12 green
  ring.Color(  0, 240,  60),
  ring.Color(  0, 240, 120),
  ring.Color(  0, 240, 180),
  ring.Color(  0, 240, 240), // 16 cyan
  ring.Color(  0,  60, 240),
  ring.Color(  0, 120, 240),
  ring.Color(  0, 180, 240),
  ring.Color(  0,   0, 240), // 20 blue
  ring.Color(  0,   0, 180),
  ring.Color(  0,   0, 120),
  ring.Color(  0,   0,  60)
};

/*
    bright colors of the rainbow for single use
*/
uint32_t brightColors[] = {
  ring.Color(120,   0,   0),
  ring.Color(180,   0,   0),
  ring.Color(240,   0,   0), // red
  ring.Color(240,  60,   0),
  ring.Color(240, 120,   0),
  ring.Color(240, 180,   0),
  ring.Color(240, 240,   0), // yellow
  ring.Color(180, 240,   0),
  ring.Color(120, 240,   0),
  ring.Color( 60, 240,   0),
  ring.Color(  0, 240,   0), // green
  ring.Color(  0, 240,  60),
  ring.Color(  0, 240, 120),
  ring.Color(  0, 240, 180),
  ring.Color(  0, 240, 240), // cyan
  ring.Color(  0,  60, 240),
  ring.Color(  0, 120, 240),
  ring.Color(  0, 180, 240),
  ring.Color(  0,   0, 240), // blue
  ring.Color(  0,   0, 180),
};

/*
   turn off ring -- used after many patterns to quiet LEDs
*/
void ringOff() {
  for (int pos = 0; pos < 24; pos++) {
    ring.setPixelColor(pos, 0);
  }
  ring.show();
} // void ringOff() {

#define NUM_PATTERNS 9

/*
   Used for debugging
*/
void showPatterns() {
  Serial.println("showing all patterns");
  for (int i = 0; i < NUM_PATTERNS; i++) {
    Serial.println(i);
    doPattern(i);
    delay(2000);
  }
} // void showPatterns() {

/*
   pick a random action to do
*/
void doSomething() {
  int32_t r = random(NUM_PATTERNS);
  if (DEBUG > 3) {
    Serial.print("doSomething r = ");
    Serial.println(r);
  }
  doPattern(r);
} // void doSomething()

/*
  Given a pattern number, do that pattern then turn off LEDs
*/
void doPattern(int p) {
  uint32_t c = random(20);
  switch (p) {
    case 0:
      spinCW();
      break;
    case 1:
      spinCCW();
      break;
    case 2:
      spinUpCW();
      break;
    case 3:
      spinUpCCW();
      break;
    case 4:
      spinDownCW();
      break;
    case 5:
      spinDownCCW();
      break;
    case 6:
      rainboxColorSequence(10);
      break;
    case 7:
      Serial.println(c, HEX);
      theaterChase(brightColors[c], 70);
      theaterChase(brightColors[c], 70);
      theaterChase(brightColors[c], 70);
      theaterChase(brightColors[c], 70);
      theaterChase(brightColors[c], 70);
      break;
    case 8:
    default:
      for (int i = 0; i < 3; i++) {
        packPulse(10);
      }
      break;
  }
  ringOff();
} // void doPattern(int p)

/*
   BELOW ARE VARIOUS THINGS TO DO WHEN ACTIVATED.
*/

void spinCW() {
  rainbow_cw(11);
  rainbow_cw(9);
  rainbow_cw(5);
  rainbow_cw(3);
  rainbow_cw(1);
  rainbow_cw(3);
  rainbow_cw(5);
  rainbow_cw(9);
  rainbow_cw(11);
} // void spinCW()

void spinCCW() {
  rainbow_ccw(11);
  rainbow_ccw(9);
  rainbow_ccw(5);
  rainbow_ccw(3);
  rainbow_ccw(1);
  rainbow_ccw(3);
  rainbow_ccw(5);
  rainbow_ccw(9);
  rainbow_ccw(11);
} // void spinCCW()

void spinUpCW() {
  rainbow_cw(11);
  rainbow_cw(9);
  rainbow_cw(5);
  rainbow_cw(3);
  rainbow_cw(1);
} // void spinUpCW()

void spinUpCCW() {
  rainbow_ccw(11);
  rainbow_ccw(9);
  rainbow_ccw(5);
  rainbow_ccw(3);
  rainbow_ccw(1);
} // void spinUpCCW()

void spinDownCW() {
  rainbow_cw(1);
  rainbow_cw(3);
  rainbow_cw(5);
  rainbow_cw(9);
  rainbow_cw(12);
} // void spinDownCW()

void spinDownCCW() {
  rainbow_ccw(1);
  rainbow_ccw(3);
  rainbow_ccw(5);
  rainbow_ccw(9);
  rainbow_ccw(12);
} // void spinDownCCW()

void rainbow_ccw(uint32_t d) {
  /*
     Spin rainbow colors one full spin CCW
  */
  for (int offset = 0; offset < 24; offset++) {
    for (int pos = 0; pos < 24; pos++) {
      ring.setPixelColor(pos, rainboxColors[(pos + offset) % 24]);
    }
    ring.show();
    delay(d);
  }
} // void rainbow_ccw(uint32_t d)


void rainbow_cw(uint32_t d) {
  /*
     Spin rainbow colors one full spin CCW
  */
  for (int offset = 23; offset >= 0; offset--) {
    for (int pos = 0; pos < 24; pos++) {
      ring.setPixelColor(pos, rainboxColors[(pos + offset) % 24]);
    }
    ring.show();
    delay(d);
  }
} // void rainbow_cw(uint32_t d)

/*
   From GhostBuster pack
*/
void packPulse(uint16_t wait) {
  uint8_t INTENSITY_CHUNK = 8;
  uint8_t TOP_INTENSITY = 200;  // this must be < 255 - INTENSITY_CHUNK

  for (uint8_t intensity = 0;
       intensity <= TOP_INTENSITY;
       intensity += INTENSITY_CHUNK) {
    // start with some blue, end all red
    uint8_t red_intensity = intensity;
    uint8_t blue_intensity = (TOP_INTENSITY / 8) - (intensity / 2);
    if (blue_intensity >= TOP_INTENSITY / 2) blue_intensity = 0;
    for (uint16_t i = 0; i < ring.numPixels(); i++) {
      ring.setPixelColor(i, red_intensity, 0, blue_intensity);
    }
    ring.show();
    delay(wait);
  } // for intensity

} // void packPulse(uint16_t wait)

/*
  Theater-style crawling lights with a spacing of 3
*/
void theaterChase(uint32_t color, uint32_t wait) {
  for (int q = 0; q < 3; q++) {
    for (int i = 0; i < ring.numPixels(); i = i + 3) {
      ring.setPixelColor(q + i, color);  //turn every third pixel on
    }
    ring.show();
    delay(wait);
    for (int i = 0; i < ring.numPixels(); i = i + 3) {
      ring.setPixelColor(q + i, 0);      //turn every third pixel off
    }
  }
} // void theaterChase(uint32_t color, uint32_t wait)

void chase(byte r, byte g, byte b, uint32_t d) {
  for (int q = 0; q < 3; q++) {
    for (int i = 0; i < ring.numPixels(); i = i + 3) {
      ring.setPixelColor(q + i, ring.Color(r, g, b)); //turn every 3rd pixel on
    }
    ring.show();
    delay(d);
    for (int i = 0; i < ring.numPixels(); i = i + 3) {
      ring.setPixelColor(q + i, 0);      //turn every third pixel off
    }
  }
} // void chase(byte r, byte g, byte b, uint32_t d)

void setRing(byte r, byte g, byte b, uint32_t d) {

  for (int i = 0; i < ring.numPixels(); i++ ) {
    ring.setPixelColor(i, ring.Color(r, g, b));
    ring.show();
    delay(d);
  }
} // void setRing(byte r, byte g, byte b, uint32_t d)


/*
   This will generate RGB values to sweep through the colors of the rainbow.
   Output starts and ends with black and the numbers are generated in a
   sequence of 6 phases, each of which sweeps a single color up or down.
   The sequences are:
   1:  sweep red from 0 to 255
      now RED
   2:  sweep green from 0 to 255
      now YELLOW
   3:  sweep red from 255 to 0
      now GREEN
   4:  sweep blue from 0 to 255
      now CYAN
   5:  sweep green from 255 to 0
      now BLUE
   6:  sweep blue from 255 to 0

   parameter d is time in uSec from phase to phase
*/
void rainboxColorSequence(uint32_t d) {
  int8_t inc = 48;
  uint16_t top = 250 / inc;

  byte r = 0;
  byte g = 0;
  byte b = 0;

  /* phase 1:  black -> red */
  for (int i = 0; i < top; i++) {
    r += inc;
    chase(r, g, b, d);
  }

  /* phase 2:  red -> yellow */
  for (int i = 0; i < top; i++) {
    g += inc;
    chase(r, g, b, d);
  }

  /* phase 3:  yellow -> green */
  for (int i = 0; i < top; i++) {
    r -= inc;
    chase(r, g, b, d);
  }

  /* phase 4:  green -> cyan */
  for (int i = 0; i < top; i++) {
    b += inc;
    chase(r, g, b, d);
  }

  /* phase 5:  cyan -> blue */
  for (int i = 0; i < top; i++) {
    g -= inc;
    chase(r, g, b, d);
  }

  /* phase 6:  blue -> black */
  for (int i = 0; i < top; i++) {
    b -= inc;
    chase(r, g, b, d);
  }
} // void rainboxColorSequence(uint32_t d)

/* end of Annunciator */

