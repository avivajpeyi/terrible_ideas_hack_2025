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