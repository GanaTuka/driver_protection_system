# Driver Protection System

A Python driver monitoring prototype that uses MediaPipe face landmarks to detect unsafe driver behavior and send stop/go commands to an Arduino car through an HC-05 Bluetooth module.

## Features

- Detects face presence, eye closure, and head direction.
- Stops the Arduino car when unsafe behavior lasts too long.
- Uses a real webcam for live face detection.
- Sends Bluetooth commands to Arduino using HC-05.

## Setup

On Windows, use PowerShell or the VS Code terminal:

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

If that window appears, run the full car system:

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
Connecting Bluetooth...
Bluetooth connected on COM7 at 9600 baud.
```

The camera window is opened before the face model and Bluetooth setup. This makes it easier to see whether the problem is camera/display, MediaPipe, or HC-05.

Controls:

- `c`: calibrate current face direction as forward
- `r`: reset stopped state
- `q`: quit

## Bluetooth

Bluetooth is configured in `config.py`.

```python
BLUETOOTH_ENABLED = True
BLUETOOTH_PORT = "COM7"
BLUETOOTH_BAUDRATE = 9600
BLUETOOTH_TIMEOUT_SECONDS = 1.0
BLUETOOTH_WRITE_TIMEOUT_SECONDS = 2.0
BLUETOOTH_STARTUP_DELAY_SECONDS = 2.0
BLUETOOTH_RETRY_SECONDS = 1.0
```

`COM7` is the default Windows Bluetooth serial port. If your HC-05 appears on another port, change `BLUETOOTH_PORT` in `config.py`.

Camera and debug switches are also in `config.py`.

```python
CAMERA_INDEX = 0
CAMERA_BACKEND = "DSHOW"
DISPLAY_ENABLED = True
STARTUP_CAMERA_PREVIEW_SECONDS = 3.0
FACE_ANALYSIS_ENABLED = True
```

For camera-only testing, temporarily set:

```python
FACE_ANALYSIS_ENABLED = False
BLUETOOTH_ENABLED = False
```

The Python app sends:

- `S`: stop Arduino car
- `G`: allow Arduino car to move again

To test only the HC-05/Arduino connection:

```powershell
python bluetooth_test.py --list
python bluetooth_test.py --port COM7 --send G
python bluetooth_test.py --port COM7 --send S
```

If `COM7` times out, try the other HC-05 COM port shown by `--list`. Windows usually creates one incoming port and one outgoing port; use the outgoing port.

For this project, run with Windows Python if you are using `COM7`.

## Arduino Wiring (HC-05 or HC-06)

Both modules use the same wiring:

```text
VCC        -> Arduino 5V
GND        -> Arduino GND
TXD        -> Arduino pin 2
RXD        -> Arduino pin 3 through voltage divider (1kΩ + 2kΩ to GND)
```

The voltage divider is needed because Arduino TX is 5V but HC-05/HC-06 RX expects 3.3V logic.

Arduino code reads from both:
- USB Serial (when connected via cable for programming/testing)
- HC-05/HC-06 Bluetooth on pins 2 and 3

The ready-to-upload Arduino Uno sketch is here:

```text
arduino/driver_protection_car/driver_protection_car.ino
```

Open that file in Arduino IDE and upload it to the Arduino Uno.

## HC-06 Setup Guide

HC-06 is often easier to use than HC-05 because:
- It's slave-only (no AT commands needed)
- Works out of the box at 9600 baud
- Same wiring as HC-05

**Steps to use HC-06:**

1. **Wire the HC-06:**
   ```text
   HC-06 VCC  -> Arduino 5V
   HC-06 GND  -> Arduino GND
   HC-06 TXD  -> Arduino pin 2
   HC-06 RXD  -> Arduino pin 3 through voltage divider
   ```

2. **Upload the Arduino sketch:**
   - Open `arduino/driver_protection_car/driver_protection_car.ino` in Arduino IDE
   - Upload to Arduino Uno (USB cable)

3. **Pair HC-06 with Windows:**
   - Power on Arduino + HC-06
   - HC-06 LED should blink rapidly (waiting to pair)
   - Go to Windows Bluetooth settings → Add device
   - Select "HC-06" (or similar)
   - Use PIN `1234` or `0000`
   - After pairing, check Windows Bluetooth settings → More Bluetooth options → COM Ports tab
   - You should see an **Outgoing** COM port (e.g., `COM8`)

4. **Update config.py:**
   Change `BLUETOOTH_PORT` to the outgoing COM port shown in Windows:
   ```python
   BLUETOOTH_PORT = "COM8"  # or whatever port Windows shows as outgoing
   ```

5. **Test the connection:**
   ```powershell
   python bluetooth_test.py --list
   python bluetooth_test.py --port COM8 --send G
   python bluetooth_test.py --port COM8 --send S
   ```
   Should show "Sent 1 byte(s)." for both commands.

6. **Run the full system:**
   ```powershell
   python main.py
   ```

## Troubleshooting HC-06

- If pairing fails: Try PIN `0000` instead of `1234`
- If no outgoing COM port appears: Remove device, power cycle HC-06, pair again
- If commands don't work: Verify wiring (especially voltage divider on RX)
- If Python can't open COM port: Close Arduino IDE Serial Monitor first

## Troubleshooting

If Bluetooth connects but the camera window does not appear, check these first:

- Run the project with local Windows Python if you are using `COM7`. WSL/Linux usually cannot show Windows COM ports and OpenCV windows the same way.
- Make sure no other app is using the webcam.
- If your camera is not index `0`, change `CAMERA_INDEX` in `config.py` to `1` or `2`.
- If the webcam light turns on but no window appears, run `python camera_test.py` and use `Alt+Tab` to find the `Driver Camera` window.
- If the window is off-screen, change `WINDOW_X` and `WINDOW_Y` in `config.py`.
- If the camera opens but freezes while loading, set `FACE_ANALYSIS_ENABLED = False` to test camera-only mode.
- If Bluetooth causes startup problems, set `BLUETOOTH_ENABLED = False` to test camera and face detection only.
- If the window freezes at `Connecting Bluetooth...`, make sure Arduino Serial Monitor is closed and try the other HC-05 outgoing COM port.
- If `bluetooth_test.py --port COM7 --send G` times out, the problem is the Bluetooth serial port/link, not `main.py`.
- If VS Code asks for camera permission, allow it.
