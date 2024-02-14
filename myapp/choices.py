# choices.py

ARM_CHOICES = [
    ('left_snug', 'Left Arm (watch is snug to my wrist)'),
    ('right_snug', 'Right Arm (watch is snug to my wrist)'),
    ('left_strap', 'Left Arm (but I wear wrist straps)'),
    ('right_strap', 'Right Arm (but I wear wrist straps)'),
]

# Define workout types
WORKOUT_TYPES = [
    ('Chest', 'Chest'),
    ('Shoulders', 'Shoulders'),
    ('Back', 'Back'),
    ('Legs', 'Legs'),
    ('Biceps', 'Biceps'),
    ('Triceps', 'Triceps'),
    ('Abs', 'Abs'),
    ('Other', 'Other'),
]

# Define exercises for each workout type
EXERCISES = {
    'Chest': [
        ('Barbell Chest Press', 'Barbell Chest Press'),
        ('Dumbbell Chest Press', 'Dumbbell Chest Press'),
        ('Barbell Incline Chest Press', 'Barbell Incline Chest Press'),
        ('Dumbbell Incline Chest Press', 'Dumbbell Incline Chest Press'),
        ('Dumbbell Chest Fly', 'Dumbbell Chest Fly'),
    ],
    'Shoulders': [
        ('Barbell Shoulder Press', 'Barbell Shoulder Press'),
        ('Dumbbell Shoulder Press', 'Dumbbell Shoulder Press'),
        ('Dumbbell Front Raise', 'Dumbbell Front Raise'),
        ('Dumbbell Lateral Raise', 'Dumbbell Lateral Raise'),
        ('Barbell Upright Row', 'Barbell Upright Row'),
        ('Dumbbell Upright Row', 'Dumbbell Upright Row'),
    ],
    'Back': [
        ('Pull-up', 'Pull-up'),
        ('Barbell Bent Over Row', 'Barbell Bent Over Row'),
        ('Dumbbell Bent Over Row', 'Dumbbell Bent Over Row'),
        ('T-Bar Row', 'T-Bar Row'),
        ('Dumbbell Single Arm Row', 'Dumbbell Single Arm Row'),
    ],
    'Legs': {
        ('Barbell Sumo Squat', 'Barbell Sumo Squat'),
        ('Dumbbell Sumo Squat', 'Dumbbell Sumo Squat'),
        ('Barbell Hip Thrust', 'Barbell Hip Thrust'),
        ('Barbell Front Squat', 'Barbell Front Squat'),
        ('Dumbbell Front Squat', 'Dumbbell Front Squat'),
        ('Barbell Back Squat', 'Barbell Back Squat'),
        ('Dumbbell Back Squat', 'Dumbbell Back Squat'),
        ('Dumbbell Lunge', 'Dumbbell Lunge'),
        ('Barbell Lunge', 'Barbell Lunge'),
        ('Standing Calf Raise', 'Standing Calf Raise'),
        ('Seated Calf Raise', 'Seated Calf Raise'),
        ('Box Jump', 'Box Jump'),
        ('Barbell Deadlift', 'Barbell Deadlift'),
        ('Dumbbell Deadlift', 'Dumbbell Deadlift'),
        ('Barbell Romanian Deadlift', 'Barbell Romanian Deadlift'),
        ('Dumbbell Romanian Deadlift', 'Dumbbell Romanian Deadlift'),
    },
    'Biceps': [
        ('Dumbbell Hammer Curl', 'Dumbbell Hammer Curl'),
        ('Barbell Curl', 'Barbell Curl'),
        ('Concentration Curl', 'Concentration Curl'),
        ('Chin-up', 'Chin-up'),
        ('EZ-Bar Curl', 'EZ-Bar Curl'),
    ],
    'Triceps': [
        ('Tricep Dip', 'Tricep Dip'),
        ('Tricep Extension', 'Tricep Extension'),
        ('Skull Crusher', 'Skull Crusher'),
    ],
    'Abs': [
        ('Crunch', 'Crunch'),
        ('Plank', 'Plank'),
    ],
}

