MUSCLE_GROUPS = {
    "chest": {
        "name": "Chest",
        "exercises": ["bench_press", "incline_bench_press", "push_up"],
    },
    "shoulders": {
        "name": "Shoulders",
        "exercises": ["overhead_press", "lateral_raise", "arnold_press"],
    },
    "legs": {
        "name": "Legs",
        "exercises": ["squat", "lunge", "bulgarian_split_squat", "romanian_deadlift"],
    },
    "back": {
        "name": "Back",
        "exercises": ["pull_up", "barbell_row", "deadlift"],
    },
}

EXERCISES = {
    "bench_press": {
        "name": "Bench Press",
        "muscle_group": "chest",
        "camera_view": "side",
        "aspects": ["Bar path", "Elbow angle", "Arch position", "Grip width"],
    },
    "incline_bench_press": {
        "name": "Incline Bench Press",
        "muscle_group": "chest",
        "camera_view": "side",
        "aspects": ["Bar path", "Elbow angle", "Bench angle", "Grip width"],
    },
    "push_up": {
        "name": "Push-up",
        "muscle_group": "chest",
        "camera_view": "side",
        "aspects": ["Body alignment", "Elbow angle", "Depth", "Hand placement"],
    },
    "overhead_press": {
        "name": "Overhead Press",
        "muscle_group": "shoulders",
        "camera_view": "any",
        "aspects": ["Bar path", "Back lean", "Lockout", "Elbow position"],
    },
    "lateral_raise": {
        "name": "Lateral Raise",
        "muscle_group": "shoulders",
        "camera_view": "any",
        "aspects": ["Arm angle", "Shoulder height", "Body swing", "Elbow bend"],
    },
    "arnold_press": {
        "name": "Arnold Press",
        "muscle_group": "shoulders",
        "camera_view": "front",
        "aspects": ["Rotation path", "Elbow position", "Lockout", "Posture"],
    },
    "squat": {
        "name": "Squat",
        "muscle_group": "legs",
        "camera_view": "side",
        "aspects": ["Knee alignment", "Depth", "Back angle", "Hip hinge"],
    },
    "lunge": {
        "name": "Lunge",
        "muscle_group": "legs",
        "camera_view": "side",
        "aspects": ["Front knee depth", "Torso position", "Back knee", "Stride"],
    },
    "bulgarian_split_squat": {
        "name": "Bulgarian Split Squat",
        "muscle_group": "legs",
        "camera_view": "side",
        "aspects": ["Knee tracking", "Torso position", "Depth", "Balance"],
    },
    "romanian_deadlift": {
        "name": "Romanian Deadlift",
        "muscle_group": "legs",
        "camera_view": "side",
        "aspects": ["Hip hinge", "Back position", "Knee bend", "Bar path"],
    },
    "pull_up": {
        "name": "Pull-up",
        "muscle_group": "back",
        "camera_view": "any",
        "aspects": ["Full extension", "Chin over bar", "Body swing", "Grip"],
    },
    "barbell_row": {
        "name": "Barbell Row",
        "muscle_group": "back",
        "camera_view": "side",
        "aspects": ["Back angle", "Elbow path", "Hip hinge", "Bar path"],
    },
    "deadlift": {
        "name": "Deadlift",
        "muscle_group": "back",
        "camera_view": "side",
        "aspects": ["Back position", "Hip hinge", "Bar path", "Lockout"],
    },
}
