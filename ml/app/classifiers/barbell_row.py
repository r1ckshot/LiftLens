import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Torso angle thresholds (back_angle: 0° = upright, 90° = horizontal).
# BarBend / StrongLifts: torso should be roughly parallel to floor (45–90°).
# ACE: "lean forward at a 45-degree angle" = 45° minimum.
BACK_GOOD = 55.0    # properly hinged; lats loaded correctly
BACK_WARN = 30.0    # too upright (Yates-row style); reduces lat engagement

# Pull ROM thresholds (elbow angle at peak of pull; 180° = straight, 90° = right angle).
# Research: elbow should reach ~90° at peak (bar to lower chest/belly).
ROM_GOOD = 100.0    # full pull — elbows at or behind torso level
ROM_WARN = 130.0    # partial pull — bar not reaching the body

# Exercise phase detection: frames where the lifter is clearly bent over.
_ROW_BACK_MIN = 30.0

# Exclude physically impossible elbow-angle artifacts.
_MIN_PLAUSIBLE_ELBOW = 30.0


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _row_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames where the lifter is bent over enough to be performing the row."""
    row = [f for f in frames if f.back_angle is not None and f.back_angle > _ROW_BACK_MIN]
    return row if row else frames


def _torso_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back angle during the row phase."""
    row = _row_phase_frames(frames)
    vals = [f.back_angle for f in row if f.back_angle is not None]
    return statistics.median(vals) if vals else None


def _min_elbow_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum elbow angle across all frames — the peak of the pull."""
    vals = [e for f in frames
            if (e := _avg_elbow(f)) is not None and e >= _MIN_PLAUSIBLE_ELBOW]
    return min(vals) if vals else None


def _torso_feedback(torso: Optional[float]) -> FeedbackItem:
    if torso is None:
        return FeedbackItem("back_position", "error", "Could not measure torso angle — hips/shoulders not visible.")
    if torso >= BACK_GOOD:
        return FeedbackItem("back_position", "ok", "Good torso angle — properly hinged forward throughout the set.")
    if torso >= BACK_WARN:
        return FeedbackItem(
            "back_position", "warning",
            f"Torso too upright ({torso:.0f}°). Hinge forward more at the hips — aim for your torso parallel to the floor to maximise lat engagement.",
        )
    return FeedbackItem(
        "back_position", "error",
        f"Not enough forward lean ({torso:.0f}°). Bend at the hips until your torso is roughly parallel to the floor before pulling.",
    )


def _rom_feedback(min_elbow: Optional[float]) -> FeedbackItem:
    if min_elbow is None:
        return FeedbackItem("pull_rom", "error", "Could not measure pull range — elbows not visible.")
    if min_elbow <= ROM_GOOD:
        return FeedbackItem("pull_rom", "ok", "Good pull — bar reaching the body with elbows fully bent.")
    if min_elbow <= ROM_WARN:
        return FeedbackItem(
            "pull_rom", "warning",
            f"Partial range of motion ({min_elbow:.0f}°). Pull the bar all the way to your lower chest or belly — drive elbows behind your body.",
        )
    return FeedbackItem(
        "pull_rom", "error",
        f"Very incomplete pull ({min_elbow:.0f}°). Bend your elbows fully and pull the bar to your torso on every rep.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class BarbellRowClassifier(BaseClassifier):
    """Rule-based barbell row technique classifier (side view)."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        torso = _torso_angle(frames)
        min_elbow = _min_elbow_angle(frames)

        feedback = [
            _torso_feedback(torso),
            _rom_feedback(min_elbow),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
