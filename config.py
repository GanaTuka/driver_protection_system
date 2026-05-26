# config.py

# =========================
# Driver camera
# =========================
CAMERA_INDEX = 0
CAMERA_BACKEND = "DSHOW"
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480

# =========================
# MediaPipe model
# =========================
FACE_LANDMARKER_MODEL_PATH = "assets/models/face_landmarker.task"

# =========================
# Window names
# =========================
WEBCAM_WINDOW_NAME = "Driver Camera"
WINDOW_X = 80
WINDOW_Y = 80
WINDOW_TOPMOST = True

# =========================
# Safety timing thresholds
# Increased to reduce false STOPs
# =========================
EYE_CLOSED_STOP_SECONDS = 5.0
LOOK_LEFT_STOP_SECONDS = 5.0
LOOK_RIGHT_STOP_SECONDS = 5.0
LOOK_UP_STOP_SECONDS = 5.0
LOOK_DOWN_STOP_SECONDS = 5.0
NO_FACE_STOP_SECONDS = 3.0

# =========================
# Eye threshold
# Lower = harder to count as closed
# =========================
EAR_CLOSED_THRESHOLD = 0.17

# =========================
# Head direction thresholds
# Wider values = less sensitive
# =========================
YAW_LEFT_THRESHOLD = 35.0
YAW_RIGHT_THRESHOLD = -35.0
PITCH_UP_THRESHOLD = -35.0
PITCH_DOWN_THRESHOLD = 35.0
# =========================
# Forward dead-zone
# Bigger dead-zone = easier to show FORWARD
# =========================
FORWARD_YAW_DEADZONE = 24.0
FORWARD_PITCH_DEADZONE = 28.0

# =========================
# Smoothing
# Lower = smoother, less jumpy
# =========================
SMOOTHING_ALPHA = 0.12

# =========================
# TCP -> Phone -> Bluetooth (HC-06)
# =========================
TCP_ENABLED = True
TCP_HOST = "192.168.1.27"
TCP_PORT = 6000
TCP_TIMEOUT_SECONDS = 5.0
TCP_RECONNECT_SECONDS = 2.0
TCP_STOP_COMMAND = "S"
TCP_GO_COMMAND = "G"

# =========================
# Driver profile (face-based driver authentication)
# =========================
DRIVER_PROFILE_ENABLED = True
DRIVER_PROFILE_MATCH_THRESHOLD = 0.85
DRIVER_PROFILE_PATH = "assets/driver_profile.npy"

# =========================
# Face capture
# =========================
FACE_CAPTURE_ENABLED = True
FACE_CAPTURE_DIR = "captures"

# =========================
# UI / behavior
# =========================
DISPLAY_ENABLED = True
STARTUP_CAMERA_PREVIEW_SECONDS = 3.0
FACE_ANALYSIS_ENABLED = True
STOP_LATCHED = False
