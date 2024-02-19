# serializers.py
from rest_framework import serializers
from .models import (CustomUser, Feed, Like, Comment, Exercise, WorkoutType, UserWorkout, SelectedExercise, UserFollowing,
                      )
# WorkoutGroup, WorkoutSession, Zone, WorkoutSet, CustomWorkout, CustomWorkoutSession, CustomZone
from rest_framework.exceptions import ValidationError

class CustomUserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.SerializerMethodField()
    interactions_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','full_name','height', 'height_measurement', 'weight', 'weight_measurement', 'date_of_birth', 'arm_choice', 'bio', 'profile_photo', 'followers_count', 'posts_count','interactions_count', 'email','username']


    def get_posts_count(self, obj):
        return obj.get_feeds_count()

    def get_interactions_count(self, obj):
        return obj.get_interactions_count()
    

class OnboardSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.SerializerMethodField()
    interactions_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','full_name','height', 'height_measurement', 'weight', 'height_measurement', 'date_of_birth', 'arm_choice', 'bio', 'profile_photo', 'followers_count', 'posts_count','interactions_count','username']
        read_only_fields = ['email']  # Make the email field read-only


    def get_posts_count(self, obj):
        return obj.get_feeds_count()

    def get_interactions_count(self, obj):
        return obj.get_interactions_count()

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


# class ZoneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Zone
#         fields = ['zone_number', 'duration', 'hr_points']

# class WorkoutGroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkoutGroup
#         fields = '__all__'

# class CustomWorkoutSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomWorkout
#         fields = '__all__'

# class WorkoutSetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkoutSet
#         fields = ['reps', 'weight', 'avg_heart_rate']

# class WorkoutSessionSerializer(serializers.ModelSerializer):
#     zones = ZoneSerializer(many=True)
#     sets = WorkoutSetSerializer(many=True)

#     class Meta:
#         model = WorkoutSession
#         fields = ['session_id', 'start_time', 'end_time', 'total_hr_points', 'avg_heart_rate_per_min', 'zones', 'sets']

#     def create(self, validated_data):
#         zones_data = validated_data.pop('zones')
#         sets_data = validated_data.pop('sets')
#         workout_session = WorkoutSession.objects.create(**validated_data)
        
#         for zone_data in zones_data:
#             Zone.objects.create(workout_session=workout_session, **zone_data)
        
#         for set_data in sets_data:
#             WorkoutSet.objects.create(workout_session=workout_session, **set_data)
        
#         return workout_session

# class CustomZoneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomZone
#         fields = ['zone_number', 'duration', 'hr_points']

# class CustomWorkoutSessionSerializer(serializers.ModelSerializer):
#     custom_zones = CustomZoneSerializer(many=True)

#     class Meta:
#         model = CustomWorkoutSession
#         fields = ['session_id', 'start_time', 'end_time', 'timer_result', 'avg_heart_rate_per_min', 'total_hr_points', 'custom_zones']

#     def create(self, validated_data):
#         custom_zones_data = validated_data.pop('custom_zones')
#         custom_workout_session = CustomWorkoutSession.objects.create(**validated_data)
        
#         for zone_data in custom_zones_data:
#             CustomZone.objects.create(workout_session=custom_workout_session, **zone_data)
        
#         return custom_workout_session