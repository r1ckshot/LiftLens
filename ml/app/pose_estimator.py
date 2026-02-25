import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional


@dataclass
class Landmark:
    x: float
    y: float
    z: float
    visibility: float
    wx: float = 0.0  # world x, metres, person's right = positive
    wy: float = 0.0  # world y, metres, up = positive
    wz: float = 0.0  # world z, metres, toward camera = positive


class LandmarkIndex:
    """MediaPipe Pose landmark indices we care about."""
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


class PoseEstimator:
    """Processes a video file and returns MediaPipe Pose landmarks per frame."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1,
    ):
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process_video(self, video_path: str) -> list[Optional[list[Landmark]]]:
        """
        Returns a list of landmarks per frame.
        Each element is a list of 33 Landmark objects, or None if pose not detected.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        results = []
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # MediaPipe expects RGB, OpenCV gives BGR
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pose_result = self._pose.process(frame_rgb)

                if pose_result.pose_landmarks:
                    world_lms = pose_result.pose_world_landmarks.landmark
                    results.append([
                        Landmark(lm.x, lm.y, lm.z, lm.visibility,
                                 wx=wlm.x, wy=wlm.y, wz=wlm.z)
                        for lm, wlm in zip(pose_result.pose_landmarks.landmark, world_lms)
                    ])
                else:
                    results.append(None)
        finally:
            cap.release()

        return results

    def get_video_info(self, video_path: str) -> dict:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration_sec": frame_count / fps if fps > 0 else 0,
        }

    def close(self):
        self._pose.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
