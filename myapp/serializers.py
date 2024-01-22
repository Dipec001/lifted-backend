# serializers.py
from rest_framework import serializers
from .models import CustomUser, Feed, Like, Comment

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['height', 'weight', 'date_of_birth', 'arm_choice']


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
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at', 'likes_count']
        read_only_fields = ['user', 'created_at', 'updated_at', 'likes_count']
