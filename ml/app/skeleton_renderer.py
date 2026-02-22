import cv2
import mediapipe as mp
from typing import Optional

from app.pose_estimator import Landmark

_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS
_DOT_COLOR = (0, 0, 255)       # red — landmark points
_LINE_COLOR = (0, 255, 0)      # green — skeleton lines
_DOT_RADIUS = 5
_LINE_THICKNESS = 2
_VISIBILITY_THRESHOLD = 0.5


class SkeletonRenderer:
    """Renders MediaPipe pose landmarks onto a video using OpenCV."""

    def render(
        self,
        video_path: str,
        landmarks_seq: list[Optional[list[Landmark]]],
        output_path: str,
    ) -> None:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (w, h),
        )

        try:
            for landmarks in landmarks_seq:
                ret, frame = cap.read()
                if not ret:
                    break
                if landmarks is not None:
                    self._draw(frame, landmarks, w, h)
                out.write(frame)
        finally:
            cap.release()
            out.release()

    def _draw(self, frame, landmarks: list[Landmark], w: int, h: int) -> None:
        for a, b in _CONNECTIONS:
            lm_a = landmarks[a]
            lm_b = landmarks[b]
            if lm_a.visibility > _VISIBILITY_THRESHOLD and lm_b.visibility > _VISIBILITY_THRESHOLD:
                pt_a = (int(lm_a.x * w), int(lm_a.y * h))
                pt_b = (int(lm_b.x * w), int(lm_b.y * h))
                cv2.line(frame, pt_a, pt_b, _LINE_COLOR, _LINE_THICKNESS)

        for lm in landmarks:
            if lm.visibility > _VISIBILITY_THRESHOLD:
                pt = (int(lm.x * w), int(lm.y * h))
                cv2.circle(frame, pt, _DOT_RADIUS, _DOT_COLOR, -1)
