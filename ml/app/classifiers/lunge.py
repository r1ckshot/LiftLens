import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Front knee angle at the bottom position (hip-knee-ankle; lower = deeper lunge).
# Research: peak knee flexion ≈ 90° in a standard forward lunge (PMC4641539).
DEPTH_GOOD = 90.0
DEPTH_WARN = 110.0

# Back angle thresholds (spine vs vertical; lower = more upright).
# Upright torso is optimal for lunges; same reference range as squat.
BACK_GOOD = 50.0
BACK_WARN = 65.0

# Bottom-phase detection: the deeper of the two knee angles should be in this range.
# < 45° = MediaPipe artifact; > 100° = standing / early descent.
_BOTTOM_KNEE_MIN = 45.0
_BOTTOM_KNEE_MAX = 100.0

# Both knees must be below this angle to be considered a lunge frame.
# Filters out walking steps where only one knee is flexed (~70°) while the other
# is nearly straight (~170°) — which would otherwise falsely register as good depth.
_BOTH_BENT_THRESHOLD = 160.0


def _deeper_knee(f: FrameFeatures) -> Optional[float]:
    """
    Returns the smaller (deeper) knee angle, but only when BOTH knees are
    simultaneously bent (< 160°). Excludes walking frames where only one knee
    is flexed and the other is near-straight.
    """
    la, ra = f.knee_angle_left, f.knee_angle_right
    if la is None or ra is None:
        return None
    if la >= _BOTH_BENT_THRESHOLD or ra >= _BOTH_BENT_THRESHOLD:
        return None
    return min(la, ra)


def _min_depth_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum front-knee angle across the video, excluding artifact frames (< 45°)."""
    angles = [k for f in frames if (k := _deeper_knee(f)) is not None and k >= _BOTTOM_KNEE_MIN]
    return min(angles) if angles else None


def _bottom_phase_back_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """
    Median back angle during the bottom phase of the lunge.

    Bottom phase is defined as frames where the deeper knee angle is in
    [45°, 100°]. Falls back to the 90th-percentile if no bottom frames exist.
    """
    knee_vals = [_deeper_knee(f) for f in frames]
    bottom_back = [
        f.back_angle
        for f, k in zip(frames, knee_vals)
        if k is not None and _BOTTOM_KNEE_MIN <= k <= _BOTTOM_KNEE_MAX
        and f.back_angle is not None
    ]

    if bottom_back:
        return statistics.median(bottom_back)

    all_back = sorted(f.back_angle for f in frames if f.back_angle is not None)
    if not all_back:
        return None
    return all_back[int(len(all_back) * 0.90)]


def _depth_feedback(min_knee: Optional[float]) -> FeedbackItem:
    if min_knee is None:
        return FeedbackItem("depth", "error", "Could not measure lunge depth — knees not visible.")
    if min_knee <= DEPTH_GOOD:
        return FeedbackItem("depth", "ok", "Good lunge depth.")
    if min_knee <= DEPTH_WARN:
        return FeedbackItem(
            "depth", "warning",
            f"Partial depth ({min_knee:.0f}°). Lower your back knee closer to the floor.",
        )
    return FeedbackItem(
        "depth", "error",
        f"Insufficient depth ({min_knee:.0f}°). Step further forward and lower your hips.",
    )


def _back_feedback(bottom_back: Optional[float]) -> FeedbackItem:
    if bottom_back is None:
        return FeedbackItem("back_position", "error", "Could not measure back angle — shoulders/hips not visible.")
    if bottom_back <= BACK_GOOD:
        return FeedbackItem("back_position", "ok", "Good torso position.")
    if bottom_back <= BACK_WARN:
        return FeedbackItem(
            "back_position", "warning",
            f"Slight forward lean ({bottom_back:.0f}°). Keep your torso upright.",
        )
    return FeedbackItem(
        "back_position", "error",
        f"Excessive forward lean ({bottom_back:.0f}°). Keep your chest up and core engaged.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class LungeClassifier(BaseClassifier):
    """Rule-based lunge technique classifier."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        min_knee = _min_depth_angle(frames)
        bottom_back = _bottom_phase_back_angle(frames)

        feedback = [
            _depth_feedback(min_knee),
            _back_feedback(bottom_back),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
