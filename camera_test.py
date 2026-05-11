import platform

import cv2

from config import (
    CAMERA_BACKEND,
    CAMERA_INDEX,
    WEBCAM_HEIGHT,
    WEBCAM_WIDTH,
    WEBCAM_WINDOW_NAME,
    WINDOW_TOPMOST,
    WINDOW_X,
    WINDOW_Y,
)


def get_camera_backend():
    if platform.system() != "Windows":
        return cv2.CAP_ANY

    if CAMERA_BACKEND.upper() == "DSHOW":
        return cv2.CAP_DSHOW
    if CAMERA_BACKEND.upper() == "MSMF":
        return cv2.CAP_MSMF
    return cv2.CAP_ANY


def main():
    print(f"Opening camera index {CAMERA_INDEX} for display test...")
    cap = cv2.VideoCapture(CAMERA_INDEX, get_camera_backend())
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam at CAMERA_INDEX={CAMERA_INDEX}.")

    cv2.namedWindow(WEBCAM_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WEBCAM_WINDOW_NAME, WEBCAM_WIDTH, WEBCAM_HEIGHT)
    cv2.moveWindow(WEBCAM_WINDOW_NAME, WINDOW_X, WINDOW_Y)
    if WINDOW_TOPMOST:
        cv2.setWindowProperty(WEBCAM_WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    print("Camera test window should be visible now. Press q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        cv2.putText(frame, "Camera test - press q", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.imshow(WEBCAM_WINDOW_NAME, frame)

        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
