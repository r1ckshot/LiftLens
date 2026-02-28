import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Body position thresholds (back_angle: 0° = upright, 90° = horizontal).
# Flat bench press: person lies nearly horizontal → back_angle 80–90°.
# Camera validator is bypassed for this exercise (spread_ratio breaks for
# lying bodies), so body position is verified here instead.
BP_FLAT_GOOD = 70.0   # ≥ 70° = lying flat; correct for bench press
BP_FLAT_WARN = 50.0   # 50–70° = elevated; looks like incline bench press

# Depth thresholds (min elbow angle at bottom of press; 90° = right angle).
# NSCA / BarBend: bar should touch or nearly touch chest → elbow ~90° at bottom.
DEPTH_GOOD = 100.0   # bar at or near chest; full ROM
DEPTH_WARN = 125.0   # partial ROM; bar not reaching chest

# Lockout thresholds (max elbow angle at top of press).
# Powerlifting: full lockout required. Bodybuilding: ~170° acceptable.
LOCKOUT_GOOD = 155.0  # near-full or full extension
LOCKOUT_WARN = 135.0  # significant incomplete lockout

_MIN_PLAUSIBLE_ELBOW = 30.0


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _body_position(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back_angle — used to verify the person is lying flat."""
    vals = [f.back_angle for f in frames if f.back_angle is not None]
    return statistics.median(vals) if vals else None


def _min_elbow(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum elbow angle — the deepest point of the press (bar at chest)."""
    vals = [e for f in frames if (e := _avg_elbow(f)) is not None and e >= _MIN_PLAUSIBLE_ELBOW]
    return min(vals) if vals else None


def _max_elbow(frames: list[FrameFeatures]) -> Optional[float]:
    """Maximum elbow angle — the lockout position at the top of the press."""
    vals = [e for f in frames if (e := _avg_elbow(f)) is not None and e >= _MIN_PLAUSIBLE_ELBOW]
    return max(vals) if vals else None


def _position_feedback(pos: Optional[float]) -> FeedbackItem:
    if pos is None:
        return FeedbackItem("body_position", "error", "Could not detect body position — ensure your full body is visible.")
    if pos > 100.0:
        return FeedbackItem(
            "body_position", "error",
            "Could not reliably read body position from this camera angle. "
            "Film from the side of the bench for accurate analysis.",
        )
    if pos >= BP_FLAT_GOOD:
        return FeedbackItem("body_position", "ok", "Good setup — body correctly horizontal on the bench.")
    if pos >= BP_FLAT_WARN:
        return FeedbackItem(
            "body_position", "warning",
            f"Body too elevated ({pos:.0f}°). Lie flat on the bench — this looks more like an incline press. "
            "Use the Incline Bench Press exercise if that is your intention.",
        )
    return FeedbackItem(
        "body_position", "error",
        f"Body position not suitable for flat bench press ({pos:.0f}°). "
        "Lie flat on the bench, or switch to Incline Bench Press.",
    )


def _depth_feedback(min_el: Optional[float]) -> FeedbackItem:
    if min_el is None:
        return FeedbackItem("depth", "error", "Could not measure elbow angle — arms not visible.")
    if min_el <= DEPTH_GOOD:
        return FeedbackItem("depth", "ok", "Good depth — weight reaching the chest on each rep.")
    if min_el <= DEPTH_WARN:
        return FeedbackItem(
            "depth", "warning",
            f"Partial range of motion ({min_el:.0f}°). Lower the weight all the way to your chest before pressing back up.",
        )
    return FeedbackItem(
        "depth", "error",
        f"Very incomplete range of motion ({min_el:.0f}°). The weight must touch or nearly touch your chest for a full rep.",
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


class BenchPressClassifier(BaseClassifier):
    """Rule-based flat bench press technique classifier (side view, person lying horizontal)."""

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
