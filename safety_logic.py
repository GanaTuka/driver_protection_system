# safety_logic.py

import time


class SafetyLogic:
    def __init__(
        self,
        eye_closed_stop_seconds=5.0,
        look_left_stop_seconds=3.0,
        look_right_stop_seconds=3.0,
        look_up_stop_seconds=3.0,
        look_down_stop_seconds=3.0,
        no_face_stop_seconds=3.0,
        stop_latched=True,
    ):
        self.eye_closed_stop_seconds = eye_closed_stop_seconds
        self.look_left_stop_seconds = look_left_stop_seconds
        self.look_right_stop_seconds = look_right_stop_seconds
        self.look_up_stop_seconds = look_up_stop_seconds
        self.look_down_stop_seconds = look_down_stop_seconds
        self.no_face_stop_seconds = no_face_stop_seconds
        self.stop_latched = stop_latched

        self.state = "NORMAL"
        self.stop_reason = None
        self.stopped_at = None

        self.eyes_closed_since = None
        self.look_left_since = None
        self.look_right_since = None
        self.look_up_since = None
        self.look_down_since = None
        self.no_face_since = None

    def _start_or_keep_timer(self, current_value):
        return current_value if current_value is not None else time.time()

    def _reset_other_direction_timers(self, direction):
        if direction != "LEFT":
            self.look_left_since = None
        if direction != "RIGHT":
            self.look_right_since = None
        if direction != "UP":
            self.look_up_since = None
        if direction != "DOWN":
            self.look_down_since = None
        if direction == "FORWARD":
            self.look_left_since = None
            self.look_right_since = None
            self.look_up_since = None
            self.look_down_since = None

    def trigger_stop(self, reason: str):
        if self.state != "STOP":
            self.state = "STOP"
            self.stop_reason = reason
            self.stopped_at = time.time()

    def update(self, analysis):
        if self.state == "STOP" and self.stop_latched:
            return

        now = time.time()

        face_detected = analysis["face_detected"]
        eyes_closed = analysis["eyes_closed"]
        head_direction = analysis["head_direction"]

        if not face_detected:
            self.no_face_since = self._start_or_keep_timer(self.no_face_since)
            self.eyes_closed_since = None
            self.look_left_since = None
            self.look_right_since = None
            self.look_up_since = None
            self.look_down_since = None

            if now - self.no_face_since >= self.no_face_stop_seconds:
                self.trigger_stop("No face detected too long")
            return
        else:
            self.no_face_since = None

        if eyes_closed:
            self.eyes_closed_since = self._start_or_keep_timer(self.eyes_closed_since)
            if now - self.eyes_closed_since >= self.eye_closed_stop_seconds:
                self.trigger_stop("Eyes closed too long")
                return
        else:
            self.eyes_closed_since = None

        self._reset_other_direction_timers(head_direction)

        if head_direction == "LEFT":
            self.look_left_since = self._start_or_keep_timer(self.look_left_since)
            if now - self.look_left_since >= self.look_left_stop_seconds:
                self.trigger_stop("Looking left too long")
                return

        elif head_direction == "RIGHT":
            self.look_right_since = self._start_or_keep_timer(self.look_right_since)
            if now - self.look_right_since >= self.look_right_stop_seconds:
                self.trigger_stop("Looking right too long")
                return

        elif head_direction == "UP":
            self.look_up_since = self._start_or_keep_timer(self.look_up_since)
            if now - self.look_up_since >= self.look_up_stop_seconds:
                self.trigger_stop("Looking up too long")
                return

        elif head_direction == "DOWN":
            self.look_down_since = self._start_or_keep_timer(self.look_down_since)
            if now - self.look_down_since >= self.look_down_stop_seconds:
                self.trigger_stop("Looking down too long")
                return

        if self.state == "STOP" and not self.stop_latched:
            self.reset()

    def get_timers(self):
        now = time.time()

        def elapsed(since):
            return 0.0 if since is None else now - since

        return {
            "eyes_closed": elapsed(self.eyes_closed_since),
            "look_left": elapsed(self.look_left_since),
            "look_right": elapsed(self.look_right_since),
            "look_up": elapsed(self.look_up_since),
            "look_down": elapsed(self.look_down_since),
            "no_face": elapsed(self.no_face_since),
        }

    def reset(self):
        self.state = "NORMAL"
        self.stop_reason = None
        self.stopped_at = None

        self.eyes_closed_since = None
        self.look_left_since = None
        self.look_right_since = None
        self.look_up_since = None
        self.look_down_since = None
        self.no_face_since = None

    def is_stopped(self):
        return self.state == "STOP"