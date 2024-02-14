# serializers.py
from rest_framework import serializers
from .models import CustomUser, Feed, Like, Comment, Exercise, WorkoutType, UserWorkout, SelectedExercise, UserFollowing
from rest_framework.exceptions import ValidationError

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['height', 'weight', 'date_of_birth', 'arm_choice', 'bio','profile_picture', 'first_name','last_name']


class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser  # Use your custom user model
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'created_at', 'user']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at']

    def save(self, **kwargs):
        # Set the user field to the currently authenticated user
        self.validated_data['user'] = self.context['request'].user
        return super().save(**kwargs)

class FeedSerializer(serializers.ModelSerializer):
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Feed
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at', 'likes_count', 'likes', 'comments_count', 'comments',]
        read_only_fields = ['user', 'created_at', 'updated_at', 'likes_count', 'comments_count']


# class SetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Set
#         fields = ['id', 'reps', 'weight']
class WorkoutTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkoutType
        fields = ['id', 'name']

class ExerciseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)  # Make the name field optional
    # workout_type = WorkoutTypeSerializer()
    workout_type = serializers.PrimaryKeyRelatedField(queryset=WorkoutType.objects.all(), source='workout_type.id')


    class Meta:
        model = Exercise
        fields = ['id', 'name','workout_type']

class SelectedExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedExercise
        fields = '__all__'  # You can specify specific fields if needed


class UserWorkoutSerializer(serializers.ModelSerializer):

    selected_exercises = SelectedExerciseSerializer(many=True)  # Include exercise serializer for each user workout
    class Meta:
        model = UserWorkout
        fields = ['id', 'user', 'title', 'selected_exercises']


class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ("id", "following_user_id", "created")
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ("id", "user_id", "created")