from typing import Optional

from app.feature_extractor import FrameFeatures
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem

# Elbow angle at the top of the pull-up (arms maximally bent).
# Research: mean elbow flexion ROM at top = 93.4°; chin above bar ≈ 90°.
DEPTH_GOOD = 90.0
DEPTH_WARN = 120.0

# Elbow angle at the bottom (dead hang, arms fully extended).
# Arms should be nearly straight between reps.
EXTENSION_GOOD = 160.0
EXTENSION_WARN = 140.0

# Exclude MediaPipe artifact frames where elbow angle is physically impossible.
_ELBOW_ARTIFACT_MIN = 45.0


def _avg_elbow(f: FrameFeatures) -> Optional[float]:
    if f.elbow_angle_left is not None and f.elbow_angle_right is not None:
        return (f.elbow_angle_left + f.elbow_angle_right) / 2
    return f.elbow_angle_left if f.elbow_angle_left is not None else f.elbow_angle_right


def _min_elbow_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Minimum average elbow angle across the video — the top of the pull-up."""
    angles = [e for f in frames if (e := _avg_elbow(f)) is not None and e >= _ELBOW_ARTIFACT_MIN]
    return min(angles) if angles else None


def _max_elbow_angle(frames: list[FrameFeatures]) -> Optional[float]:
    """Maximum average elbow angle across the video — the dead hang bottom position."""
    angles = [e for f in frames if (e := _avg_elbow(f)) is not None]
    return max(angles) if angles else None


def _depth_feedback(min_elbow: Optional[float]) -> FeedbackItem:
    if min_elbow is None:
        return FeedbackItem("range_of_motion", "error", "Could not measure elbow angle — arms not visible.")
    if min_elbow <= DEPTH_GOOD:
        return FeedbackItem("range_of_motion", "ok", "Good range of motion — full height achieved.")
    if min_elbow <= DEPTH_WARN:
        return FeedbackItem(
            "range_of_motion", "warning",
            f"Partial rep ({min_elbow:.0f}°). Pull higher until your chin clears the overhead grip.",
        )
    return FeedbackItem(
        "range_of_motion", "error",
        f"Insufficient height ({min_elbow:.0f}°). Pull yourself much higher — chin must clear the grip point.",
    )


def _extension_feedback(max_elbow: Optional[float]) -> FeedbackItem:
    if max_elbow is None:
        return FeedbackItem("full_extension", "error", "Could not measure arm extension — arms not visible.")
    if max_elbow >= EXTENSION_GOOD:
        return FeedbackItem("full_extension", "ok", "Good dead hang — arms fully extended between reps.")
    if max_elbow >= EXTENSION_WARN:
        return FeedbackItem(
            "full_extension", "warning",
            f"Incomplete extension ({max_elbow:.0f}°). Fully hang between reps to maximise range of motion.",
        )
    return FeedbackItem(
        "full_extension", "error",
        f"Arms not fully extended ({max_elbow:.0f}°). Let your arms straighten completely at the bottom of each rep.",
    )


def _overall_score(items: list[FeedbackItem]) -> str:
    statuses = {item.status for item in items}
    if "error" in statuses:
        return "poor"
    if "warning" in statuses:
        return "needs_improvement"
    return "good"


class PullUpClassifier(BaseClassifier):
    """Rule-based pull-up technique classifier."""

    def predict(self, features: list[Optional[FrameFeatures]]) -> ClassificationResult:
        frames = [f for f in features if f is not None]

        if not frames:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem("general", "error", "No pose detected in video.")],
            )

        min_elbow = _min_elbow_angle(frames)
        max_elbow = _max_elbow_angle(frames)

        feedback = [
            _depth_feedback(min_elbow),
            _extension_feedback(max_elbow),
        ]

        return ClassificationResult(
            overall_score=_overall_score(feedback),
            feedback=feedback,
        )
