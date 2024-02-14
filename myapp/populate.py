# populate.py

from .models import WorkoutType, Exercise
from .choices import WORKOUT_TYPES, EXERCISES

def create_workout_types_and_exercises():
    for workout_type_code, workout_type_name in WORKOUT_TYPES:
        workout_type, created = WorkoutType.objects.get_or_create(name=workout_type_name)

        # Get the list of exercises for the current workout type
        exercises_data = EXERCISES.get(workout_type_name, [])

        # Create exercises for the current workout type
        create_exercises(workout_type, exercises_data)

def create_exercises(parent, exercises_data):
    for exercise_code, exercise_name in exercises_data:
        if isinstance(exercise_name, tuple):  # Check if it's a nested category
            category_name, category_exercises = exercise_name
            category_obj, _ = Exercise.objects.get_or_create(name=category_name, workout_type=parent)
            create_exercises(category_obj, category_exercises)
        else:
            Exercise.objects.get_or_create(name=exercise_name, workout_type=parent)

# Call the function to populate data
create_workout_types_and_exercises()
