import os
import subprocess
from dataclasses import dataclass
from typing import Optional, Callable

import cv2
import mediapipe as mp
import numpy as np

from app.pose_estimator import Landmark
from app.feature_extractor import FrameFeatures
from app.exercises import EXERCISES
from app.thresholds import (
    SQUAT_KNEE_GOOD, SQUAT_KNEE_WARN, SQUAT_BACK_GOOD, SQUAT_BACK_WARN,
    LUNGE_KNEE_GOOD, LUNGE_KNEE_WARN, LUNGE_BACK_GOOD, LUNGE_BACK_WARN,
    PUSHUP_ELBOW_GOOD, PUSHUP_ELBOW_WARN, PUSHUP_HIP_GOOD, PUSHUP_HIP_WARN,
    BENCH_ELBOW_GOOD, BENCH_ELBOW_WARN,
    INCLINE_ELBOW_GOOD, INCLINE_ELBOW_WARN,
    OHP_LOCKOUT_GOOD, OHP_LOCKOUT_WARN,
    LATERAL_HEIGHT_GOOD, LATERAL_HEIGHT_WARN, LATERAL_ELBOW_GOOD, LATERAL_ELBOW_WARN,
    UPRIGHT_ROW_SHOULDER_GOOD, UPRIGHT_ROW_SHOULDER_WARN,
    UPRIGHT_ROW_ELBOW_GOOD, UPRIGHT_ROW_ELBOW_WARN,
    RDL_BACK_GOOD, RDL_BACK_WARN, RDL_KNEE_GOOD, RDL_KNEE_STRAIGHT_WARN, RDL_KNEE_BENT_WARN,
    DEADLIFT_KNEE_GOOD, DEADLIFT_STIFF_LEG_WARN, DEADLIFT_LOCKOUT_GOOD, DEADLIFT_LOCKOUT_WARN,
    BARBELL_ROW_BACK_GOOD, BARBELL_ROW_BACK_WARN, BARBELL_ROW_ROM_GOOD, BARBELL_ROW_ROM_WARN,
    PULLUP_DEPTH_GOOD, PULLUP_DEPTH_WARN, PULLUP_EXTENSION_GOOD, PULLUP_EXTENSION_WARN,
)

_VISIBILITY_THRESHOLD = 0.5

# ── MediaPipe landmark indices ────────────────────────────────────────────────
_LSHOULDER, _RSHOULDER = 11, 12
_LELBOW,    _RELBOW    = 13, 14
_LWRIST,    _RWRIST    = 15, 16
_LHIP,      _RHIP      = 23, 24
_LKNEE,     _RKNEE     = 25, 26
_LANKLE,    _RANKLE    = 27, 28

# Left/right landmark sets for near-side detection
_LEFT_LM  = frozenset({_LSHOULDER, _LELBOW, _LWRIST, _LHIP, _LKNEE, _LANKLE})
_RIGHT_LM = frozenset({_RSHOULDER, _RELBOW, _RWRIST, _RHIP, _RKNEE, _RANKLE})

# Skip: face (0-10), hand fingers (17-22), foot details (29-32)
_SKIP_LM = frozenset(range(0, 11)) | frozenset(range(17, 23)) | frozenset(range(29, 33))
_DRAW_CONNECTIONS = frozenset(
    (a, b) for a, b in mp.solutions.pose.POSE_CONNECTIONS
    if a not in _SKIP_LM and b not in _SKIP_LM
)

# ── Colours (BGR) ─────────────────────────────────────────────────────────────
_STATUS_COLORS = {
    "ok":      (50,  205,  50),   # green
    "warning": (0,   165, 255),   # orange
    "error":   (0,    0,  220),   # red
}
_DEFAULT_COLOR = (110, 110, 110)  # grey — bones with no metric assigned
_DOT_COLOR     = (210,  50, 210)  # purple — all joints, always fixed

_STATUS_PRIORITY = {"ok": 0, "warning": 1, "error": 2}

_LINE_THICKNESS = 2
_DOT_RADIUS     = 5
_ARC_RADIUS     = 30
_ARC_THICKNESS  = 2
_FONT           = cv2.FONT_HERSHEY_SIMPLEX
_FONT_SCALE     = 0.62
_FONT_THICKNESS = 2


