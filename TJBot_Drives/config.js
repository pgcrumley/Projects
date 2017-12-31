/*
User-specific configuration
    ** IMPORTANT NOTE ********************
    * Please ensure you do not interchange your username and password.
    * Hint: Your username is the lengthy value ~ 36 digits including a hyphen
    * Hint: Your password is the smaller value ~ 12 characters
*/

// Create the credentials object for export
exports.credentials = {};

// Watson Speech to Text
// https://www.ibm.com/watson/developercloud/speech-to-text.html
exports.credentials.speech_to_text = {
        url: "https://stream.watsonplatform.net/speech-to-text/api",
        username: "1068d827-f330-4c30-8f18-580bb28e342c",
        password: "sFmNgygTufe4"
}

exports.drive_server_address = 127.0.0.1; // by default use "localhost"
exports.drive_server_port = 9999;  // by default use IP port 9999
