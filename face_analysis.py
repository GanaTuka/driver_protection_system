# face_analysis.py

import cv2
import math
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

POSE_LANDMARKS = {
    "nose_tip": 1,
    "chin": 152,
    "left_eye_outer": 33,
    "right_eye_outer": 263,
    "left_mouth": 61,
    "right_mouth": 291,
}


def euclidean(p1, p2):
    return math.dist(p1, p2)


def eye_aspect_ratio(eye_points):
    a = euclidean(eye_points[1], eye_points[5])
    b = euclidean(eye_points[2], eye_points[4])
    c = euclidean(eye_points[0], eye_points[3])

    if c == 0:
        return 0.0

    return (a + b) / (2.0 * c)


class FaceAnalyzer:
    def __init__(
        self,
        model_path,
        ear_closed_threshold=0.17,
        yaw_left_threshold=35.0,
        yaw_right_threshold=-35.0,
        pitch_up_threshold=-35.0,
        pitch_down_threshold=35.0,
        forward_yaw_deadzone=24.0,
        forward_pitch_deadzone=28.0,
        smoothing_alpha=0.12,
    ):
        self.ear_closed_threshold = ear_closed_threshold
        self.yaw_left_threshold = yaw_left_threshold
        self.yaw_right_threshold = yaw_right_threshold
        self.pitch_up_threshold = pitch_up_threshold
        self.pitch_down_threshold = pitch_down_threshold
        self.forward_yaw_deadzone = forward_yaw_deadzone
        self.forward_pitch_deadzone = forward_pitch_deadzone
        self.smoothing_alpha = smoothing_alpha

        self.smoothed_yaw = 0.0
        self.smoothed_pitch = 0.0

        # forward calibration offsets
        self.calibrated_yaw_offset = 0.0
        self.calibrated_pitch_offset = 0.0

        # keep raw values too, so calibration uses true current pose
        self.last_raw_yaw = 0.0
        self.last_raw_pitch = 0.0

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def calibrate_forward_from_raw(self):
        self.calibrated_yaw_offset = self.last_raw_yaw
        self.calibrated_pitch_offset = self.last_raw_pitch

        # reset smoothing around the new center
        self.smoothed_yaw = 0.0
        self.smoothed_pitch = 0.0

    def _smooth_value(self, old_value, new_value):
        alpha = self.smoothing_alpha
        return alpha * new_value + (1.0 - alpha) * old_value

    def _to_pixel(self, landmark, width, height):
        return (int(landmark.x * width), int(landmark.y * height))

    def _extract_eye_points(self, landmarks, indices, width, height):
        return [self._to_pixel(landmarks[i], width, height) for i in indices]

    def _estimate_head_pose(self, landmarks, width, height):
        image_points = np.array(
            [
                self._to_pixel(landmarks[POSE_LANDMARKS["nose_tip"]], width, height),
                self._to_pixel(landmarks[POSE_LANDMARKS["chin"]], width, height),
                self._to_pixel(landmarks[POSE_LANDMARKS["left_eye_outer"]], width, height),
                self._to_pixel(landmarks[POSE_LANDMARKS["right_eye_outer"]], width, height),
                self._to_pixel(landmarks[POSE_LANDMARKS["left_mouth"]], width, height),
                self._to_pixel(landmarks[POSE_LANDMARKS["right_mouth"]], width, height),
            ],
            dtype="double",
        )

        model_points = np.array(
            [
                (0.0, 0.0, 0.0),
                (0.0, -63.6, -12.5),
                (-43.3, 32.7, -26.0),
                (43.3, 32.7, -26.0),
                (-28.9, -28.9, -24.1),
                (28.9, -28.9, -24.1),
            ],
            dtype="double",
        )

        focal_length = width
        center = (width / 2, height / 2)
        camera_matrix = np.array(
            [
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1],
            ],
            dtype="double",
        )

        dist_coeffs = np.zeros((4, 1))

        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return 0.0, 0.0

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        pose_matrix = cv2.hconcat((rotation_matrix, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_matrix)

        pitch = float(euler_angles[0, 0])
        yaw = float(euler_angles[1, 0])

        return yaw, pitch

    def _get_head_direction(self, yaw, pitch):
        # large center zone first
        if abs(yaw) <= self.forward_yaw_deadzone and abs(pitch) <= self.forward_pitch_deadzone:
            return "FORWARD"

        # left/right first
        if yaw >= self.yaw_left_threshold:
            return "LEFT"
        if yaw <= self.yaw_right_threshold:
            return "RIGHT"

        # choose one mapping only
        # current mapping: positive pitch = DOWN, negative pitch = UP
        if pitch >= self.pitch_down_threshold:
            return "DOWN"
        if pitch <= self.pitch_up_threshold:
            return "UP"

        return "FORWARD"

    def analyze(self, frame):
        height, width = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks:
            return {
                "face_detected": False,
                "eyes_closed": False,
                "head_direction": "UNKNOWN",
                "left_ear": 0.0,
                "right_ear": 0.0,
                "avg_ear": 0.0,
                "yaw": 0.0,
                "pitch": 0.0,
                "raw_yaw": 0.0,
                "raw_pitch": 0.0,
                "landmarks": None,
            }

        landmarks = result.face_landmarks[0]

        left_eye = self._extract_eye_points(landmarks, LEFT_EYE_IDX, width, height)
        right_eye = self._extract_eye_points(landmarks, RIGHT_EYE_IDX, width, height)

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        eyes_closed = avg_ear < self.ear_closed_threshold

        raw_yaw, raw_pitch = self._estimate_head_pose(landmarks, width, height)
        self.last_raw_yaw = raw_yaw
        self.last_raw_pitch = raw_pitch

        yaw = raw_yaw - self.calibrated_yaw_offset
        pitch = raw_pitch - self.calibrated_pitch_offset

        self.smoothed_yaw = self._smooth_value(self.smoothed_yaw, yaw)
        self.smoothed_pitch = self._smooth_value(self.smoothed_pitch, pitch)

        head_direction = self._get_head_direction(self.smoothed_yaw, self.smoothed_pitch)

        return {
            "face_detected": True,
            "eyes_closed": eyes_closed,
            "head_direction": head_direction,
            "left_ear": left_ear,
            "right_ear": right_ear,
            "avg_ear": avg_ear,
            "yaw": self.smoothed_yaw,
            "pitch": self.smoothed_pitch,
            "raw_yaw": raw_yaw,
            "raw_pitch": raw_pitch,
            "landmarks": landmarks,
            "left_eye_points": left_eye,
            "right_eye_points": right_eye,
        }

    def close(self):
        if hasattr(self, "landmarker"):
            self.landmarker.close()