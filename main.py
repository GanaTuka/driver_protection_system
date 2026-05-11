# main.py

import platform
import time

import cv2

from config import (
    CAMERA_INDEX,
    CAMERA_BACKEND,
    WEBCAM_WIDTH,
    WEBCAM_HEIGHT,
    FACE_LANDMARKER_MODEL_PATH,
    WEBCAM_WINDOW_NAME,
    WINDOW_X,
    WINDOW_Y,
    WINDOW_TOPMOST,
    STOP_LATCHED,
    EYE_CLOSED_STOP_SECONDS,
    LOOK_LEFT_STOP_SECONDS,
    LOOK_RIGHT_STOP_SECONDS,
    LOOK_UP_STOP_SECONDS,
    LOOK_DOWN_STOP_SECONDS,
    NO_FACE_STOP_SECONDS,
    EAR_CLOSED_THRESHOLD,
    YAW_LEFT_THRESHOLD,
    YAW_RIGHT_THRESHOLD,
    PITCH_UP_THRESHOLD,
    PITCH_DOWN_THRESHOLD,
    FORWARD_YAW_DEADZONE,
    FORWARD_PITCH_DEADZONE,
    SMOOTHING_ALPHA,
    BLUETOOTH_ENABLED,
    BLUETOOTH_PORT,
    BLUETOOTH_BAUDRATE,
    BLUETOOTH_STOP_COMMAND,
    BLUETOOTH_GO_COMMAND,
    DISPLAY_ENABLED,
    STARTUP_CAMERA_PREVIEW_SECONDS,
    FACE_ANALYSIS_ENABLED,
)
from safety_logic import SafetyLogic
from face_analysis import FaceAnalyzer
from bluetooth_control import BluetoothController