# ── AngleViz ─────────────────────────────────────────────────────────────────

@dataclass
class AngleViz:
    """Configuration for one joint angle visualisation.

    Only the two bones directly adjacent to the vertex — (vertex, arm_a) and
    (vertex, arm_b) — receive the dynamic colour.

    active_below / active_above define when the arc is "active":
      - lower_is_better: arc shown only when value <= active_below
      - higher_is_better: arc shown only when value >= active_above
    Outside this range (rest / neutral position) neither the arc nor the label
    are drawn, so standing straight never shows a misleading red arc.
    """
    vertex:          int
    arm_a:           int
    arm_b:           int
    get_value:       Callable             # (FrameFeatures) -> Optional[float]
    good:            float
    warn:            float
    lower_is_better: bool          = True
    active_below:    Optional[float] = None   # suppress when value > this
    active_above:    Optional[float] = None   # suppress when value < this


# ── Per-exercise angle configurations ─────────────────────────────────────────
# Each exercise lists only the angles relevant to that movement.
# L and R variants are both listed; near-side filtering selects the visible one
# for side-view exercises automatically.

EXERCISE_ANGLE_VIZ: dict[str, list[AngleViz]] = {
    "squat": [
        AngleViz(_LKNEE, _LHIP,      _LANKLE, lambda f: f.knee_angle_left,  SQUAT_KNEE_GOOD, SQUAT_KNEE_WARN, True, 168.),
        AngleViz(_RKNEE, _RHIP,      _RANKLE, lambda f: f.knee_angle_right, SQUAT_KNEE_GOOD, SQUAT_KNEE_WARN, True, 168.),
        AngleViz(_LHIP,  _LSHOULDER, _LKNEE,  lambda f: f.back_angle,       SQUAT_BACK_GOOD, SQUAT_BACK_WARN, True),
        AngleViz(_RHIP,  _RSHOULDER, _RKNEE,  lambda f: f.back_angle,       SQUAT_BACK_GOOD, SQUAT_BACK_WARN, True),
    ],
    "lunge": [
        AngleViz(_LKNEE, _LHIP,      _LANKLE, lambda f: f.knee_angle_left,  LUNGE_KNEE_GOOD, LUNGE_KNEE_WARN, True, 168.),
        AngleViz(_RKNEE, _RHIP,      _RANKLE, lambda f: f.knee_angle_right, LUNGE_KNEE_GOOD, LUNGE_KNEE_WARN, True, 168.),
        AngleViz(_LHIP,  _LSHOULDER, _LKNEE,  lambda f: f.back_angle,       LUNGE_BACK_GOOD, LUNGE_BACK_WARN, True),
        AngleViz(_RHIP,  _RSHOULDER, _RKNEE,  lambda f: f.back_angle,       LUNGE_BACK_GOOD, LUNGE_BACK_WARN, True),
    ],
    "romanian_deadlift": [
        # Leaning forward IS the exercise — lower_is_better=False, more lean = greener.
        AngleViz(_LHIP,  _LSHOULDER, _LKNEE,  lambda f: f.back_angle,        RDL_BACK_GOOD, RDL_BACK_WARN, False, None, 20.),
        AngleViz(_RHIP,  _RSHOULDER, _RKNEE,  lambda f: f.back_angle,        RDL_BACK_GOOD, RDL_BACK_WARN, False, None, 20.),
        # Knee: slight bend required. Warns if >RDL_KNEE_STRAIGHT_WARN (locked) or <RDL_KNEE_BENT_WARN (squat).
        AngleViz(_LKNEE, _LHIP,      _LANKLE, lambda f: f.knee_angle_left,  RDL_KNEE_GOOD, RDL_KNEE_STRAIGHT_WARN, True, None, RDL_KNEE_BENT_WARN),
        AngleViz(_RKNEE, _RHIP,      _RANKLE, lambda f: f.knee_angle_right, RDL_KNEE_GOOD, RDL_KNEE_STRAIGHT_WARN, True, None, RDL_KNEE_BENT_WARN),
    ],
    "deadlift": [
        # Knee: detect stiff-leg setup. Warns if >DEADLIFT_STIFF_LEG_WARN. Hide when standing (>168°).
        AngleViz(_LKNEE, _LHIP,      _LANKLE, lambda f: f.knee_angle_left,  DEADLIFT_KNEE_GOOD, DEADLIFT_STIFF_LEG_WARN, True, 168.),
        AngleViz(_RKNEE, _RHIP,      _RANKLE, lambda f: f.knee_angle_right, DEADLIFT_KNEE_GOOD, DEADLIFT_STIFF_LEG_WARN, True, 168.),
        # Back: lockout indicator — show only when near upright (active_below=30°).
        AngleViz(_LHIP,  _LSHOULDER, _LKNEE,  lambda f: f.back_angle, DEADLIFT_LOCKOUT_GOOD, DEADLIFT_LOCKOUT_WARN, True, 30.),
        AngleViz(_RHIP,  _RSHOULDER, _RKNEE,  lambda f: f.back_angle, DEADLIFT_LOCKOUT_GOOD, DEADLIFT_LOCKOUT_WARN, True, 30.),
    ],
    "push_up": [
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  PUSHUP_ELBOW_GOOD, PUSHUP_ELBOW_WARN, True, 165.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, PUSHUP_ELBOW_GOOD, PUSHUP_ELBOW_WARN, True, 165.),
        # Body alignment: hip should be in a straight line shoulder-hip-knee (~180°).
        AngleViz(_LHIP, _LSHOULDER, _LKNEE, lambda f: f.hip_angle_left,  PUSHUP_HIP_GOOD, PUSHUP_HIP_WARN, False),
        AngleViz(_RHIP, _RSHOULDER, _RKNEE, lambda f: f.hip_angle_right, PUSHUP_HIP_GOOD, PUSHUP_HIP_WARN, False),
    ],
    "bench_press": [
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  BENCH_ELBOW_GOOD, BENCH_ELBOW_WARN, True, 155.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, BENCH_ELBOW_GOOD, BENCH_ELBOW_WARN, True, 155.),
    ],
    "incline_bench_press": [
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  INCLINE_ELBOW_GOOD, INCLINE_ELBOW_WARN, True, 155.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, INCLINE_ELBOW_GOOD, INCLINE_ELBOW_WARN, True, 155.),
    ],
    "overhead_press": [
        AngleViz(_LELBOW,    _LSHOULDER, _LWRIST,  lambda f: f.elbow_angle_left,    OHP_LOCKOUT_GOOD, OHP_LOCKOUT_WARN, False, None, 100.),
        AngleViz(_RELBOW,    _RSHOULDER, _RWRIST,  lambda f: f.elbow_angle_right,   OHP_LOCKOUT_GOOD, OHP_LOCKOUT_WARN, False, None, 100.),
        AngleViz(_LSHOULDER, _LHIP,      _LELBOW,  lambda f: f.shoulder_angle_left,  OHP_LOCKOUT_GOOD, OHP_LOCKOUT_WARN, False, None, 60.),
        AngleViz(_RSHOULDER, _RHIP,      _RELBOW,  lambda f: f.shoulder_angle_right, OHP_LOCKOUT_GOOD, OHP_LOCKOUT_WARN, False, None, 60.),
    ],
    "lateral_raise": [
        AngleViz(_LSHOULDER, _LHIP,      _LELBOW,  lambda f: f.shoulder_angle_left,  LATERAL_HEIGHT_GOOD, LATERAL_HEIGHT_WARN, False, None, 20.),
        AngleViz(_RSHOULDER, _RHIP,      _RELBOW,  lambda f: f.shoulder_angle_right, LATERAL_HEIGHT_GOOD, LATERAL_HEIGHT_WARN, False, None, 20.),
        AngleViz(_LELBOW,    _LSHOULDER, _LWRIST,  lambda f: f.elbow_angle_left,  LATERAL_ELBOW_GOOD, LATERAL_ELBOW_WARN, False, None, 20.),
        AngleViz(_RELBOW,    _RSHOULDER, _RWRIST,  lambda f: f.elbow_angle_right, LATERAL_ELBOW_GOOD, LATERAL_ELBOW_WARN, False, None, 20.),
    ],
    "upright_row": [
        AngleViz(_LSHOULDER, _LHIP,      _LELBOW,  lambda f: f.shoulder_angle_left,  UPRIGHT_ROW_SHOULDER_GOOD, UPRIGHT_ROW_SHOULDER_WARN, False, None, 20.),
        AngleViz(_RSHOULDER, _RHIP,      _RELBOW,  lambda f: f.shoulder_angle_right, UPRIGHT_ROW_SHOULDER_GOOD, UPRIGHT_ROW_SHOULDER_WARN, False, None, 20.),
        AngleViz(_LELBOW,    _LSHOULDER, _LWRIST,  lambda f: f.elbow_angle_left,  UPRIGHT_ROW_ELBOW_GOOD, UPRIGHT_ROW_ELBOW_WARN, True, 165.),
        AngleViz(_RELBOW,    _RSHOULDER, _RWRIST,  lambda f: f.elbow_angle_right, UPRIGHT_ROW_ELBOW_GOOD, UPRIGHT_ROW_ELBOW_WARN, True, 165.),
    ],
    "barbell_row": [
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  BARBELL_ROW_ROM_GOOD, BARBELL_ROW_ROM_WARN, True, 165.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, BARBELL_ROW_ROM_GOOD, BARBELL_ROW_ROM_WARN, True, 165.),
        AngleViz(_LHIP,   _LSHOULDER, _LKNEE,  lambda f: f.back_angle, BARBELL_ROW_BACK_GOOD, BARBELL_ROW_BACK_WARN, False, None, 30.),
        AngleViz(_RHIP,   _RSHOULDER, _RKNEE,  lambda f: f.back_angle, BARBELL_ROW_BACK_GOOD, BARBELL_ROW_BACK_WARN, False, None, 30.),
    ],
    "pull_up": [
        # Top of rep: pull height. Active only when arm is bent (<130°).
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  PULLUP_DEPTH_GOOD, PULLUP_DEPTH_WARN, True, 130.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, PULLUP_DEPTH_GOOD, PULLUP_DEPTH_WARN, True, 130.),
        # Bottom of rep: dead hang extension. Active when arm near-straight (>135°).
        AngleViz(_LELBOW, _LSHOULDER, _LWRIST, lambda f: f.elbow_angle_left,  PULLUP_EXTENSION_GOOD, PULLUP_EXTENSION_WARN, False, None, 135.),
        AngleViz(_RELBOW, _RSHOULDER, _RWRIST, lambda f: f.elbow_angle_right, PULLUP_EXTENSION_GOOD, PULLUP_EXTENSION_WARN, False, None, 135.),
    ],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _angle_color(value: float, good: float, warn: float, lower_is_better: bool) -> tuple:
    if lower_is_better:
        if value <= good: return _STATUS_COLORS["ok"]
        if value <= warn: return _STATUS_COLORS["warning"]
        return _STATUS_COLORS["error"]
    else:
        if value >= good: return _STATUS_COLORS["ok"]
        if value >= warn: return _STATUS_COLORS["warning"]
        return _STATUS_COLORS["error"]


