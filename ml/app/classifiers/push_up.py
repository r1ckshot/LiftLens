import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Body alignment thresholds: deviation from straight = |180° - hip_angle|.
# 0° = perfect straight line heels-to-head (research: "straight line" standard).
ALIGNMENT_GOOD = 15.0
ALIGNMENT_WARN = 30.0

# Depth thresholds: minimum average elbow angle across all frames.
# Research: ~90° at full depth; 100° allows reasonable tolerance.
DEPTH_GOOD = 100.0
DEPTH_WARN = 115.0

# Push phase detection: frames where avg elbow_angle < 150° (arms actively bent).
_PUSH_ELBOW_MAX = 150.0


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _avg_hip(f: FrameFeatures) -> Optional[float]:
    if f.hip_angle_left is not None and f.hip_angle_right is not None:
        return (f.hip_angle_left + f.hip_angle_right) / 2
    return f.hip_angle_left if f.hip_angle_left is not None else f.hip_angle_right


def _push_phase_alignment(frames: list[FrameFeatures]) -> Optional[float]:
    """
    Median body alignment deviation during the push phase (elbow < 150°).
    Deviation = |180° - hip_angle|; 0° means shoulders, hips, and ankles are in a straight line.
    Falls back to all frames if no push-phase frames are detected.
    """
    deviations = []
    for f in frames:
        e = _avg_elbow(f)
        h = _avg_hip(f)
        if e is not None and e < _PUSH_ELBOW_MAX and h is not None:
            deviations.append(abs(180.0 - h))
    if deviations:
        return statistics.median(deviations)
    all_dev = [abs(180.0 - h) for f in frames if (h := _avg_hip(f)) is not None]
    return statistics.median(all_dev) if all_dev else None


def _min_elbow_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum average elbow angle — captures the deepest point of each rep."""
    angles = []
    for f in frames:
        e = _avg_elbow(f)
        if e is not None:
            angles.append(e)
    return min(angles) if angles else None


def _alignment_feedback(deviation: Optional[float]) -> FeedbackItem:
    if deviation is None:
        return FeedbackItem(
            "body_alignment", "error",
            "Could not measure body alignment — hips not visible.",
        )
    if deviation <= ALIGNMENT_GOOD:
        return FeedbackItem("body_alignment", "ok", "Good body alignment — straight from head to heels.")
    if deviation <= ALIGNMENT_WARN:
        return FeedbackItem(
            "body_alignment", "warning",
            f"Body not fully straight ({deviation:.0f}° deviation). Engage your core and glutes to maintain a rigid plank position.",
        )
    return FeedbackItem(
        "body_alignment", "error",
        f"Significant hip sag or pike ({deviation:.0f}° deviation). Keep your body in a straight line throughout the movement.",
    )


def _depth_feedback(min_elbow: Optional[float]) -> FeedbackItem:
    if min_elbow is None:
        return FeedbackItem(
            "depth", "error",
            "Could not measure push-up depth — elbows not visible.",
        )
    if min_elbow <= DEPTH_GOOD:
        return FeedbackItem("depth", "ok", "Good depth — chest close to the floor.")
    if min_elbow <= DEPTH_WARN:
        return FeedbackItem(
            "depth", "warning",
            f"Partial depth ({min_elbow:.0f}°). Lower your chest closer to the floor.",
        )
    return FeedbackItem(
        "depth", "error",
        f"Insufficient depth ({min_elbow:.0f}°). Bend your elbows much more — chest should nearly touch the floor.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class PushUpClassifier(BaseClassifier):
    """Rule-based push-up technique classifier."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        alignment = _push_phase_alignment(frames)
        min_elbow = _min_elbow_angle(frames)

        feedback = [
            _alignment_feedback(alignment),
            _depth_feedback(min_elbow),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
