import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Shoulder abduction angle at the peak of the raise (front view: hip→shoulder→elbow).
# At proper height (arms parallel to floor): shoulder_angle ≈ 80-100°.
# Research: arms should reach approximately shoulder height (90° abduction).
HEIGHT_GOOD = 80.0  # at or above shoulder height
HEIGHT_WARN = 60.0  # visibly below shoulder height

# Body swing: how much the torso leans back/forward during the raise (3D back lean).
# 0° = perfectly upright. People lean back to use momentum when the weight is too heavy.
# Research: <15° is acceptable natural stabilisation; >22° indicates momentum use.
SWING_GOOD = 15.0
SWING_WARN = 22.0

# Elbow angle during the raise.
# Should be softly bent (≈ 150-170°). Overly bent = curling; too straight = strain risk.
ELBOW_BENT_WARN = 135.0  # too much bend → turning into a lateral curl

# Raise-phase detection: frames where at least one arm is raised.
_RAISE_SHOULDER_MIN = 40.0
# Minimum fraction of frames that must be in raise phase for reliable elbow detection.
_MIN_RAISE_FRACTION = 0.05


def _avg_shoulder(f: FrameFeatures) -> Optional[float]:
    if f.shoulder_angle_left is not None and f.shoulder_angle_right is not None:
        return (f.shoulder_angle_left + f.shoulder_angle_right) / 2
    return f.shoulder_angle_left if f.shoulder_angle_left is not None else f.shoulder_angle_right


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _raise_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Returns raise-phase frames, or empty list if raise phase is not reliably detected.

    An empty result means the camera angle is likely not frontal — the lateral arm
    movement is invisible in the 2D projection so shoulder_angle stays low.
    """
    raised = [f for f in frames if (s := _avg_shoulder(f)) is not None and s > _RAISE_SHOULDER_MIN]
    min_frames = max(10, len(frames) * _MIN_RAISE_FRACTION)
    return raised if len(raised) >= min_frames else []


def _peak_shoulder_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Maximum average shoulder angle — the top of the raise."""
    vals = [s for f in frames if (s := _avg_shoulder(f)) is not None]
    return max(vals) if vals else None


def _body_swing(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back lean during the raise phase — detects momentum use.
    Falls back to all frames if raise phase is not reliably detected."""
    raise_frames = _raise_phase_frames(frames)
    source = raise_frames if raise_frames else frames
    vals = [f.back_lean_3d for f in source if f.back_lean_3d is not None]
    return statistics.median(vals) if vals else None


def _raise_elbow(frames: list[FrameFeatures]) -> Optional[float]:
    """Median elbow angle during the raise phase.
    Returns None if raise phase is not detected or measurements are implausible.

    Elbow angles < 90° during a lateral raise are physically impossible and
    indicate a camera angle artifact (arm moving perpendicular to camera in 2D).
    """
    raise_frames = _raise_phase_frames(frames)
    if not raise_frames:
        return None
    vals = [e for f in raise_frames if (e := _avg_elbow(f)) is not None]
    if not vals:
        return None
    med = statistics.median(vals)
    return med if med >= 90 else None  # < 90° = 2D projection artifact


def _height_feedback(peak: Optional[float]) -> FeedbackItem:
    if peak is None:
        return FeedbackItem("arm_height", "error", "Could not measure arm height — shoulders/elbows not visible.")
    if peak >= HEIGHT_GOOD:
        return FeedbackItem("arm_height", "ok", "Good raise height — arms reaching shoulder level.")
    if peak >= HEIGHT_WARN:
        return FeedbackItem(
            "arm_height", "warning",
            f"Partial range ({peak:.0f}°). Raise your arms until they are parallel to the floor.",
        )
    return FeedbackItem(
        "arm_height", "error",
        f"Arms too low ({peak:.0f}°). Raise to shoulder height — imagine pouring water from a jug at your sides.",
    )


def _swing_feedback(swing: Optional[float]) -> FeedbackItem:
    if swing is None:
        return FeedbackItem(
            "body_swing", "error",
            "Could not measure body swing — hips/shoulders not visible or no 3D data.",
        )
    if swing <= SWING_GOOD:
        return FeedbackItem("body_swing", "ok", "Good torso stability — minimal body swing.")
    if swing <= SWING_WARN:
        return FeedbackItem(
            "body_swing", "warning",
            f"Slight body lean ({swing:.0f}°). Brace your core and avoid using momentum to raise the weight.",
        )
    return FeedbackItem(
        "body_swing", "error",
        f"Excessive body swing ({swing:.0f}°). Lower the weight and raise with strict form — torso stays vertical.",
    )


def _elbow_feedback(elbow: Optional[float]) -> FeedbackItem:
    if elbow is None:
        return FeedbackItem(
            "elbow_position", "warning",
            "Could not assess elbow angle from this camera angle. "
            "Position the camera directly in front of you for accurate elbow tracking.",
        )
    if elbow >= ELBOW_BENT_WARN:
        return FeedbackItem("elbow_position", "ok", "Good elbow position — slight bend maintained.")
    return FeedbackItem(
        "elbow_position", "warning",
        f"Elbows too bent ({elbow:.0f}°). Keep a soft bend in the elbow — avoid turning the movement into a curl.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class LateralRaiseClassifier(BaseClassifier):
    """Rule-based lateral raise technique classifier using 2D angles + 3D body swing."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        peak = _peak_shoulder_angle(frames)
        swing = _body_swing(frames)
        elbow = _raise_elbow(frames)

        feedback = [
            _height_feedback(peak),
            _swing_feedback(swing),
            _elbow_feedback(elbow),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
