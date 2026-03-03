# Single source of truth for exercise angle thresholds.
# Both classifiers and skeleton_renderer import from here — never hardcode these values elsewhere.

# ── Squat ─────────────────────────────────────────────────────────────────────
SQUAT_KNEE_GOOD = 90.0    # hip-knee-ankle; ≤ = parallel or below
SQUAT_KNEE_WARN = 110.0
SQUAT_BACK_GOOD = 50.0    # spine vs vertical; ≤ = acceptable lean
SQUAT_BACK_WARN = 65.0

# ── Lunge ─────────────────────────────────────────────────────────────────────
LUNGE_KNEE_GOOD = 90.0
LUNGE_KNEE_WARN = 110.0
LUNGE_BACK_GOOD = 50.0
LUNGE_BACK_WARN = 65.0

# ── Push-up ───────────────────────────────────────────────────────────────────
PUSHUP_ELBOW_GOOD     = 100.0
PUSHUP_ELBOW_WARN     = 115.0
PUSHUP_ALIGNMENT_GOOD = 15.0    # max deviation from straight (|180° - hip_angle|)
PUSHUP_ALIGNMENT_WARN = 30.0
# Derived for renderer (hip_angle = 180° - deviation):
PUSHUP_HIP_GOOD = 180.0 - PUSHUP_ALIGNMENT_GOOD   # = 165°
PUSHUP_HIP_WARN = 180.0 - PUSHUP_ALIGNMENT_WARN    # = 150°

# ── Bench Press ───────────────────────────────────────────────────────────────
BENCH_ELBOW_GOOD   = 100.0
BENCH_ELBOW_WARN   = 125.0
BENCH_LOCKOUT_GOOD = 155.0
BENCH_LOCKOUT_WARN = 135.0

# ── Incline Bench Press ───────────────────────────────────────────────────────
INCLINE_ELBOW_GOOD   = 100.0
INCLINE_ELBOW_WARN   = 125.0
INCLINE_LOCKOUT_GOOD = 155.0
INCLINE_LOCKOUT_WARN = 135.0

# ── Overhead Press ────────────────────────────────────────────────────────────
OHP_LOCKOUT_GOOD = 160.0
OHP_LOCKOUT_WARN = 145.0

# ── Lateral Raise ─────────────────────────────────────────────────────────────
LATERAL_HEIGHT_GOOD = 80.0
LATERAL_HEIGHT_WARN = 60.0
LATERAL_ELBOW_GOOD  = 155.0   # soft-bend threshold (renderer-side "good" reference)
LATERAL_ELBOW_WARN  = 135.0   # below = arms too bent (turning into a curl)

# ── Upright Row ───────────────────────────────────────────────────────────────
UPRIGHT_ROW_SHOULDER_GOOD = 70.0
UPRIGHT_ROW_SHOULDER_WARN = 40.0
UPRIGHT_ROW_ELBOW_GOOD    = 100.0
UPRIGHT_ROW_ELBOW_WARN    = 130.0

# ── Romanian Deadlift ─────────────────────────────────────────────────────────
RDL_BACK_GOOD          = 45.0
RDL_BACK_WARN          = 30.0
RDL_KNEE_STRAIGHT_WARN = 168.0   # above = knees locked
RDL_KNEE_GOOD          = 160.0   # renderer reference: below = proper soft bend
RDL_KNEE_BENT_WARN     = 130.0   # below = squat pattern

# ── Deadlift ──────────────────────────────────────────────────────────────────
DEADLIFT_STIFF_LEG_WARN  = 145.0   # knee above this during hinge = stiff-leg
DEADLIFT_KNEE_GOOD       = 120.0   # renderer reference: below = proper setup bend
DEADLIFT_LOCKOUT_GOOD    = 10.0    # back_angle ≤ = hips fully extended
DEADLIFT_LOCKOUT_WARN    = 20.0

# ── Barbell Row ───────────────────────────────────────────────────────────────
BARBELL_ROW_BACK_GOOD = 55.0
BARBELL_ROW_BACK_WARN = 30.0
BARBELL_ROW_ROM_GOOD  = 100.0
BARBELL_ROW_ROM_WARN  = 130.0

# ── Pull-up ───────────────────────────────────────────────────────────────────
PULLUP_DEPTH_GOOD     = 90.0
PULLUP_DEPTH_WARN     = 120.0
PULLUP_EXTENSION_GOOD = 160.0
PULLUP_EXTENSION_WARN = 140.0
