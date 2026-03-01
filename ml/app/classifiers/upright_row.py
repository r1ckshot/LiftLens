import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Peak height thresholds (max shoulder_angle during pull; 0° = arm at side, 90° = elbow at shoulder).
# BarBend / PureGym / Peloton: pull until elbows are at shoulder level (parallel to floor).
# Do NOT raise elbows above shoulders — increases shoulder impingement risk.
PEAK_GOOD_MIN = 70.0   # elbows near shoulder level — good pull height
PEAK_GOOD_MAX = 120.0  # upper bound — above this risks shoulder impingement
PEAK_WARN_MIN = 40.0   # below this = error (barely pulling at all)

# Elbow bend thresholds (min elbow_angle during pull; 180° = straight, 90° = right angle).
# At the peak of a proper upright row, forearms hang down from the elbows → ~90° elbow angle.
ELBOW_GOOD = 100.0   # arms well bent — bar pulled to chin/chest level
ELBOW_WARN = 130.0   # insufficient bend — bar not travelling high enough

# Body swing thresholds (max back_lean_3d during pull phase).
# Research: "do not lean back — use a controlled pull, not momentum".
SWING_GOOD = 15.0    # ≤ 15° = controlled
SWING_WARN = 25.0    # > 25° = clearly using momentum

# Pull phase: frames where the arms are clearly raised above the resting position.
_PULL_ANGLE_MIN = 25.0
_MIN_PULL_FRACTION = 0.05


def _avg_shoulder(f: FrameFeatures) -> Optional[float]:
    if f.shoulder_angle_left is not None and f.shoulder_angle_right is not None:
        return (f.shoulder_angle_left + f.shoulder_angle_right) / 2
    return f.shoulder_angle_left if f.shoulder_angle_left is not None else f.shoulder_angle_right


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _pull_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames where the arms are actively pulled above the resting position."""
    pulled = [f for f in frames if (a := _avg_shoulder(f)) is not None and a > _PULL_ANGLE_MIN]
    min_frames = max(5, len(frames) * _MIN_PULL_FRACTION)
    return pulled if len(pulled) >= min_frames else []


def _peak_height(frames: list[FrameFeatures]) -> Optional[float]:
    """85th-percentile shoulder angle during the pull — how high the elbows typically rise."""
    pull = _pull_phase_frames(frames)
    source = pull if pull else frames
    vals = sorted(a for f in source if (a := _avg_shoulder(f)) is not None)
    if not vals:
        return None
    return vals[int(len(vals) * 0.85)]


def _elbow_bend(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum elbow angle during the pull — how bent the arms are at peak."""
    pull = _pull_phase_frames(frames)
    if not pull:
        return None
    vals = [e for f in pull if (e := _avg_elbow(f)) is not None and e >= 30.0]
    return min(vals) if vals else None


def _body_swing(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back lean during the pull phase — detects torso momentum.
    Uses median because max() is dominated by 3D landmark noise from front-view cameras."""
    pull = _pull_phase_frames(frames)
    source = pull if pull else frames
    vals = [f.back_lean_3d for f in source if f.back_lean_3d is not None]
    return statistics.median(vals) if vals else None


def _height_feedback(peak: Optional[float]) -> FeedbackItem:
    if peak is None:
        return FeedbackItem("pull_height", "error", "Could not detect pull height — shoulders not visible.")
    if peak > PEAK_GOOD_MAX:
        return FeedbackItem(
            "pull_height", "warning",
            f"Elbows raised too high ({peak:.0f}°). Stop when elbows are level with your shoulders — "
            "pulling higher puts the shoulder joint into impingement.",
        )
    if peak >= PEAK_GOOD_MIN:
        return FeedbackItem("pull_height", "ok", "Good pull height — elbows reaching shoulder level.")
    if peak >= PEAK_WARN_MIN:
        return FeedbackItem(
            "pull_height", "warning",
            f"Bar not coming up high enough ({peak:.0f}°). Pull until your elbows are level with your shoulders.",
        )
    return FeedbackItem(
        "pull_height", "error",
        f"Very low pull ({peak:.0f}°). Drive your elbows upward until they reach shoulder height.",
    )


def _elbow_feedback(elbow: Optional[float]) -> FeedbackItem:
    if elbow is None:
        return FeedbackItem("elbow_bend", "warning", "Could not assess elbow bend — arms not visible from this angle.")
    if elbow <= ELBOW_GOOD:
        return FeedbackItem("elbow_bend", "ok", "Good elbow bend — arms properly bent at the top of the pull.")
    if elbow <= ELBOW_WARN:
        return FeedbackItem(
            "elbow_bend", "warning",
            f"Elbows not bending enough ({elbow:.0f}°). Drive your elbows up and let the bar hang — "
            "elbows should always be higher than your wrists.",
        )
    return FeedbackItem(
        "elbow_bend", "error",
        f"Arms barely bent ({elbow:.0f}°). Pull the bar toward your chin by driving elbows upward — "
        "use a lighter weight if needed.",
    )


def _swing_feedback(swing: Optional[float]) -> FeedbackItem:
    if swing is None:
        return FeedbackItem("body_swing", "warning",
                            "Could not assess body swing — position the camera directly in front of you.")
    if swing <= SWING_GOOD:
        return FeedbackItem("body_swing", "ok", "Good control — no excessive body swing.")
    if swing <= SWING_WARN:
        return FeedbackItem(
            "body_swing", "warning",
            f"Slight body lean detected ({swing:.0f}°). Keep your torso upright — lower the weight if needed.",
        )
    return FeedbackItem(
        "body_swing", "error",
        f"Significant torso lean ({swing:.0f}°). You are using momentum instead of your shoulders and traps. "
        "Use a lighter weight and pull with a slow, controlled motion.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class UprightRowClassifier(BaseClassifier):
    """Rule-based upright row technique classifier (front view)."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        peak = _peak_height(frames)
        elbow = _elbow_bend(frames)
        swing = _body_swing(frames)

        feedback = [
            _height_feedback(peak),
            _elbow_feedback(elbow),
            _swing_feedback(swing),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
