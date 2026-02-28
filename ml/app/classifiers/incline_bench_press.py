import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Body position thresholds (back_angle: 0° = upright, 90° = horizontal).
# Incline at 30° from horizontal → back_angle ~60°.
# Incline at 45° from horizontal → back_angle ~45°.
# Optimal range (30–45° bench) → back_angle 45–60°. Allow 35–70° in practice.
IBP_POS_MIN = 35.0    # below = bench too steep (> 55° incline; more like OHP)
IBP_POS_MAX = 70.0    # above = bench too flat (< 20° incline; looks like flat bench press)

# Depth thresholds (min elbow angle at bottom of press; 90° = right angle).
# NSCA / SetForSet: bar lowers to upper chest (just below clavicle); elbow ~90°.
DEPTH_GOOD = 100.0   # bar at or near upper chest; full ROM
DEPTH_WARN = 125.0   # partial ROM; bar not reaching chest

# Lockout thresholds (max elbow angle at top of press).
LOCKOUT_GOOD = 155.0  # near-full or full extension
LOCKOUT_WARN = 135.0  # significant incomplete lockout

_MIN_PLAUSIBLE_ELBOW = 30.0


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _body_position(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back_angle — used to verify the bench is at the correct incline angle."""
    vals = [f.back_angle for f in frames if f.back_angle is not None]
    return statistics.median(vals) if vals else None


def _min_elbow(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum elbow angle — the deepest point of the press (bar at upper chest)."""
    vals = [e for f in frames if (e := _avg_elbow(f)) is not None and e >= _MIN_PLAUSIBLE_ELBOW]
    return min(vals) if vals else None


def _max_elbow(frames: list[FrameFeatures]) -> Optional[float]:
    """Maximum elbow angle — the lockout position at the top of the press."""
    vals = [e for f in frames if (e := _avg_elbow(f)) is not None and e >= _MIN_PLAUSIBLE_ELBOW]
    return max(vals) if vals else None


def _position_feedback(pos: Optional[float]) -> FeedbackItem:
    if pos is None:
        return FeedbackItem("body_position", "error", "Could not detect body position — ensure your full body is visible.")
    if IBP_POS_MIN <= pos <= IBP_POS_MAX:
        return FeedbackItem("body_position", "ok", "Good bench angle — torso at the correct incline for upper chest activation.")
    if pos > IBP_POS_MAX:
        return FeedbackItem(
            "body_position", "warning",
            f"Bench angle too flat ({pos:.0f}°). Raise the bench to 30–45° — "
            "or switch to Flat Bench Press if you intend to press horizontally.",
        )
    return FeedbackItem(
        "body_position", "warning",
        f"Bench angle too steep ({pos:.0f}°). Lower the bench to 30–45° — "
        "angles above 55° shift the load from upper chest to front delts.",
    )


def _depth_feedback(min_el: Optional[float]) -> FeedbackItem:
    if min_el is None:
        return FeedbackItem("depth", "error", "Could not measure elbow angle — arms not visible.")
    if min_el <= DEPTH_GOOD:
        return FeedbackItem("depth", "ok", "Good depth — weight reaching the upper chest on each rep.")
    if min_el <= DEPTH_WARN:
        return FeedbackItem(
            "depth", "warning",
            f"Partial range of motion ({min_el:.0f}°). Lower the weight all the way to your upper chest (just below the clavicle) before pressing.",
        )
    return FeedbackItem(
        "depth", "error",
        f"Very incomplete range of motion ({min_el:.0f}°). The weight must reach your upper chest for a full rep.",
    )


def _lockout_feedback(max_el: Optional[float]) -> FeedbackItem:
    if max_el is None:
        return FeedbackItem("lockout", "error", "Could not measure lockout — arms not visible.")
    if max_el >= LOCKOUT_GOOD:
        return FeedbackItem("lockout", "ok", "Good lockout — elbows fully extended at the top.")
    if max_el >= LOCKOUT_WARN:
        return FeedbackItem(
            "lockout", "warning",
            f"Incomplete lockout ({max_el:.0f}°). Fully extend your elbows at the top of each rep.",
        )
    return FeedbackItem(
        "lockout", "error",
        f"Elbows significantly bent at the top ({max_el:.0f}°). Press the bar to full arm extension on every rep.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class InclineBenchPressClassifier(BaseClassifier):
    """Rule-based incline bench press technique classifier (side view, bench at 30–45°)."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        pos = _body_position(frames)
        min_el = _min_elbow(frames)
        max_el = _max_elbow(frames)

        feedback = [
            _position_feedback(pos),
            _depth_feedback(min_el),
            _lockout_feedback(max_el),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
