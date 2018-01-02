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

Give TJBot a "set of wheels".

See https://github.com/pgcrumley/Projects/TJBot_Drives
to learn how to let TJBot drive.

Code inspired by IBM's TJBot stt.js program.

This requires entries for:
    exports.drive_server_address = 127.0.0.1; // by default use "localhost"
    exports.drive_server_port = 9999;  // by default use IP port 9999
in the config.js file.  You can alter these to meet your local needs.
*/

var DEBUG = 2;

// see https://github.com/ibmtjbot for more details on config and setup
var TJBot = require('tjbot');
var config = require('./config');
var credentials = config.credentials;
var hardware = ['led', 'servo', 'microphone'];
var tjConfig = {
    log: {
        level: 'info'  // change to 'verbose' for more details
    },
    listen: {  // annoying the microphoneDeviceId & language must be given
        microphoneDeviceId: 'plughw:1,0',
        language: 'en-US',
        inactivityTimeout: 60 // close connection after 60 seconds of silence
    },
    wave: {
        servoPin: 12 // corresponds to BCM 12 / physical PIN 32
    }
};
var tj = new TJBot(hardware, tjConfig, credentials);

console.log("You can tell me how to drive with commands of:");
console.log("  forward, backward, stop, halt,");
console.log("  right, left, clockwise, counter-clockwise");


/*
 * Sends a REST command to a local REST server to turn a switch on or off.
 */
function sendREST(action) {
    
    var http = require('http');
    var url = require('url');

    // The dictionary of data to sent to the REST server
    var postData = JSON.stringify({
        'drive' : action
    });
    if (DEBUG > 1) {
        console.log(postData.toString())
    }
    // Details about how to send the REST request
    var options = {
            'method' : 'POST',
            'protocol' : 'http:',
            'hostname' : config.drive_server_address,
            'port' : config.drive_server_port,
            'path' : '/json',
            'headers' : {
                'Content-Type' : 'application/json',
                'Content-Length' : Buffer.byteLength(postData)
            }
    }

    // Actually send the request
    var req = http.request(options, function (res) {
        var chunks = [];

        // res.setEncoding('utf8');

        res.on('data', function(chunk) {
            chunks.push(chunk);
        });

        res.on('end', function() {
            var data = Buffer.concat(chunks);
            if (DEBUG > 1) {
                console.log(data.toString())
            }
        });
    });

    req.on('error', (e) => {
        console.error(`problem with request: ${e.message}`);
    });

    req.write(postData);        
    req.end();
}


// listen for speech
tj.listen(function(msg) {

    // STOP
    if ( (msg.indexOf("stop") >= 0)
            || (msg.indexOf("halt") >= 0)
            || (msg.indexOf("idle") >= 0) ) {
        sendREST("stop");
        tj.shine('red');
    // FORWARD
    } else if ( (msg.indexOf("forward") >= 0)
            || (msg.indexOf("fore") >= 0) ) {
        sendREST("forward");
        tj.shine('green');
    // BACKWARD
    } else if (msg.indexOf("back") >= 0) {
        sendREST("backward");
        tj.shine('green');
    } else if ( (msg.indexOf("right") >= 0)
            || (msg.indexOf("rite") >= 0) ) {
        // RIGHT
        sendREST("right");
        tj.shine('yellow');
    // LEFT
    } else if (msg.indexOf("left") >= 0) {
        // LEFT
        sendREST("left");
        tj.shine('yellow');
    } else if (msg.indexOf("count") >= 0) {
        // COUNTER-CLOCKWISE (do this first as it also has "clock"
        sendREST("ccw");
        tj.shine('orange');
    } else if (msg.indexOf("clock") >= 0) {
        // CLOCKWISE
        sendREST("cw");
        tj.shine('orange');
    } else {
        // if in doubt, stop
        if (DEBUG > 1) {
            console.log('did not understand string of "' + msg +'"');
        }
        sendREST("stop");
        tj.shine('blue');        
    }
});
