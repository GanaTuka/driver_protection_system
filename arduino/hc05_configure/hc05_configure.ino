#include <SoftwareSerial.h>

SoftwareSerial BTSerial(2, 3); // RX, TX

void setup() {
  Serial.begin(9600);
  BTSerial.begin(38400); // HC-05 default is usually 38400

  Serial.println("Enter AT commands in Serial Monitor:");
  Serial.println("  AT");
  Serial.println("  AT+ROLE=0");
  Serial.println("  AT+UART=9600,0,0");
  Serial.println("  AT+CMODE=1");
  Serial.println("  AT+NAME=DriverProtectionCar");
  Serial.println();
}

void loop() {
  if (BTSerial.available()) {
    Serial.write(BTSerial.read());
  }
  if (Serial.available()) {
    BTSerial.write(Serial.read());
  }
}
