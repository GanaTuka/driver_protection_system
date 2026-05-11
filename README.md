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

For this project, run with Windows Python if you are using `COM7`.

## Arduino HC-05 Wiring

```text
HC-05 VCC  -> Arduino 5V
HC-05 GND  -> Arduino GND
HC-05 TXD  -> Arduino pin 2
HC-05 RXD  -> Arduino pin 3 through voltage divider
```

Arduino code should read Bluetooth on `SoftwareSerial BT(2, 3)` and stop when it receives `S`.

## Troubleshooting

If Bluetooth connects but the camera window does not appear, check these first:

- Run the project with local Windows Python if you are using `COM7`. WSL/Linux usually cannot show Windows COM ports and OpenCV windows the same way.
- Make sure no other app is using the webcam.
- If your camera is not index `0`, change `CAMERA_INDEX` in `config.py` to `1` or `2`.
- If the webcam light turns on but no window appears, run `python camera_test.py` and use `Alt+Tab` to find the `Driver Camera` window.
- If the window is off-screen, change `WINDOW_X` and `WINDOW_Y` in `config.py`.
- If the camera opens but freezes while loading, set `FACE_ANALYSIS_ENABLED = False` to test camera-only mode.
- If Bluetooth causes startup problems, set `BLUETOOTH_ENABLED = False` to test camera and face detection only.
- If VS Code asks for camera permission, allow it.
