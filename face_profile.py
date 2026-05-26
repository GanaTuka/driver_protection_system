import numpy as np
from pathlib import Path


ANCHOR_INDICES = (1, 2, 33, 61, 152, 168, 263, 291)


def _align_landmarks(source, target_anchors):
    src_anchors = source[list(ANCHOR_INDICES)]
    src_centroid = src_anchors.mean(axis=0)
    tgt_centroid = target_anchors.mean(axis=0)
    src_centered = src_anchors - src_centroid
    tgt_centered = target_anchors - tgt_centroid
    H = src_centered.T @ tgt_centered
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    aligned = (source - src_centroid) @ R.T + tgt_centroid
    return aligned


class FaceProfile:
    def __init__(self, match_threshold=0.75, profile_path="assets/driver_profile.npy"):
        self.match_threshold = match_threshold
        self.profile_path = Path(profile_path)
        self.encoding = None
        self.profile_anchor_points = None
        self._load()

    def _extract_encoding(self, landmarks):
        points = []

        for lm in landmarks:
            points.extend([lm.x, lm.y, lm.z])

        all_landmarks = np.array(points, dtype=np.float32).reshape(-1, 3)

        if self.profile_anchor_points is not None:
            all_landmarks = _align_landmarks(all_landmarks, self.profile_anchor_points)
        else:
            nose = all_landmarks[1].copy()
            all_landmarks -= nose

        left_eye = all_landmarks[33]
        right_eye = all_landmarks[263]
        eye_dist = np.linalg.norm(left_eye - right_eye)
        if eye_dist > 0:
            all_landmarks /= eye_dist

        return all_landmarks.flatten()

    def save_profile(self, landmarks):
        points = []
        for lm in landmarks:
            points.extend([lm.x, lm.y, lm.z])
        all_landmarks = np.array(points, dtype=np.float32).reshape(-1, 3)
        self.profile_anchor_points = all_landmarks[list(ANCHOR_INDICES)].copy()
        self.encoding = self._extract_encoding(landmarks)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(str(self.profile_path), self.encoding)
        self.save_anchor()
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
        self.profile_anchor_points = None
        if self.profile_path.exists():
            self.profile_path.unlink()
        anchor_path = self.profile_path.parent / "driver_profile_anchor.npy"
        if anchor_path.exists():
            anchor_path.unlink()
        print("Driver profile cleared")

    def _load(self):
        if self.profile_path.exists():
            self.encoding = np.load(str(self.profile_path))
            print(f"Driver profile loaded from {self.profile_path}")
            anchor_path = self.profile_path.parent / "driver_profile_anchor.npy"
            if anchor_path.exists():
                loaded = np.load(str(anchor_path))
                if loaded.shape == (len(ANCHOR_INDICES), 3):
                    self.profile_anchor_points = loaded
                else:
                    print(f"Old anchor format ignored; press C to re-save profile")

    def save_anchor(self):
        if self.profile_anchor_points is not None:
            anchor_path = self.profile_path.parent / "driver_profile_anchor.npy"
            np.save(str(anchor_path), self.profile_anchor_points)
            print(f"Anchor saved to {anchor_path}")
