#include <Servo.h>
#include <NewPing.h>
#include <SoftwareSerial.h>

// ================= MOTOR =================
const int LeftMotorForward = 7;
const int LeftMotorBackward = 6;
const int RightMotorForward = 5;
const int RightMotorBackward = 4;

#define ENA 9
#define ENB 11

// ================= ULTRASONIC =================
#define trig_pin A1
#define echo_pin A2
#define maximum_distance 200

NewPing sonar(trig_pin, echo_pin, maximum_distance);
Servo servo_motor;

// ================= HC-06 =================
// HC-06 TXD -> Arduino pin 2
// HC-06 RXD -> Arduino pin 3 through voltage divider
SoftwareSerial BT(2, 3);

// ================= BUZZER =================
#define buzzerPin 8

// ================= VARIABLES =================
int distance = 100;
bool goesForward = false;
bool remoteStopped = true;
bool firstStopReceived = false;

// =================================================

void setup() {
  Serial.begin(9600);
  BT.begin(9600);

  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorForward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  pinMode(buzzerPin, OUTPUT);

  servo_motor.attach(10);
  servo_motor.write(115);

  moveStop();
  Serial.println("Driver protection car ready.");
  delay(500);
}

// =================================================

void loop() {
  readBluetoothCommand();

  if (remoteStopped) {
    moveStop();
    if (firstStopReceived) beepUntilGo();
    return;
  }

  runObstacleAvoidance();
}

// =================================================

void processCommand(char c) {
  if (c == 'S') {
    remoteStopped = true;
    firstStopReceived = true;
    moveStop();
  } else if (c == 'X') {
    remoteStopped = true;
    firstStopReceived = false;
    moveStop();
  } else if (c == 'G') {
    remoteStopped = false;
  }
}

void readBluetoothCommand() {
  while (Serial.available()) {
    processCommand(Serial.read());
  }
  while (BT.available()) {
    processCommand(BT.read());
  }
}

// =================================================

void runObstacleAvoidance() {
  distance = readPing();

  if (distance <= 20) {
    moveStop();
    beepContinuous(250);

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

void beepUntilGo() {
  while (remoteStopped && firstStopReceived) {
    readBluetoothCommand();

    for (int i = 0; i < 3 && remoteStopped; i++) {
      digitalWrite(buzzerPin, HIGH);
      delay(150);
      digitalWrite(buzzerPin, LOW);
      delay(120);
    }

    if (remoteStopped) delay(400);
  }

  digitalWrite(buzzerPin, LOW);
}

void beepContinuous(unsigned long duration) {
  unsigned long start = millis();
  bool state = false;

  while (millis() - start < duration) {
    readBluetoothCommand();
    if (!remoteStopped) {
      moveStop();
      return;
    }

    state = !state;
    digitalWrite(buzzerPin, state ? HIGH : LOW);
    delay(100);
  }

  digitalWrite(buzzerPin, LOW);
}

// =================================================

int lookRight() {
  servo_motor.write(50);
  delayWithBluetoothCheck(500);
  int dist = readPing();
  delayWithBluetoothCheck(100);
  servo_motor.write(115);
  return dist;
}

int lookLeft() {
  servo_motor.write(170);
  delayWithBluetoothCheck(500);
  int dist = readPing();
  delayWithBluetoothCheck(100);
  servo_motor.write(115);
  return dist;
}

int readPing() {
  delayWithBluetoothCheck(70);
  int cm = sonar.ping_cm();
  return cm == 0 ? 250 : cm;
}

// ================= MOVEMENT =================

void moveStop() {
  if (goesForward) {
    goesForward = false;

    // ramp down PWM for smooth deceleration
    for (int speed = 255; speed >= 0; speed -= 15) {
      analogWrite(ENA, speed);
      analogWrite(ENB, speed);
      delay(15);
    }

    // short reverse brake
    digitalWrite(LeftMotorForward, LOW);
    digitalWrite(RightMotorForward, LOW);
    digitalWrite(LeftMotorBackward, HIGH);
    digitalWrite(RightMotorBackward, HIGH);
    delay(50);
    digitalWrite(LeftMotorBackward, LOW);
    digitalWrite(RightMotorBackward, LOW);
  } else {
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    digitalWrite(RightMotorForward, LOW);
    digitalWrite(LeftMotorForward, LOW);
    digitalWrite(RightMotorBackward, LOW);
    digitalWrite(LeftMotorBackward, LOW);
  }
}

// =================================================

void moveForward() {
  if (!goesForward) {
    goesForward = true;

    digitalWrite(LeftMotorForward, HIGH);
    digitalWrite(RightMotorForward, HIGH);
    digitalWrite(LeftMotorBackward, LOW);
    digitalWrite(RightMotorBackward, LOW);

    analogWrite(ENA, 255);
    analogWrite(ENB, 255);
  }
}

void moveBackward() {
  goesForward = false;

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorForward, LOW);

  analogWrite(ENA, 255);
  analogWrite(ENB, 255);
}

// =================================================

void turnRight() {
  goesForward = false;

  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);

  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  delayWithBluetoothCheck(250);
  moveStop();
}

void turnLeft() {
  goesForward = false;

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);

  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  delayWithBluetoothCheck(250);
  moveStop();
}
