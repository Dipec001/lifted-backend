# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from .choices import ARM_CHOICES
from uuid import uuid4

class CustomUser(AbstractUser):
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    arm_choice = models.CharField(max_length=50, choices=ARM_CHOICES, blank=True)

class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # New field to track the number of likes
    likes_count = models.PositiveIntegerField(default=0)

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
    




# Create a model for the workout that includes:
# A title (Charfield)
# The type of exercise (dropdown menu with multiple choices - Choice Field)
# The duration of the workout in minutes (Integer field)
