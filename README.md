# Driver Protection System

A Python driver monitoring prototype that uses MediaPipe face landmarks to detect unsafe driver behavior and stop a road simulation. It can also send stop/go commands to an Arduino car through an HC-05 Bluetooth module.

## Features

- Detects face presence, eye closure, and head direction.
- Stops the road simulation when unsafe behavior lasts too long.
- Supports webcam input or a driver test video.
- Sends Bluetooth commands to Arduino using HC-05.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Controls:

- `c`: calibrate current face direction as forward
- `r`: reset stopped state
- `q`: quit

## Bluetooth

Bluetooth is configured in `config.py`.

```python
BLUETOOTH_ENABLED = True
BLUETOOTH_PORT = "/dev/rfcomm0"
BLUETOOTH_BAUDRATE = 9600
```

The Python app sends:

- `S`: stop Arduino car
- `G`: allow Arduino car to move again

Bind HC-05 on Linux after pairing:

```bash
sudo rfcomm bind /dev/rfcomm0 HC05_MAC_ADDRESS 1
```

## Arduino HC-05 Wiring

```text
HC-05 VCC  -> Arduino 5V
HC-05 GND  -> Arduino GND
HC-05 TXD  -> Arduino pin 2
HC-05 RXD  -> Arduino pin 3 through voltage divider
```

Arduino code should read Bluetooth on `SoftwareSerial BT(2, 3)` and stop when it receives `S`.
