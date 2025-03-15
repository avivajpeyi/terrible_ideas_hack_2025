# ml_game_controller

Needs 

python 3.10/.11


```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
wget -O pose_landmarker.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task
```


# Arduino setup
We have a ESP8266 board. We need to get it to work with the Arduino IDE.

https://www.instructables.com/ESP8266-and-Python-Communication-ForNoobs/


### 
```

To trigger an Arduino Uno from Python, you can use serial communication, specifically the pySerial library for Python and the Firmata library for Arduino, allowing you to send commands from your Python script to control the Arduino board. 
Here's a breakdown of the process:
1. Arduino Setup:
Install the Firmata Library:
In the Arduino IDE, go to Sketch > Include Library > Add .ZIP Library... and select the StandardFirmata library.
Upload StandardFirmata Sketch:
Open the StandardFirmata example sketch (File > Examples > Firmata > StandardFirmata) and upload it to your Arduino Uno. 
2. Python Setup:
Install pySerial: Open a terminal or command prompt and install the library using pip install pyserial.
Import the library: In your Python script, import the serial module: import serial. 
3. Python Script:
Python


import serial

# Replace 'COM3' with the correct port for your Arduino
arduino = serial.Serial('COM3', 115200)

# Function to send commands to Arduino
def send_command(command):
    arduino.write(command.encode('utf-8')) # Encode to bytes
    # Add a small delay to allow the Arduino to process the command
    time.sleep(0.05)

# Example: Turn on an LED (assuming pin 13)
send_command("1") # Send command to turn on the LED
# Example: Turn off an LED (assuming pin 13)
send_command("0") # Send command to turn off the LED
4. Arduino Sketch:
Code

// Arduino sketch to receive commands from Python
void setup() {
  pinMode(13, OUTPUT); // Assuming LED is connected to pin 13
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    int command = Serial.read();
    if (command == '1') {
      digitalWrite(13, HIGH); // Turn on LED
    } else if (command == '0') {
      digitalWrite(13, LOW); // Turn off LED
    }
  }
}
Explanation:
Serial Communication:
The Python script uses pySerial to establish a serial connection with the Arduino.
Commands:
The Python script sends commands (e.g., "1" for on, "0" for off) to the Arduino via the serial port.
Arduino Receives:
The Arduino sketch reads the serial data and interprets it as commands to control the LED (or other hardware). 
Important Notes:
Port:
Ensure you replace 'COM3' in the Python script with the correct COM port that your Arduino is connected to. 
Baud Rate:
Make sure the baud rate in the Python script matches the baud rate in the Arduino sketch (115200 in this example). 
Encoding:
When sending data from Python, ensure it's encoded to bytes using command.encode('utf-8'). 
Firmata:
pyFirmata provides a more structured approach for controlling Arduino from Python, offering a wider range of functionalities. Real Python Tutorials


``` 