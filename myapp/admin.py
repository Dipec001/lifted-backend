from django.contrib import admin
from .models import CustomUser, Comment, Like, Feed, Exercise, WorkoutType, UserWorkout, Set, SelectedExercise, UserFollowing
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Comment)
admin.site.register(Feed)
admin.site.register(Like)
admin.site.register(Exercise)
admin.site.register(WorkoutType)
admin.site.register(UserWorkout)
admin.site.register(SelectedExercise)
admin.site.register(Set)
admin.site.register(UserFollowing)