def _color_priority(color: tuple) -> int:
    for status, c in _STATUS_COLORS.items():
        if c == color:
            return _STATUS_PRIORITY[status]
    return -1


def _is_active(av: AngleViz, val: float) -> bool:
    """Return True if the angle is in the 'active' range where arc should be shown."""
    if av.active_below is not None and val > av.active_below:
        return False
    if av.active_above is not None and val < av.active_above:
        return False
    return True


def _filter_near_side(landmarks: list[Landmark], vizs: list[AngleViz]) -> list[AngleViz]:
    """For side-view exercises, return only the vizs whose vertex is on the
    side of the body closer to the camera (smaller z = closer in MediaPipe)."""
    if not vizs:
        return vizs
    try:
        left_z  = (landmarks[_LSHOULDER].z + landmarks[_LHIP].z) / 2
        right_z = (landmarks[_RSHOULDER].z + landmarks[_RHIP].z) / 2
        near_left = left_z <= right_z
    except (IndexError, AttributeError):
        return vizs  # fallback: show all

    result = []
    for av in vizs:
        is_left  = av.vertex in _LEFT_LM
        is_right = av.vertex in _RIGHT_LM
        if is_left and not is_right:
            if near_left:
                result.append(av)
        elif is_right and not is_left:
            if not near_left:
                result.append(av)
        else:
            result.append(av)  # center/ambiguous — always include
    return result


