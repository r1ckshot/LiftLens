import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Knee angle thresholds (angle at joint B = hip-knee-ankle; lower = deeper squat)
DEPTH_GOOD = 90.0
DEPTH_WARN = 110.0

# Back angle thresholds (spine vs vertical; lower = more upright)
BACK_GOOD = 35.0
BACK_WARN = 50.0


def _min_knee_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Returns the minimum average knee angle across all frames (deepest point)."""
    angles = []
    for f in frames:
        left = f.knee_angle_left
        right = f.knee_angle_right
        if left is not None and right is not None:
            angles.append((left + right) / 2)
        elif left is not None:
            angles.append(left)
        elif right is not None:
            angles.append(right)
    return min(angles) if angles else None


def _median_back_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Returns the median back angle across all frames."""
    angles = [f.back_angle for f in frames if f.back_angle is not None]
    return statistics.median(angles) if angles else None


def _depth_feedback(min_knee: Optional[float]) -> FeedbackItem:
    if min_knee is None:
        return FeedbackItem("depth", "error", "Could not measure squat depth — knees not visible.")
    if min_knee <= DEPTH_GOOD:
        return FeedbackItem("depth", "ok", "Good squat depth.")
    if min_knee <= DEPTH_WARN:
        return FeedbackItem(
            "depth", "warning",
            f"Partial depth ({min_knee:.0f}°). Aim for thighs parallel to the floor (≤90°).",
        )
    return FeedbackItem(
        "depth", "error",
        f"Insufficient depth ({min_knee:.0f}°). Squat much lower.",
    )


def _back_feedback(median_back: Optional[float]) -> FeedbackItem:
    if median_back is None:
        return FeedbackItem("back_position", "error", "Could not measure back angle — shoulders/hips not visible.")
    if median_back <= BACK_GOOD:
        return FeedbackItem("back_position", "ok", "Good back position.")
    if median_back <= BACK_WARN:
        return FeedbackItem(
            "back_position", "warning",
            f"Slight forward lean ({median_back:.0f}°). Keep your chest up.",
        )
    return FeedbackItem(
        "back_position", "error",
        f"Excessive forward lean ({median_back:.0f}°). Engage your core and keep torso upright.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class SquatClassifier(BaseClassifier):
    """Rule-based squat technique classifier."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        min_knee = _min_knee_angle(frames)
        median_back = _median_back_angle(frames)

        feedback = [
            _depth_feedback(min_knee),
            _back_feedback(median_back),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
