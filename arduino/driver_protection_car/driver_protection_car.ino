#include <Servo.h>
#include <NewPing.h>
#include <SoftwareSerial.h>

// ================= MOTOR =================
const int LeftMotorForward = 7;
const int LeftMotorBackward = 6;
const int RightMotorForward = 5;
const int RightMotorBackward = 4;

// ================= ULTRASONIC =================
#define trig_pin A1
#define echo_pin A2
#define maximum_distance 200

NewPing sonar(trig_pin, echo_pin, maximum_distance);
Servo servo_motor;

// ================= HC-05 =================
// HC-05 TXD -> Arduino pin 2
// HC-05 RXD -> Arduino pin 3 through a voltage divider
SoftwareSerial BT(2, 3); // RX, TX

// ================= BUZZER =================
#define buzzerPin 8

// ================= VARIABLES =================
int distance = 100;
bool goesForward = false;

// Start stopped for safety. Python must send 'G' before the car drives.
bool remoteStopped = true;

// =================================================

void setup() {
  Serial.begin(9600);
  BT.begin(9600);

  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorForward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  servo_motor.attach(10);
  servo_motor.write(115);

  moveStop();

  Serial.println("Driver protection car ready.");
  Serial.println("Bluetooth commands: S=stop, G=go");

  beep(2);
  delay(1000);
}

// =================================================

void loop() {
  readBluetoothCommand();

  if (remoteStopped) {
    moveStop();
    return;
  }

  runObstacleAvoidance();
}

// =================================================

void readBluetoothCommand() {
  while (BT.available()) {
    char c = BT.read();

    Serial.print("BT received: ");
    Serial.println(c);

    if (c == 'S') {
      remoteStopped = true;
      moveStop();
      beep(1);
      Serial.println("Safety STOP active");
    } else if (c == 'G') {
      remoteStopped = false;
      Serial.println("Car allowed to drive");
    }
  }
}

// =================================================

void runObstacleAvoidance() {
  distance = readPing();

  if (distance <= 20) {
    moveStop();
    beep(1);

    delayWithBluetoothCheck(300);
    if (remoteStopped) return;

    moveBackward();
    delayWithBluetoothCheck(400);
    if (remoteStopped) return;

    moveStop();
    delayWithBluetoothCheck(300);
    if (remoteStopped) return;

    int distanceRight = lookRight();
    delayWithBluetoothCheck(300);
    if (remoteStopped) return;

    int distanceLeft = lookLeft();
    delayWithBluetoothCheck(300);
    if (remoteStopped) return;

    if (distanceRight >= distanceLeft) {
      turnRight();
    } else {
      turnLeft();
    }

    moveStop();
  } else {
    moveForward();
  }
}

// =================================================

void delayWithBluetoothCheck(unsigned long ms) {
  unsigned long startTime = millis();

  while (millis() - startTime < ms) {
    readBluetoothCommand();

    if (remoteStopped) {
      moveStop();
      return;
    }

    delay(10);
  }
}

// =================================================

void beep(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(buzzerPin, HIGH);
    delay(150);
    digitalWrite(buzzerPin, LOW);
    delay(100);
  }
}

// =================================================

int lookRight() {
  servo_motor.write(50);
  delayWithBluetoothCheck(500);

  int distance = readPing();

  delayWithBluetoothCheck(100);
  servo_motor.write(115);

  return distance;
}

// =================================================

int lookLeft() {
  servo_motor.write(170);
  delayWithBluetoothCheck(500);

  int distance = readPing();

  delayWithBluetoothCheck(100);
  servo_motor.write(115);

  return distance;
}

// =================================================

int readPing() {
  delayWithBluetoothCheck(70);

  int cm = sonar.ping_cm();

  if (cm == 0) {
    cm = 250;
  }

  return cm;
}

// ================= MOVEMENT =================

void moveStop() {
  goesForward = false;

  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorBackward, LOW);
}

// =================================================

void moveForward() {
  if (!goesForward) {
    goesForward = true;

    digitalWrite(LeftMotorForward, HIGH);
    digitalWrite(RightMotorForward, HIGH);

    digitalWrite(LeftMotorBackward, LOW);
    digitalWrite(RightMotorBackward, LOW);
  }
}

// =================================================

void moveBackward() {
  goesForward = false;

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);

  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorForward, LOW);
}

// =================================================

void turnRight() {
  goesForward = false;

  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);

  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);

  delayWithBluetoothCheck(250);
  moveStop();
}

// =================================================

void turnLeft() {
  goesForward = false;

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorForward, HIGH);

  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);

  delayWithBluetoothCheck(250);
  moveStop();
}