def _build_frame_bone_colors(
    features: FrameFeatures,
    vizs: list[AngleViz],
) -> dict[frozenset, tuple]:
    """Compute per-frame bone colours from actual angle values vs thresholds.
    Only the two bones directly adjacent to each arc vertex are coloured:
    (vertex, arm_a) and (vertex, arm_b).  Highest priority wins conflicts."""
    result: dict[frozenset, tuple] = {}
    priorities: dict[frozenset, int] = {}

    for av in vizs:
        val = av.get_value(features)
        if val is None or not _is_active(av, val):
            continue
        color = _angle_color(val, av.good, av.warn, av.lower_is_better)
        prio  = _color_priority(color)
        for bone in (frozenset({av.vertex, av.arm_a}), frozenset({av.vertex, av.arm_b})):
            if prio > priorities.get(bone, -1):
                result[bone]     = color
                priorities[bone] = prio

    return result


def _lm_pt(
    landmarks: list[Landmark],
    idx: int,
    w: int,
    h: int,
) -> Optional[tuple[int, int]]:
    lm = landmarks[idx]
    return (int(lm.x * w), int(lm.y * h)) if lm.visibility > _VISIBILITY_THRESHOLD else None


def _draw_angle_arc(
    frame,
    pt_v: tuple[int, int],
    pt_a: tuple[int, int],
    pt_b: tuple[int, int],
    value: float,
    color: tuple,
) -> None:
    """Draw arc at pt_v between arms toward pt_a and pt_b.
    Angle value is labelled with a semi-transparent background, offset well
    clear of the arc so there is no overlap.  OpenCV is ASCII-only; no degree
    symbol is used."""
    va = np.array(pt_a, dtype=float) - np.array(pt_v, dtype=float)
    vb = np.array(pt_b, dtype=float) - np.array(pt_v, dtype=float)
    if np.linalg.norm(va) < 1 or np.linalg.norm(vb) < 1:
        return

    ang_a = np.degrees(np.arctan2(va[1], va[0]))
    ang_b = np.degrees(np.arctan2(vb[1], vb[0]))
    diff  = (ang_b - ang_a) % 360
    if diff > 180:
        start, sweep = ang_b, 360 - diff
    else:
        start, sweep = ang_a, diff

    cv2.ellipse(
        frame, pt_v, (_ARC_RADIUS, _ARC_RADIUS),
        0, start, start + sweep, color, _ARC_THICKNESS, cv2.LINE_AA,
    )

    # Place label well outside the arc so it never overlaps it
    mid_rad = np.radians(start + sweep / 2)
    offset  = _ARC_RADIUS + 38
    tx = int(pt_v[0] + offset * np.cos(mid_rad))
    ty = int(pt_v[1] + offset * np.sin(mid_rad))

    label = f"{value:.0f}"
    (tw, th), baseline = cv2.getTextSize(label, _FONT, _FONT_SCALE, _FONT_THICKNESS)
    tx = max(2, min(frame.shape[1] - tw - 4, tx))
    ty = max(th + 4, min(frame.shape[0] - 4, ty))

    # Semi-transparent dark background for readability
    pad = 3
    x1 = max(0, tx - pad)
    y1 = max(0, ty - th - pad)
    x2 = min(frame.shape[1], tx + tw + pad)
    y2 = min(frame.shape[0], ty + baseline + pad)
    frame[y1:y2, x1:x2] = (frame[y1:y2, x1:x2] * 0.4).astype(np.uint8)

    cv2.putText(
        frame, label,
        (tx, ty), _FONT, _FONT_SCALE, color, _FONT_THICKNESS, cv2.LINE_AA,
    )


