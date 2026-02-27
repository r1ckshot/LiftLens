from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Lockout: back_angle at the most upright point AFTER the bottom of the lift.
# NSCA / Greg Nuckols (Stronger by Science): "complete hip and knee extension at the top."
LOCKOUT_GOOD = 10.0   # fully upright — hips driven through
LOCKOUT_WARN = 20.0   # slight forward lean — incomplete lockout

# Stiff-leg detection: minimum knee angle during the hinge phase.
# Unlike back_angle (which varies with limb proportions), knee angle at the
# bottom clearly separates styles:
#   Conventional: knees ~80–120° (significantly bent at the start)
#   Stiff-leg / hips too high: knees > 145° (nearly straight throughout)
# NSCA / Alan Thrall: "conventional deadlift requires deliberate knee bend at setup."
STIFF_LEG_WARN = 145.0

# Hinge-phase detection: frames where the lifter is clearly leaning forward.
_HINGE_BACK_MIN = 35.0

# Exclude physically impossible knee-angle artifacts.
_MIN_PLAUSIBLE_KNEE = 60.0


def _avg_knee(f: FrameFeatures) -> Optional[float]:
    if f.knee_angle_left is not None and f.knee_angle_right is not None:
        return (f.knee_angle_left + f.knee_angle_right) / 2
    return f.knee_angle_left if f.knee_angle_left is not None else f.knee_angle_right


def _hinge_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames where the torso is visibly tilted forward (bar is being pulled)."""
    hinge = [f for f in frames if f.back_angle is not None and f.back_angle > _HINGE_BACK_MIN]
    return hinge if hinge else frames


def _min_hinge_knee(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum knee angle during the hinge phase — the most-bent position at setup."""
    hinge = _hinge_phase_frames(frames)
    vals = [k for f in hinge
            if (k := _avg_knee(f)) is not None and k >= _MIN_PLAUSIBLE_KNEE]
    return min(vals) if vals else None


def _post_bottom_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames at and after the maximum back angle (the ascending / lockout phase).

    Avoids false positives from the lifter standing upright before the lift —
    the pre-lift stance and a proper lockout look identical in a single frame,
    so we only assess lockout AFTER the deepest point has been passed.
    """
    indexed = [(i, f) for i, f in enumerate(frames) if f.back_angle is not None]
    if not indexed:
        return frames
    max_idx = max(indexed, key=lambda x: x[1].back_angle)[0]
    return frames[max_idx:]


def _lockout_back_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum back angle after the bottom — the best lockout position achieved."""
    post = _post_bottom_frames(frames)
    vals = [f.back_angle for f in post if f.back_angle is not None]
    return min(vals) if vals else None


def _setup_feedback(min_knee: Optional[float]) -> FeedbackItem:
    if min_knee is None:
        return FeedbackItem("setup", "error", "Could not measure setup — knees not visible during the pull.")
    if min_knee > STIFF_LEG_WARN:
        return FeedbackItem(
            "setup", "warning",
            f"Knees too straight at setup ({min_knee:.0f}°). This looks like a stiff-leg deadlift. "
            f"Bend your knees more before pulling — sit into the bar and drive your hips down.",
        )
    return FeedbackItem("setup", "ok", "Good starting position — knees appropriately bent at setup.")


def _lockout_feedback(lockout: Optional[float]) -> FeedbackItem:
    if lockout is None:
        return FeedbackItem("lockout", "error", "Could not measure lockout — hips/shoulders not visible.")
    if lockout <= LOCKOUT_GOOD:
        return FeedbackItem("lockout", "ok", "Good lockout — hips fully extended at the top.")
    if lockout <= LOCKOUT_WARN:
        return FeedbackItem(
            "lockout", "warning",
            f"Incomplete lockout ({lockout:.0f}°). Drive your hips through to full extension — squeeze your glutes at the top.",
        )
    return FeedbackItem(
        "lockout", "error",
        f"No lockout achieved ({lockout:.0f}°). Fully extend hips and knees at the top of every rep.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class DeadliftClassifier(BaseClassifier):
    """Rule-based deadlift technique classifier (conventional, side view)."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        min_knee = _min_hinge_knee(frames)
        lockout = _lockout_back_angle(frames)

        feedback = [
            _setup_feedback(min_knee),
            _lockout_feedback(lockout),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
