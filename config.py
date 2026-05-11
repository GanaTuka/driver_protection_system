# config.py

# =========================
# Driver input source
# =========================
USE_VIDEO_FILE_FOR_DRIVER = False
DRIVER_VIDEO_PATH = "assets/driver_test.mp4"

# =========================
# Camera
# =========================
CAMERA_INDEX = 0
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480

# =========================
# Simulation video + sound
# =========================
ROAD_SIMULATOR_ENABLED = False
ROAD_VIDEO_PATH = "assets/road_video.mp4"
WARNING_SOUND_PATH = "assets/warning.wav"
WARNING_SOUND_DURATION_SECONDS = 1.0

# =========================
# MediaPipe model
# =========================
FACE_LANDMARKER_MODEL_PATH = "assets/models/face_landmarker.task"

# =========================
# Window names
# =========================
WEBCAM_WINDOW_NAME = "Driver Camera"
ROAD_WINDOW_NAME = "Road Simulation"

# =========================
# Safety timing thresholds
# Increased to reduce false STOPs
# =========================
EYE_CLOSED_STOP_SECONDS = 5.0
LOOK_LEFT_STOP_SECONDS = 5.0
LOOK_RIGHT_STOP_SECONDS = 5.0
LOOK_UP_STOP_SECONDS = 5.0
LOOK_DOWN_STOP_SECONDS = 5.0
NO_FACE_STOP_SECONDS = 5.0

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
# Bluetooth / HC-05
# =========================
BLUETOOTH_ENABLED = True
BLUETOOTH_PORT = "COM7"
BLUETOOTH_BAUDRATE = 9600
BLUETOOTH_STOP_COMMAND = "S"
BLUETOOTH_GO_COMMAND = "G"

# =========================
# UI / behavior
# =========================
SHOW_DEBUG_TEXT = True
STOP_LATCHED = True