# ── Main class ────────────────────────────────────────────────────────────────

class SkeletonRenderer:
    """Renders MediaPipe pose landmarks onto a video and re-encodes to H.264.

    Visuals:
    - Joints: always purple.
    - Bones: per-frame dynamic green/orange/red for the two bones adjacent to
             each active arc vertex.  All other bones are grey.
    - Arcs:  drawn only when the joint angle is in the 'active' range (i.e. the
             person is actually performing the movement, not standing at rest).
    - Labels: angle value with semi-transparent background, clear of the arc.
    Face (lm 0-10), hand fingers (17-22) and foot details (29-32) are skipped.
    For side-view exercises only the near side is drawn.
    """

    def render(
        self,
        video_path: str,
        landmarks_seq: list[Optional[list[Landmark]]],
        output_path: str,
        exercise_id: str = "",
        features_seq: list[Optional[FrameFeatures]] | None = None,
    ) -> None:
        vizs = EXERCISE_ANGLE_VIZ.get(exercise_id, [])
        camera_view = EXERCISES.get(exercise_id, {}).get("camera_view", "side")
        side_view   = (camera_view == "side")

        tmp_path = output_path + ".tmp.mp4"
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(
            tmp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h),
        )

        try:
            for i, landmarks in enumerate(landmarks_seq):
                ret, frame = cap.read()
                if not ret:
                    break
                # Skip frame 0: MediaPipe runs full detection (no prior) on the
                # first frame, which is less accurate than tracking on frame 1+.
                # Leaving frame 0 without overlay avoids a misaligned thumbnail.
                if landmarks is not None and i > 0:
                    features = (
                        features_seq[i]
                        if features_seq is not None and i < len(features_seq)
                        else None
                    )
                    self._draw(frame, landmarks, features, vizs, side_view, w, h)
                out.write(frame)
        finally:
            cap.release()
            out.release()

        subprocess.run(
            ["ffmpeg", "-i", tmp_path, "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y", output_path],
            check=True, capture_output=True,
        )
        os.unlink(tmp_path)

    def _draw(
        self,
        frame,
        landmarks: list[Landmark],
        features: Optional[FrameFeatures],
        vizs: list[AngleViz],
        side_view: bool,
        w: int,
        h: int,
    ) -> None:
        # For side-view exercises, only render the side closer to the camera
        active_vizs = _filter_near_side(landmarks, vizs) if side_view else vizs

        bone_colors = (
            _build_frame_bone_colors(features, active_vizs)
            if features and active_vizs else {}
        )

        # ── Bones ────────────────────────────────────────────────────────────
        for a, b in _DRAW_CONNECTIONS:
            lm_a, lm_b = landmarks[a], landmarks[b]
            if (lm_a.visibility > _VISIBILITY_THRESHOLD
                    and lm_b.visibility > _VISIBILITY_THRESHOLD):
                pt_a  = (int(lm_a.x * w), int(lm_a.y * h))
                pt_b  = (int(lm_b.x * w), int(lm_b.y * h))
                color = bone_colors.get(frozenset({a, b}), _DEFAULT_COLOR)
                cv2.line(frame, pt_a, pt_b, color, _LINE_THICKNESS, cv2.LINE_AA)

        # ── Angle arcs + labels ───────────────────────────────────────────────
        if features and active_vizs:
            for av in active_vizs:
                val = av.get_value(features)
                if val is None or not _is_active(av, val):
                    continue
                color = _angle_color(val, av.good, av.warn, av.lower_is_better)
                pv = _lm_pt(landmarks, av.vertex, w, h)
                pa = _lm_pt(landmarks, av.arm_a,  w, h)
                pb = _lm_pt(landmarks, av.arm_b,  w, h)
                if pv and pa and pb:
                    _draw_angle_arc(frame, pv, pa, pb, val, color)

        # ── Joints (always purple, drawn last so they sit on top) ─────────────
        # Skip the same landmarks as for connections — no orphan dot clusters
        # on face, hand fingers, or foot details.
        for idx, lm in enumerate(landmarks):
            if idx in _SKIP_LM:
                continue
            if lm.visibility > _VISIBILITY_THRESHOLD:
                pt = (int(lm.x * w), int(lm.y * h))
                cv2.circle(frame, pt, _DOT_RADIUS, _DOT_COLOR, -1, cv2.LINE_AA)
