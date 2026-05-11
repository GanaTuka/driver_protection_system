# main.py

import cv2

from config import (
    USE_VIDEO_FILE_FOR_DRIVER,
    DRIVER_VIDEO_PATH,
    CAMERA_INDEX,
    WEBCAM_WIDTH,
    WEBCAM_HEIGHT,
    ROAD_SIMULATOR_ENABLED,
    ROAD_VIDEO_PATH,
    WARNING_SOUND_PATH,
    WARNING_SOUND_DURATION_SECONDS,
    FACE_LANDMARKER_MODEL_PATH,
    WEBCAM_WINDOW_NAME,
    ROAD_WINDOW_NAME,
    SHOW_DEBUG_TEXT,
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
)
from simulator import RoadSimulator
from safety_logic import SafetyLogic
from face_analysis import FaceAnalyzer
from bluetooth_control import BluetoothController


def draw_status(frame, state, reason=None, warning_active=False):
    output = frame.copy()

    if state == "STOP":
        cv2.putText(output, "STOP", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        if reason:
            cv2.putText(output, f"Reason: {reason}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    elif warning_active:
        cv2.putText(output, "WARNING", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
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


def open_driver_source():
    if USE_VIDEO_FILE_FOR_DRIVER:
        cap = cv2.VideoCapture(DRIVER_VIDEO_PATH)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open driver video: {DRIVER_VIDEO_PATH}")
        return cap

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")
    return cap


def main():
    driver_source = open_driver_source()

    simulator = None
    if ROAD_SIMULATOR_ENABLED:
        simulator = RoadSimulator(
            video_path=ROAD_VIDEO_PATH,
            warning_sound_path=WARNING_SOUND_PATH,
            warning_duration=WARNING_SOUND_DURATION_SECONDS,
        )

    logic = SafetyLogic(
        eye_closed_stop_seconds=EYE_CLOSED_STOP_SECONDS,
        look_left_stop_seconds=LOOK_LEFT_STOP_SECONDS,
        look_right_stop_seconds=LOOK_RIGHT_STOP_SECONDS,
        look_up_stop_seconds=LOOK_UP_STOP_SECONDS,
        look_down_stop_seconds=LOOK_DOWN_STOP_SECONDS,
        no_face_stop_seconds=NO_FACE_STOP_SECONDS,
        stop_latched=STOP_LATCHED,
    )

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
            if USE_VIDEO_FILE_FOR_DRIVER:
                print("Driver video ended.")
            else:
                print("Could not read driver frame.")
            break

        if not USE_VIDEO_FILE_FOR_DRIVER:
            driver_frame = cv2.flip(driver_frame, 1)

        analysis = analyzer.analyze(driver_frame)
        logic.update(analysis)

        if logic.is_stopped():
            if simulator is not None:
                simulator.stop()
            bluetooth.send_stop()
        else:
            bluetooth.send_go()

        warning_active = simulator is not None and simulator.is_warning_active()
        timers = logic.get_timers()

        webcam_display = draw_status(
            driver_frame,
            logic.state,
            logic.stop_reason,
            warning_active=warning_active,
        )
        webcam_display = draw_analysis_overlay(webcam_display, analysis, timers)

        cv2.imshow(WEBCAM_WINDOW_NAME, webcam_display)

        if simulator is not None:
            road_frame = simulator.read_frame()
            road_display = draw_status(
                road_frame,
                logic.state,
                logic.stop_reason,
                warning_active=warning_active,
            )

            if SHOW_DEBUG_TEXT:
                cv2.putText(
                    road_display,
                    f"Driver source: {'video file' if USE_VIDEO_FILE_FOR_DRIVER else 'webcam'}",
                    (20, road_display.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            cv2.imshow(ROAD_WINDOW_NAME, road_display)

        key = cv2.waitKey(20) & 0xFF

        if key == ord("c"):
            if analysis["face_detected"]:
                analyzer.calibrate_forward_from_raw()
                print("Forward direction calibrated from raw pose.")

        elif key == ord("r"):
            logic.reset()
            if simulator is not None:
                simulator.reset()

        elif key == ord("q"):
            break

    driver_source.release()
    if simulator is not None:
        simulator.release()
    analyzer.close()
    bluetooth.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
