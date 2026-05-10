# simulator.py

import cv2
import time
import pygame


class RoadSimulator:
    def __init__(self, video_path: str, warning_sound_path: str, warning_duration: float = 1.0):
        self.video_path = video_path
        self.warning_sound_path = warning_sound_path
        self.warning_duration = warning_duration

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open road video: {self.video_path}")

        self.last_frame = None
        self.stopped = False
        self.warning_played_at = None

        pygame.mixer.init()
        self.warning_sound = pygame.mixer.Sound(self.warning_sound_path)

    def read_frame(self):
        if self.stopped and self.last_frame is not None:
            return self.last_frame.copy()

        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if not ret:
            raise RuntimeError("Could not read from road video.")

        self.last_frame = frame.copy()
        return frame

    def stop(self):
        if not self.stopped:
            self.stopped = True
            self.warning_played_at = time.time()
            self.warning_sound.play()

    def reset(self):
        self.stopped = False
        self.warning_played_at = None

    def is_warning_active(self):
        if self.warning_played_at is None:
            return False
        return (time.time() - self.warning_played_at) < self.warning_duration

    def release(self):
        self.cap.release()
        pygame.mixer.quit()