import numpy as np
from dataclasses import dataclass
from typing import Optional
from app.pose_estimator import Landmark, LandmarkIndex


@dataclass
class FrameFeatures:
    """Joint angles (in degrees) extracted from a single frame."""
    # Knee angles: 180 = straight leg, ~90 = deep squat
    knee_angle_left: Optional[float]
    knee_angle_right: Optional[float]
    # Hip angles: angle at hip between torso and thigh
    hip_angle_left: Optional[float]
    hip_angle_right: Optional[float]
    # Elbow angles
    elbow_angle_left: Optional[float]
    elbow_angle_right: Optional[float]
    # Shoulder angles
    shoulder_angle_left: Optional[float]
    shoulder_angle_right: Optional[float]
    # Back angle: angle of spine (shoulder→hip) relative to vertical axis
    back_angle: Optional[float]


VISIBILITY_THRESHOLD = 0.5  # ignore landmarks below this confidence


def _angle(a: Landmark, b: Landmark, c: Landmark) -> Optional[float]:
    """
    Calculates the angle at point B formed by segments BA and BC.
    Returns degrees, or None if any landmark has low visibility.
    """
    if min(a.visibility, b.visibility, c.visibility) < VISIBILITY_THRESHOLD:
        return None

    ba = np.array([a.x - b.x, a.y - b.y])
    bc = np.array([c.x - b.x, c.y - b.y])

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba == 0 or norm_bc == 0:
        return None

    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine = np.clip(cosine, -1.0, 1.0)  # guard against floating point errors
    return float(np.degrees(np.arccos(cosine)))


def _back_angle(shoulder: Landmark, hip: Landmark) -> Optional[float]:
    """
    Angle of the spine segment (shoulder→hip) relative to the vertical axis.
    0° = perfectly upright, 90° = horizontal (parallel to floor).
    """
    if min(shoulder.visibility, hip.visibility) < VISIBILITY_THRESHOLD:
        return None

    dx = hip.x - shoulder.x
    dy = hip.y - shoulder.y  # positive y = downward in image coords

    vertical = np.array([0.0, 1.0])
    spine = np.array([dx, dy])

    norm = np.linalg.norm(spine)
    if norm == 0:
        return None

    cosine = np.dot(spine, vertical) / norm
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


class FeatureExtractor:
    """Converts per-frame landmarks into joint angle features."""

    def extract(self, landmarks: list[Landmark]) -> FrameFeatures:
        """Extracts all features from a single frame's landmarks."""
        L = LandmarkIndex

        # Convenience aliases
        lsh = landmarks[L.LEFT_SHOULDER]
        rsh = landmarks[L.RIGHT_SHOULDER]
        lel = landmarks[L.LEFT_ELBOW]
        rel = landmarks[L.RIGHT_ELBOW]
        lwr = landmarks[L.LEFT_WRIST]
        rwr = landmarks[L.RIGHT_WRIST]
        lhi = landmarks[L.LEFT_HIP]
        rhi = landmarks[L.RIGHT_HIP]
        lkn = landmarks[L.LEFT_KNEE]
        rkn = landmarks[L.RIGHT_KNEE]
        lan = landmarks[L.LEFT_ANKLE]
        ran = landmarks[L.RIGHT_ANKLE]

        # Average left/right shoulder and hip for a center-spine back angle
        mid_shoulder = Landmark(
            x=(lsh.x + rsh.x) / 2, y=(lsh.y + rsh.y) / 2,
            z=0, visibility=min(lsh.visibility, rsh.visibility),
        )
        mid_hip = Landmark(
            x=(lhi.x + rhi.x) / 2, y=(lhi.y + rhi.y) / 2,
            z=0, visibility=min(lhi.visibility, rhi.visibility),
        )

        return FrameFeatures(
            knee_angle_left=_angle(lhi, lkn, lan),
            knee_angle_right=_angle(rhi, rkn, ran),
            hip_angle_left=_angle(lsh, lhi, lkn),
            hip_angle_right=_angle(rsh, rhi, rkn),
            elbow_angle_left=_angle(lsh, lel, lwr),
            elbow_angle_right=_angle(rsh, rel, rwr),
            shoulder_angle_left=_angle(lhi, lsh, lel),
            shoulder_angle_right=_angle(rhi, rsh, rel),
            back_angle=_back_angle(mid_shoulder, mid_hip),
        )

    def extract_sequence(
        self, frames_landmarks: list[Optional[list[Landmark]]]
    ) -> list[Optional[FrameFeatures]]:
        """Extracts features for every frame. Returns None for frames with no pose."""
        return [
            self.extract(frame) if frame is not None else None
            for frame in frames_landmarks
        ]
