import statistics
from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Elbow flare: angle between elbow and shoulder in world space.
# 0° = elbows directly in front (good), 90° = fully flared to sides (bad).
# Research: elbows should track roughly 30-45° in front of the bar path (OHP).
FLARE_GOOD = 60.0
FLARE_WARN = 75.0

# Back lean in world space (spine vs vertical).
# 0° = perfectly upright; >15° = noticeable lean.
BACK_GOOD = 15.0
BACK_WARN = 25.0

# Lockout: shoulder angle at the top of the press.
# Research: full lockout = arms nearly vertical, shoulder angle ~160-180°.
LOCKOUT_GOOD = 160.0
LOCKOUT_WARN = 145.0

# Press-phase detection: frames where avg shoulder angle > 60° (arms are raised).
_PRESS_SHOULDER_MIN = 60.0


def _avg_shoulder(f: FrameFeatures) -> Optional[float]:
    if f.shoulder_angle_left is not None and f.shoulder_angle_right is not None:
        return (f.shoulder_angle_left + f.shoulder_angle_right) / 2
    return f.shoulder_angle_left if f.shoulder_angle_left is not None else f.shoulder_angle_right


def _press_phase_frames(frames: list[FrameFeatures]) -> list[FrameFeatures]:
    """Frames where the arms are actively raised (press phase)."""
    press = [f for f in frames if (s := _avg_shoulder(f)) is not None and s > _PRESS_SHOULDER_MIN]
    return press if press else frames


def _press_phase_flare(frames: list[FrameFeatures]) -> Optional[float]:
    """Median elbow flare angle during the press phase."""
    press = _press_phase_frames(frames)
    vals = [f.elbow_flare_angle_3d for f in press if f.elbow_flare_angle_3d is not None]
    return statistics.median(vals) if vals else None


def _press_phase_back_lean(frames: list[FrameFeatures]) -> Optional[float]:
    """Median back lean angle during the press phase."""
    press = _press_phase_frames(frames)
    vals = [f.back_lean_3d for f in press if f.back_lean_3d is not None]
    return statistics.median(vals) if vals else None


def _max_shoulder_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Maximum average shoulder angle across the video — the lockout position."""
    vals = [s for f in frames if (s := _avg_shoulder(f)) is not None]
    return max(vals) if vals else None


def _elbow_feedback(flare: Optional[float]) -> FeedbackItem:
    if flare is None:
        return FeedbackItem(
            "elbow_position", "error",
            "Could not measure elbow position — arms not visible or no 3D data.",
        )
    if flare <= FLARE_GOOD:
        return FeedbackItem("elbow_position", "ok", "Good elbow position — tracking forward through the press.")
    if flare <= FLARE_WARN:
        return FeedbackItem(
            "elbow_position", "warning",
            f"Slight elbow flare ({flare:.0f}°). Keep your elbows tracking slightly forward during the press.",
        )
    return FeedbackItem(
        "elbow_position", "error",
        f"Excessive elbow flare ({flare:.0f}°). Drive your elbows forward and in — don't let them wing out to the sides.",
    )


def _lockout_feedback(max_shoulder: Optional[float]) -> FeedbackItem:
    if max_shoulder is None:
        return FeedbackItem("lockout", "error", "Could not measure lockout — shoulders not visible.")
    if max_shoulder >= LOCKOUT_GOOD:
        return FeedbackItem("lockout", "ok", "Good lockout — arms fully extended overhead.")
    if max_shoulder >= LOCKOUT_WARN:
        return FeedbackItem(
            "lockout", "warning",
            f"Incomplete lockout ({max_shoulder:.0f}°). Press to full extension and shrug your traps at the top.",
        )
    return FeedbackItem(
        "lockout", "error",
        f"No lockout detected ({max_shoulder:.0f}°). Fully extend your arms overhead at the top of each rep.",
    )


def _back_feedback(lean: Optional[float]) -> FeedbackItem:
    if lean is None:
        return FeedbackItem(
            "back_position", "error",
            "Could not measure back lean — shoulders/hips not visible or no 3D data.",
        )
    if lean <= BACK_GOOD:
        return FeedbackItem("back_position", "ok", "Good upright torso position.")
    if lean <= BACK_WARN:
        return FeedbackItem(
            "back_position", "warning",
            f"Slight back lean ({lean:.0f}°). Brace your core and keep your torso vertical.",
        )
    return FeedbackItem(
        "back_position", "error",
        f"Excessive back lean ({lean:.0f}°). Avoid leaning back — tighten your core and glutes.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class OverheadPressClassifier(BaseClassifier):
    """Rule-based overhead press technique classifier using 3D world landmarks."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        flare = _press_phase_flare(frames)
        lean = _press_phase_back_lean(frames)
        max_shoulder = _max_shoulder_angle(frames)

        feedback = [
            _elbow_feedback(flare),
            _lockout_feedback(max_shoulder),
            _back_feedback(lean),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
