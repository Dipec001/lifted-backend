# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from .choices import ARM_CHOICES
from uuid import uuid4
from datetime import timezone

class CustomUser(AbstractUser):
    height = models.CharField(max_length=10, blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.CharField(max_length=15)
    arm_choice = models.CharField(max_length=50, choices=ARM_CHOICES)

    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)



class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # New field to track the number of likes and comments
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like on {self.feed}"

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.feed}"
    


class WorkoutType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.workout_type.name})"

class UserWorkout(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='Workout🔥')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SelectedExercise(models.Model):
    user_workout = models.ForeignKey('UserWorkout', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_workout} - {self.exercise}"
    


class Set(models.Model):
    reps = models.PositiveIntegerField(default=12)
    weight = models.PositiveIntegerField(default=12)
    selected_exercise = models.ForeignKey(SelectedExercise, on_delete=models.CASCADE)

    def __str__(self):
        return f"Set for {self.selected_exercise}"