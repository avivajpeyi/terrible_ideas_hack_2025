const int ledPins[] = {8, 9, 10, 11};
const int numLeds = 4;

void setup() {
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    handleCommand(Serial.read());
  }
}

void handleCommand(char command) {
  int ledIndex = -1;

  switch (command) {
    case 'R': ledIndex = 0; break;
    case 'L': ledIndex = 1; break;
    case 'D': ledIndex = 2; break;
    case 'U': ledIndex = 3; break;
    case 'F':
      Serial.println("Flash lights");
      for (int x = 0; x < 3; x++) {
        flashAllLights();
      }
      return;
  }

  if (ledIndex >= 0) {
    allLedsOff();
    digitalWrite(ledPins[ledIndex], HIGH);
    Serial.print("Activated LED ");
    Serial.println(ledIndex);
  }
}

void allLedsOff() {
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(ledPins[i], LOW);
  }
}

void flashAllLights() {
  for (int j = 0; j < 2; j++) {
    for (int i = 0; i < numLeds; i++) {
      digitalWrite(ledPins[i], HIGH);
    }
    delay(200);
    for (int i = 0; i < numLeds; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    delay(200);
  }
}