def draw_status(frame, state, reason=None):
    output = frame.copy()

    if state == "STOP":
        cv2.putText(output, "STOP", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        if reason:
            cv2.putText(output, f"Reason: {reason}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        cv2.putText(output, "NORMAL", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    return output


def draw_analysis_overlay(frame, analysis, timers):
    output = frame.copy()
    h = output.shape[0]

    if analysis["face_detected"]:
        cv2.putText(output, f"EAR: {analysis['avg_ear']:.3f}", (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.putText(output, f"Direction: {analysis['head_direction']}", (20, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.putText(output, f"Yaw: {analysis['yaw']:.1f}  Pitch: {analysis['pitch']:.1f}", (20, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if "left_eye_points" in analysis:
            for p in analysis["left_eye_points"]:
                cv2.circle(output, p, 2, (0, 255, 0), -1)
            for p in analysis["right_eye_points"]:
                cv2.circle(output, p, 2, (0, 255, 0), -1)

    else:
        cv2.putText(output, "No face detected", (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.putText(output, f"Eyes timer: {timers['eyes_closed']:.1f}s", (20, 260),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(output, f"Left timer: {timers['look_left']:.1f}s", (20, 290),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(output, f"Right timer: {timers['look_right']:.1f}s", (20, 320),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(output, f"Up timer: {timers['look_up']:.1f}s", (20, 350),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(output, f"Down timer: {timers['look_down']:.1f}s", (20, 380),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(output, f"No-face timer: {timers['no_face']:.1f}s", (20, 410),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.putText(output, "c=CALIBRATE  r=RESET  q=QUIT", (20, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return output


def draw_message(frame, message):
    output = frame.copy()
    cv2.putText(output, message, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return output


def open_driver_source():
    backend = get_camera_backend()

    print(f"Opening camera index {CAMERA_INDEX}...")
    cap = cv2.VideoCapture(CAMERA_INDEX, backend)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam at CAMERA_INDEX={CAMERA_INDEX}.")

    ret, _ = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Webcam opened, but no frames were received.")

    print(f"Camera opened at index {CAMERA_INDEX}.")
    return cap


def get_camera_backend():
    if platform.system() != "Windows":
        return cv2.CAP_ANY

    if CAMERA_BACKEND.upper() == "DSHOW":
        return cv2.CAP_DSHOW
    if CAMERA_BACKEND.upper() == "MSMF":
        return cv2.CAP_MSMF
    return cv2.CAP_ANY


def open_display_window():
    if not DISPLAY_ENABLED:
        return

    try:
        cv2.startWindowThread()
        cv2.namedWindow(WEBCAM_WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WEBCAM_WINDOW_NAME, WEBCAM_WIDTH, WEBCAM_HEIGHT)
        cv2.moveWindow(WEBCAM_WINDOW_NAME, WINDOW_X, WINDOW_Y)
        if WINDOW_TOPMOST:
            cv2.setWindowProperty(WEBCAM_WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)
        print(f"Display window opened: {WEBCAM_WINDOW_NAME}")
    except cv2.error as exc:
        raise RuntimeError(
            "Could not open the OpenCV display window. Run this with a desktop session, "
            "not a headless terminal or WSL without GUI support."
        ) from exc


def show_startup_frame(driver_source, message):
    ret, frame = driver_source.read()
    if not ret:
        raise RuntimeError("Could not read webcam frame during startup.")

    frame = cv2.flip(frame, 1)
    if DISPLAY_ENABLED:
        cv2.imshow(WEBCAM_WINDOW_NAME, draw_message(frame, message))
        cv2.waitKey(1)


def run_startup_camera_preview(driver_source):
    if not DISPLAY_ENABLED or STARTUP_CAMERA_PREVIEW_SECONDS <= 0:
        return

    print(f"Showing camera preview for {STARTUP_CAMERA_PREVIEW_SECONDS:.1f} seconds...")
    end_at = time.time() + STARTUP_CAMERA_PREVIEW_SECONDS

    while time.time() < end_at:
        ret, frame = driver_source.read()
        if not ret:
            raise RuntimeError("Could not read webcam frame during startup preview.")

        frame = cv2.flip(frame, 1)
        preview = draw_message(frame, "Camera preview - press q to quit")
        cv2.imshow(WEBCAM_WINDOW_NAME, preview)

        if cv2.waitKey(20) & 0xFF == ord("q"):
            raise KeyboardInterrupt

    if WINDOW_TOPMOST:
        cv2.setWindowProperty(WEBCAM_WINDOW_NAME, cv2.WND_PROP_TOPMOST, 0)


def main():
    driver_source = open_driver_source()
    open_display_window()

    show_startup_frame(driver_source, "Camera ready")
    run_startup_camera_preview(driver_source)

    logic = SafetyLogic(
        eye_closed_stop_seconds=EYE_CLOSED_STOP_SECONDS,
        look_left_stop_seconds=LOOK_LEFT_STOP_SECONDS,
        look_right_stop_seconds=LOOK_RIGHT_STOP_SECONDS,
        look_up_stop_seconds=LOOK_UP_STOP_SECONDS,
        look_down_stop_seconds=LOOK_DOWN_STOP_SECONDS,
        no_face_stop_seconds=NO_FACE_STOP_SECONDS,
        stop_latched=STOP_LATCHED,
    )

    analyzer = None
    if FACE_ANALYSIS_ENABLED:
        print("Loading face model...")
        show_startup_frame(driver_source, "Loading face model...")
        analyzer = FaceAnalyzer(
            model_path=FACE_LANDMARKER_MODEL_PATH,
            ear_closed_threshold=EAR_CLOSED_THRESHOLD,
            yaw_left_threshold=YAW_LEFT_THRESHOLD,
            yaw_right_threshold=YAW_RIGHT_THRESHOLD,
            pitch_up_threshold=PITCH_UP_THRESHOLD,
            pitch_down_threshold=PITCH_DOWN_THRESHOLD,
            forward_yaw_deadzone=FORWARD_YAW_DEADZONE,
            forward_pitch_deadzone=FORWARD_PITCH_DEADZONE,
            smoothing_alpha=SMOOTHING_ALPHA,
        )
        print("Face model ready.")

    print("Connecting Bluetooth...")
    show_startup_frame(driver_source, "Connecting Bluetooth...")
    bluetooth = BluetoothController(
        enabled=BLUETOOTH_ENABLED,
        port=BLUETOOTH_PORT,
        baudrate=BLUETOOTH_BAUDRATE,
        stop_command=BLUETOOTH_STOP_COMMAND,
        go_command=BLUETOOTH_GO_COMMAND,
    )

    print("Controls:")
    print("  c = calibrate forward")
    print("  r = reset")
    print("  q = quit")

    while True:
        ret, driver_frame = driver_source.read()
        if not ret:
            print("Could not read driver frame from webcam.")
            break

        driver_frame = cv2.flip(driver_frame, 1)

        if analyzer is not None:
            analysis = analyzer.analyze(driver_frame)
            logic.update(analysis)
        else:
            analysis = {
                "face_detected": False,
                "eyes_closed": False,
                "head_direction": "DISABLED",
                "avg_ear": 0.0,
                "yaw": 0.0,
                "pitch": 0.0,
            }

        if logic.is_stopped():
            bluetooth.send_stop()
        else:
            bluetooth.send_go()

        timers = logic.get_timers()

        webcam_display = draw_status(
            driver_frame,
            logic.state,
            logic.stop_reason,
        )
        webcam_display = draw_analysis_overlay(webcam_display, analysis, timers)

        if DISPLAY_ENABLED:
            cv2.imshow(WEBCAM_WINDOW_NAME, webcam_display)

        key = cv2.waitKey(20) & 0xFF if DISPLAY_ENABLED else 255

        if key == ord("c"):
            if analyzer is not None and analysis["face_detected"]:
                analyzer.calibrate_forward_from_raw()
                print("Forward direction calibrated from raw pose.")

        elif key == ord("r"):
            logic.reset()

        elif key == ord("q"):
            break

    driver_source.release()
    if analyzer is not None:
        analyzer.close()
    bluetooth.close()
    if DISPLAY_ENABLED:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
