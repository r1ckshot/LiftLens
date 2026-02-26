import statistics
from typing import Optional

from app.pose_estimator import Landmark, LandmarkIndex

# Side-view: left and right shoulders overlap in x → spread ratio near 0.
# Front-view: shoulders spread apart → ratio ~0.5–2.0 (varies with framing).
# Upper-body close shots (lateral raise) produce lower ratios (~0.35–0.60)
# than full-body shots (overhead press, ~0.90–1.10).
# Thresholds of 0.50/0.50 eliminate the dead zone in "any" mode:
# any ratio < 0.50 passes as side, any ratio ≥ 0.50 passes as front.
_MAX_SPREAD_RATIO = 0.50   # side view: ratio must be below this
_MIN_FRONT_SPREAD_RATIO = 0.50  # front view: ratio must be at or above this
_VISIBILITY_THRESHOLD = 0.5
_MIN_VALID_FRAMES = 10


def check_side_view(landmarks_seq: list[Optional[list[Landmark]]]) -> Optional[str]:
    """
    Returns None if the video is a valid side view.
    Returns an error message string if the camera angle is wrong or the body
    is not sufficiently visible.
    """
    valid = [f for f in landmarks_seq if f is not None]
    if len(valid) < _MIN_VALID_FRAMES:
        return (
            "Too few frames with pose detected. "
            "Ensure your full body is visible and well-lit."
        )

    ratios = []
    for frame in valid:
        lsh = frame[LandmarkIndex.LEFT_SHOULDER]
        rsh = frame[LandmarkIndex.RIGHT_SHOULDER]
        lhi = frame[LandmarkIndex.LEFT_HIP]
        rhi = frame[LandmarkIndex.RIGHT_HIP]

        if min(lsh.visibility, rsh.visibility, lhi.visibility, rhi.visibility) < _VISIBILITY_THRESHOLD:
            continue

        spread = abs(lsh.x - rsh.x)
        torso_h = abs((lsh.y + rsh.y) / 2 - (lhi.y + rhi.y) / 2)
        if torso_h > 0:
            ratios.append(spread / torso_h)

    if not ratios:
        return (
            "Could not detect body position. "
            "Ensure your full body is visible and well-lit."
        )

    if statistics.median(ratios) >= _MAX_SPREAD_RATIO:
        return (
            "Camera angle incorrect. Position the camera directly to your side "
            "at hip height, perpendicular to your movement direction."
        )

    return None


def check_front_view(landmarks_seq: list[Optional[list[Landmark]]]) -> Optional[str]:
    """
    Returns None if the video is a valid front view.
    Returns an error message string if the camera angle is wrong or the body
    is not sufficiently visible.
    """
    valid = [f for f in landmarks_seq if f is not None]
    if len(valid) < _MIN_VALID_FRAMES:
        return (
            "Too few frames with pose detected. "
            "Ensure your full body is visible and well-lit."
        )

    ratios = []
    for frame in valid:
        lsh = frame[LandmarkIndex.LEFT_SHOULDER]
        rsh = frame[LandmarkIndex.RIGHT_SHOULDER]
        lhi = frame[LandmarkIndex.LEFT_HIP]
        rhi = frame[LandmarkIndex.RIGHT_HIP]

        if min(lsh.visibility, rsh.visibility, lhi.visibility, rhi.visibility) < _VISIBILITY_THRESHOLD:
            continue

        spread = abs(lsh.x - rsh.x)
        torso_h = abs((lsh.y + rsh.y) / 2 - (lhi.y + rhi.y) / 2)
        if torso_h > 0:
            ratios.append(spread / torso_h)

    if not ratios:
        return (
            "Could not detect body position. "
            "Ensure your full body is visible and well-lit."
        )

    if statistics.median(ratios) < _MIN_FRONT_SPREAD_RATIO:
        return (
            "Camera angle incorrect. Position the camera directly in front of you, "
            "facing your chest, at approximately shoulder height."
        )

    return None
