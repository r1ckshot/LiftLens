import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Knee angle thresholds (angle at joint B = hip-knee-ankle; lower = deeper squat)
DEPTH_GOOD = 90.0
DEPTH_WARN = 110.0

# Back angle thresholds (spine vs vertical; lower = more upright).
# Research: low-bar squat at parallel = ~40° lean, high-bar = ~25-45°.
# 50° accommodates both styles; >65° is excessive for any squat technique.
BACK_GOOD = 50.0
BACK_WARN = 65.0

# Bottom-phase detection bounds.
# Frames with knee angle < 45° are MediaPipe artifacts (physically impossible).
# Frames with knee angle > 100° are standing or early-descent, not the bottom.
_BOTTOM_KNEE_MIN = 45.0
_BOTTOM_KNEE_MAX = 100.0


def _avg_knee(f: FrameFeatures) -> Optional[float]:
    if f.knee_angle_left is not None and f.knee_angle_right is not None:
        return (f.knee_angle_left + f.knee_angle_right) / 2
    return f.knee_angle_left if f.knee_angle_left is not None else f.knee_angle_right


def _min_knee_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Returns the minimum average knee angle, excluding artifact frames (< 45°)."""
    angles = [k for f in frames if (k := _avg_knee(f)) is not None and k >= _BOTTOM_KNEE_MIN]
    return min(angles) if angles else None


def _bottom_phase_back_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """
    Returns the median back angle during the bottom phase of the squat.

    Bottom phase is defined as frames where the average knee angle is in
    [45°, 100°]. The lower bound excludes MediaPipe artifact frames that
    appear at extreme squat positions (physically impossible angles < 45°).
    The upper bound excludes standing and early-descent frames (> 100°).

    Falls back to the 90th-percentile across all frames if no bottom frames exist
    (e.g. person only squatted to 110°, or knees not visible throughout).
    """
    knee_vals = [_avg_knee(f) for f in frames]
    bottom_back = [
        f.back_angle
        for f, k in zip(frames, knee_vals)
        if k is not None and _BOTTOM_KNEE_MIN <= k <= _BOTTOM_KNEE_MAX
        and f.back_angle is not None
    ]

    if bottom_back:
        return statistics.median(bottom_back)

    # Fallback: squat didn't reach 100° or knees always off-screen
    all_back = sorted(f.back_angle for f in frames if f.back_angle is not None)
    if not all_back:
        return None
    return all_back[int(len(all_back) * 0.90)]


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


def _back_feedback(bottom_back: Optional[float]) -> FeedbackItem:
    if bottom_back is None:
        return FeedbackItem("back_position", "error", "Could not measure back angle — shoulders/hips not visible.")
    if bottom_back <= BACK_GOOD:
        return FeedbackItem("back_position", "ok", "Good back position.")
    if bottom_back <= BACK_WARN:
        return FeedbackItem(
            "back_position", "warning",
            f"Slight forward lean ({bottom_back:.0f}°). Keep your chest up.",
        )
    return FeedbackItem(
        "back_position", "error",
        f"Excessive forward lean ({bottom_back:.0f}°). Engage your core and keep torso upright.",
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
        bottom_back = _bottom_phase_back_angle(frames)

        feedback = [
            _depth_feedback(min_knee),
            _back_feedback(bottom_back),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
