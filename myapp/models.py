# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from .choices import ARM_CHOICES
from uuid import uuid4
from datetime import timezone

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    height = models.CharField(max_length=10, blank=True, null=True)
    height_measurement = models.CharField(max_length=5, blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    weight_measurement = models.CharField(max_length=5, blank=True, null=True)
    date_of_birth = models.CharField(max_length=15, blank=True, null=True)
    arm_choice = models.CharField(max_length=50, choices=ARM_CHOICES, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    full_name = models.CharField(max_length=100, blank=True, null=True)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def followers_count(self):
        return self.followers.count()
    
    def get_feeds_count(self):
        return self.feed_set.count()
    
    def get_interactions_count(self):
        # Get all feeds associated with the user
        user_feeds = self.feed_set.all()
        
        # Sum the likes_count and comments_count from each feed
        likes_count = sum(feed.likes_count for feed in user_feeds)
        comments_count = sum(feed.comments_count for feed in user_feeds)
        
        # Return the total interactions count
        return likes_count + comments_count
    
    def __str__(self):
        return self.email  # Or any other field you want to represent the user


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
    

class UserFollowing(models.Model):
    user_id =models.ForeignKey(CustomUser, on_delete=models.CASCADE ,related_name="following")
    following_user_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name="followers")
    # To add info about when user started following
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id','following_user_id'],  name="unique_followers")
        ]

        ordering = ["-created"]

    def __str__(self):
        return f"{self.user_id} follows {self.following_user_id}"
    

# class WorkoutGroup(models.Model):
#     workout_id = models.UUIDField(default=uuid4, editable=False, unique=True)

# class WorkoutSession(models.Model):
#     session_id = models.UUIDField(default=uuid4, editable=False, unique=True)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField(null=True, blank=True)
#     total_hr_points = models.IntegerField(default=0)
#     avg_heart_rate_per_min = models.FloatField(null=True, blank=True)  # Average heart rate per minute for the entire session

# class Zone(models.Model):
#     workout_session = models.ForeignKey(WorkoutSession, related_name='zones', on_delete=models.CASCADE)
#     zone_number = models.PositiveIntegerField()
#     duration = models.DurationField()
#     hr_points = models.IntegerField()

#     class Meta:
#         unique_together = ('workout_session', 'zone_number')

# class WorkoutSet(models.Model):
#     """A set of workouts done."""
#     reps = models.PositiveIntegerField()
#     weight = models.PositiveIntegerField()
#     avg_heart_rate = models.FloatField(null=True, blank=True)
#     workout_session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets')




# class CustomWorkout(models.Model):
#     """Represents a template for a custom workout."""
#     workout_id = models.UUIDField(default=uuid4, editable=False, unique=True)
#     # Add other fields specific to the custom workout

# class CustomWorkoutSession(models.Model):
#     """Represents a recorded session of a custom workout."""
#     session_id = models.UUIDField(default=uuid4, editable=False, unique=True)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField(null=True, blank=True)
#     timer_result = models.IntegerField()  # Timer result in seconds
#     avg_heart_rate_per_min = models.FloatField(null=True, blank=True)
#     total_hr_points = models.IntegerField(default=0)
#     custom_workout = models.ForeignKey(CustomWorkout, on_delete=models.CASCADE)

# class CustomZone(models.Model):
#     """Represents a specific zone within a custom workout session."""
#     workout_session = models.ForeignKey(CustomWorkoutSession, related_name='zones', on_delete=models.CASCADE)
#     zone_number = models.PositiveIntegerField()
#     duration = models.DurationField()
#     hr_points = models.IntegerField()

#     class Meta:
#         unique_together = ('workout_session', 'zone_number')  # Ensure uniqueness of zones within a session