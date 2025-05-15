void setup() {
  Serial.begin(9600);
}

void loop() {
  int fsrValue = analogRead(A0);
  Serial.println(fsrValue);
  delay(200);  // Optional: slow down serial output
}

