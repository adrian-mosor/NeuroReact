void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // Initialize onboard LED pin
}

void loop() {
  digitalWrite(LED_BUILTIN, LOW);   // LED on
  delay(500);
  digitalWrite(LED_BUILTIN, HIGH);  // LED off
  delay(500);
}

