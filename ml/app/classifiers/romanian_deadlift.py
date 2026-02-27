import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Hip hinge depth: back_angle at the peak of the hinge.
# back_angle: 0° = perfectly upright, 90° = torso parallel to floor.
# NSCA/ACE: torso should reach ~45–90° for a complete ROM Romanian deadlift.
DEPTH_GOOD = 45.0   # significant forward lean; hamstrings properly loaded
DEPTH_WARN = 30.0   # insufficient hinge; hamstrings underloaded

# Knee angle during the hinge phase (hip-knee-ankle; 180° = fully straight).
# NSCA CSCS: "maintain slight knee flexion of ~15–30°" = knee_angle 150–165°.
# Too straight (> 168°): locked knees → excessive hamstring attachment stress.
# Too bent  (< 130°): squat pattern → moves load from hamstrings to quads.
KNEE_STRAIGHT_WARN = 168.0
KNEE_BENT_WARN = 130.0

# Hinge-phase detection: frames where the back has tilted forward enough
# to be considered part of the movement (not the resting/standing position).
_HINGE_BACK_MIN = 20.0


def _avg_knee(f: FrameFeatures) -> Optional[float]:
    if f.knee_angle_left is not None and f.knee_angle_right is not None:
        return (f.knee_angle_left + f.knee_angle_right) / 2
    return f.knee_angle_left if f.knee_angle_left is not None else f.knee_angle_right


def _hinge_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames where the torso is visibly tilted forward (hinge in progress)."""
    hinge = [f for f in frames if f.back_angle is not None and f.back_angle > _HINGE_BACK_MIN]
    return hinge if hinge else frames


def _max_back_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Peak forward lean of the torso — the bottom of the hinge."""
    vals = [f.back_angle for f in frames if f.back_angle is not None]
    return max(vals) if vals else None


def _knee_at_hinge(frames: list[FrameFeatures]) -> Optional[float]:
    """Median knee angle during the hinge phase."""
    hinge = _hinge_phase_frames(frames)
    vals = [k for f in hinge if (k := _avg_knee(f)) is not None]
    return statistics.median(vals) if vals else None


def _depth_feedback(peak: Optional[float]) -> FeedbackItem:
    if peak is None:
        return FeedbackItem("hinge_depth", "error", "Could not measure hinge depth — hips/shoulders not visible.")
    if peak >= DEPTH_GOOD:
        return FeedbackItem("hinge_depth", "ok", "Good hip hinge depth — hamstrings fully loaded.")
    if peak >= DEPTH_WARN:
        return FeedbackItem(
            "hinge_depth", "warning",
            f"Shallow hinge ({peak:.0f}°). Push your hips further back and lower the weight until you feel a strong hamstring stretch.",
        )
    return FeedbackItem(
        "hinge_depth", "error",
        f"Insufficient hip hinge ({peak:.0f}°). Drive your hips back — imagine touching a wall behind you. The bar should travel close to your legs.",
    )


def _knee_feedback(knee: Optional[float]) -> FeedbackItem:
    if knee is None:
        return FeedbackItem("knee_position", "error", "Could not measure knee angle — knees not visible.")
    if knee > KNEE_STRAIGHT_WARN:
        return FeedbackItem(
            "knee_position", "warning",
            f"Knees too straight ({knee:.0f}°). Unlock your knees slightly — a soft bend reduces stress on the hamstring attachments.",
        )
    if knee < KNEE_BENT_WARN:
        return FeedbackItem(
            "knee_position", "warning",
            f"Knees too bent ({knee:.0f}°). This looks more like a deadlift than an RDL. Keep a slight, consistent bend — push hips back, not knees forward.",
        )
    return FeedbackItem("knee_position", "ok", "Good knee position — soft bend maintained throughout the hinge.")


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class RomanianDeadliftClassifier(BaseClassifier):
    """Rule-based Romanian deadlift technique classifier."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        peak = _max_back_angle(frames)
        knee = _knee_at_hinge(frames)

        feedback = [
            _depth_feedback(peak),
            _knee_feedback(knee),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
