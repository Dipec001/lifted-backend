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
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

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