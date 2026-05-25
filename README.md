# Driver Protection System

A Python driver monitoring system that uses MediaPipe face landmarks to detect unsafe driver behavior and send stop/go commands to an Arduino car through a **phone bridge** (phone relays TCP → Bluetooth HC-06).

## Architecture

```
Laptop (Python) → TCP/WiFi → Phone app → Bluetooth HC-06 → Arduino car
```

The laptop connects to the phone app over TCP/WiFi. The phone app forwards commands via Bluetooth to the HC-06 module on the Arduino car.

## Features

- Real-time face detection and head direction tracking
- Driver-specific face profile (only responds to the calibrated driver)
- Eye closure detection (drowsiness)
- Look left/right/up/down detection
- Sends `S` (stop) and `G` (go) commands via TCP to the phone
- Gentle brake on stop for smoother car deceleration
- Obstacle avoidance running on the Arduino (independent of Python)

## Setup

On Windows (PowerShell or VS Code terminal):

```powershell
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

On Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

First test only the webcam window:

```bash
python camera_test.py
```

If that window appears, run the full system:

```bash
python main.py
```

Expected startup messages:

```text
Opening camera index 0...
Camera opened at index 0.
Display window opened: Driver Camera
Loading face model...
Face model ready.
Loading driver profile...
Connecting to phone TCP server...
TCP connected to 192.168.1.100:8080
System ready
```

Controls:

- `c`: calibrate forward direction + save driver face profile
- `r`: reset stopped state
- `q`: quit

## Phone Bridge Setup

The laptop sends TCP commands to the phone app, which relays them via Bluetooth to HC-06.

**Requirements:**
- Phone connected to same WiFi network as laptop
- Android phone with a Bluetooth serial terminal app (e.g., "Serial Bluetooth Terminal" by Kai Morich)
- HC-06 wired to Arduino car (see wiring below)

**Configuration:**

1. Open the Bluetooth serial terminal app on your phone.
2. Connect to the HC-06 module via Bluetooth.
3. Set the app to **TCP server mode** (listening on a port, e.g., `8080`).
4. Note your phone's IP address on the WiFi network.

In `config.py`:

```python
TCP_ENABLED = True
TCP_HOST = "192.168.1.100"   # YOUR PHONE'S IP ADDRESS
TCP_PORT = 8080               # PORT YOUR PHONE APP IS LISTENING ON
TCP_TIMEOUT_SECONDS = 5.0
TCP_RECONNECT_SECONDS = 2.0
```

The Python app sends:

- `S`: stop Arduino car
- `G`: allow Arduino car to drive
- `X`: silent stop (no buzzer, used on quit)

## Driver Face Profile

When you press `C`, the system:
1. Calibrates forward direction
2. Saves your face landmarks as a driver profile

After calibration, the system only responds to the saved driver's face. If someone else sits in front of the camera, safety detection is paused (no false stops).

To clear the saved profile, delete `assets/driver_profile.npy`.

Configured in `config.py`:

```python
DRIVER_PROFILE_ENABLED = True
DRIVER_PROFILE_MATCH_THRESHOLD = 0.85
DRIVER_PROFILE_PATH = "assets/driver_profile.npy"
```

## Arduino Wiring (HC-06)

```text
HC-06 VCC  -> Arduino 5V
HC-06 GND  -> Arduino GND
HC-06 TXD  -> Arduino pin 2
HC-06 RXD  -> Arduino pin 3 through voltage divider (1kΩ + 2kΩ to GND)
```

The voltage divider is needed because Arduino TX is 5V but HC-06 RX expects 3.3V logic.

The Arduino sketch reads from both:
- USB Serial (for programming/debugging)
- HC-06 Bluetooth on pins 2 and 3

Upload the sketch:

```text
arduino/driver_protection_car/driver_protection_car.ino
```

Open that file in Arduino IDE and upload it to the Arduino Uno.

## Camera-Only Testing

If you want to test only the camera and face detection without connecting to the car:

```python
TCP_ENABLED = False
```

Then run:

```bash
python main.py
```

## Troubleshooting

- **Car does not move**: Make sure the phone app is running in TCP server mode and connected to HC-06.
- **TCP connection fails**: Verify the phone's IP address and port. Both devices must be on the same WiFi network.
- **Face profile not working**: Press `C` while looking directly at the camera. Make sure your face is clearly visible.
- **Camera window does not appear**: Run `python camera_test.py` first. Use `Alt+Tab` to find the window.
- **Webcam not working**: Close other apps using the camera. Change `CAMERA_INDEX` in `config.py` to `1` or `2`.
