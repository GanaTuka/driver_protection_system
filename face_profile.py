import numpy as np
from pathlib import Path


class FaceProfile:
    def __init__(self, match_threshold=0.85, profile_path="assets/driver_profile.npy"):
        self.match_threshold = match_threshold
        self.profile_path = Path(profile_path)
        self.encoding = None
        self._load()

    def _extract_encoding(self, landmarks):
        points = []

        for lm in landmarks:
            points.extend([lm.x, lm.y, lm.z])

        encoding = np.array(points, dtype=np.float32)

        nose = encoding[1 * 3 : 1 * 3 + 3]
        encoding -= nose

        left_eye = encoding[33 * 3 : 33 * 3 + 3]
        right_eye = encoding[263 * 3 : 263 * 3 + 3]
        eye_dist = np.linalg.norm(left_eye - right_eye)
        if eye_dist > 0:
            encoding /= eye_dist

        return encoding

    def save_profile(self, landmarks):
        self.encoding = self._extract_encoding(landmarks)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(str(self.profile_path), self.encoding)
        print(f"Driver profile saved to {self.profile_path}")

    def match(self, landmarks):
        if self.encoding is None:
            return 0.0

        encoding = self._extract_encoding(landmarks)
        denom = np.linalg.norm(self.encoding) * np.linalg.norm(encoding) + 1e-8
        similarity = float(np.dot(self.encoding, encoding) / denom)
        return similarity

    def is_driver(self, landmarks):
        if self.encoding is None:
            return True

        similarity = self.match(landmarks)
        return similarity >= self.match_threshold

    def has_profile(self):
        return self.encoding is not None

    def clear(self):
        self.encoding = None
        if self.profile_path.exists():
            self.profile_path.unlink()
        print("Driver profile cleared")

    def _load(self):
        if self.profile_path.exists():
            self.encoding = np.load(str(self.profile_path))
            print(f"Driver profile loaded from {self.profile_path}")
